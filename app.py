from flask import *
import json
import subprocess
import os

app=Flask(__name__)
shard_data = ""     #共有データ

class AppException(Exception):
    pass

def exec(data:str):
    """
    POSTデータをjsonに変換
    コマンドを実行
    """
    try:
        data_json = json.loads(data)
    except json.JSONDecodeError as e:
        raise AppException(f"jsonへ変換時エラー：{e}")
    
    if not "prog" in data_json:
        raise AppException(f"progがありません")

    if not "args" in data_json:
        raise AppException(f"argsがありません")

    args = data_json["args"]
    command = None
    if type(args) == list:    
        args.insert(0,data_json["prog"])
        command = args
    else:
        command = f"{data_json["prog"]} {args}" 

    try:
        #stdin=subprocess.DEVNULLをつけないとIISから実行したときにエラー
        res = subprocess.run(command, capture_output=True,text=True,stdin=subprocess.DEVNULL)
    except Exception as e:
        raise AppException(f"コマンド実行時にエラー：{e}")
    return res

@app.route("/") 
def hello():
    return "execcommand-server"

@app.route("/exec",methods=["POST"]) 
def exec_handler():
    """
    リクエスト：
        json{"prog":起動するプログラム,"args":[引数,]}
    レスポンス：
        エラー時：json{"error":エラーメッセージ}
        OK時：json{"stdout"：標準出力}
    """
    data = request.data.decode('utf-8')
    try:
        res = exec(data)
    except AppException as e:
        data_ret = {"error":str(e)}
        return jsonify(data_ret)

    data_ret= {"stdout":res.stdout}
    return jsonify(data_ret)

@app.route("/setdata",methods=["POST"]) 
def setdata_handler():
    #POSTデータを共有データに設定
    global shard_data
    shard_data = request.data.decode('utf-8')
    return "shared_dataを設定しました"

@app.route("/getdata") 
def getdata_handler():
    #共有データを文字列で返す
    return shard_data

if __name__=="__main__":
    #IISから起動する場合、環境変数HTTP_PLATFORM_PORTでポートが指定される。そのポートを使用する
    if "HTTP_PLATFORM_PORT" in os.environ:
        port = os.environ["HTTP_PLATFORM_PORT"]
    else:
        port=5000
    app.debug=True
    app.run(port=port)
