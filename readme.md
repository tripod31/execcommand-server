# ExecCommand-server
## スクリプト
### app.py
HTTPサーバー
+ 指定されたプログラムを起動し、標準出力を返す
+ 共有データを取得／設定する。

### client.py
テスト用クライアント
```
usage: client.py [-h] {exec,setdata,getdata}
client.py: error: the following arguments are required: type
```

### service.py
app.pyをWindowsサービスとして登録する

## 動作確認環境
+ windows11/64bit
+ IIS10.0
+ python3.13.3
+ Flask3.1.0

mod_wsgiで動かす場合に関連して
+ apache2.4.62
+ visual studio2022 community edition

## app.pyのHTTPハンドラ
### POST /exec
プログラムを起動し、その標準出力を返す  
```
・リクエスト
json{"prog":起動するプログラム,"args":配列[引数文字列] or 引数文字列}

・レスポンス
エラー時：json{"error":エラーメッセージ}
OK時：json{"stdout"：標準出力}
```
### POST /setdata
POSTデータを共有データに設定

### GET /getdata
共有データを返す

## sever.pyをWindowsサービスとして登録する場合
管理者で
```
python service.py install
```

## app.pyをIIS上で動作させる場合

### 設定
1. IISの拡張機能のhttpPlatformHandlerをダウンロード＋インストールする。
2. IISマネージャ設定。サイトを追加する。
3. スクリプトがあるフォルダとpythonのインストールフォルダにIISの実行ユーザーのパーミッションを与えておく。

2,3はdoc/IIS.pdf参照

### ブラウザから確認
http://localhost:5000/  
"execcommand-server"と表示される

### web.configの説明
IIS用設定ファイル。httpPlatformHandlerを使用。IISがapp.pyを起動する。待ち受けポートはIISから環境変数で渡される。そのポートで待つ。IISがHTTPリスエストをapp.pyに渡す。

#### processesPerApplication
```
processesPerApplication="1"
```
app.pyで、グローバル変数に共有データを保存している。プロセスが別になると共有データが別になってしまう。このため、IISから起動されるプロセスの数を１つにしている。

#### environmentVariable
```
<environmentVariable name="ENV_SAMPLE" value="sample_value" />
```
app.pyに渡される環境変数を設定するサンプル。

## mod_wsgiで動かす場合

### mod_wsgiインストール
```
export MOD_WSGI_APACHE_ROOTDIR="D:\laragon\bin\apache\httpd-2.4.62-240904-win64-VS17"
pip install mod_wsgi
```
環境変数MOD_WSGI_APACHE_ROOTDIRでapache2のインストールフォルダを指定する。git bash上で実行したのでexportしている  
visualstudioでビルドされる  
visualstudioでインストールしたコンポーネントはdoc/visualstudio.pdf参照。「C++によるデスクトップ開発」をインストールした。  

### execcommand.wsgi
```
import sys

#app.pyからappオブジェクトをインポートする
sys.path.insert(0, r"D:/devel_open/eclipse/execcommand-server")
from app import app as application
```

### httpd.conf
mod_wsgiをインストールするとできるmod_wsgi-express.exeを実行する。
```
mod_wsgi-express module-config
```
出力された以下の内容を追加する
```
LoadFile "C:/Users/yoshi/AppData/Local/Programs/Python/Python313/python313.dll"
LoadModule wsgi_module "C:/Users/yoshi/AppData/Local/Programs/Python/Python313/Lib/site-packages/mod_wsgi/server/mod_wsgi.cp313-win_amd64.pyd"
WSGIPythonHome "C:/Users/yoshi/AppData/Local/Programs/Python/Python313"
```

### 000-default.conf
#### 設定パターン1
```
<VirtualHost _default_:80>
    <Directory "D:/laragon/www">
        AllowOverride All
        Require all granted
    </Directory>

    #以下の行を追加  
    #/でクライアントからアクセスする時のURLのパスを指定している
    WSGIScriptAlias / "D:/devel_open/eclipse/execcommand-server/server.wsgi"

    <Directory "D:\devel_open\eclipse\execcommand-server">
        Require all granted
    </Directory>
</VirtualHost>
```
この場合  
```
http://localhost/
```
でアクセスできる。wsgiファイルを指定できるのは１つだけ  

#### 設定パターン2
```
<VirtualHost _default_:80>
    <Directory "D:/laragon/www">
        AllowOverride All
        Require all granted

        #以下の行を追加
		AddHandler wsgi-script .wsgi
		Options +ExecCGI
    </Directory>
</VirtualHost>
```
として、D:/laragon/www下にserver.wsgiを置く。この場合  
http://localhost/server.wsgi  
でアクセスできる。複数の.wsgiファイルを置くことができる。  

#### 設定パターン3
```
<VirtualHost _default_:80>
    <Directory "D:/laragon/www">
        AllowOverride All
        Require all granted
    </Directory>

    #以下の行を追加
	WSGIScriptAlias /cgi/ "D:/laragon/www/wsgi/"	
</VirtualHost>
```
として、D:/laragon/www/wsgi下にexeccommand.wsgiを置く。この場合  
http://localhost/wsgi/server.wsgi  
でアクセスできる。複数の.wsgiファイルを置くことができる。  