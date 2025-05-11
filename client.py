import requests
import argparse

URL = "http://127.0.0.1:5000/"
                
def exec():
    data = {
        "prog": "ping.exe",
        #"args": ["localhost","-n","1"]
        "args": "localhost -n 1"
    }
    try:
        res = requests.post(
                URL + "exec",
                json = data,
            )
    except Exception as e:
        print(f"post時エラー{e}")
        return

    try:
        data = res.json()
        print(data)
    except:
        data = res.text
        print(data)

def setdata():
    data = "テスト共有データ"
    try:
        res = requests.post(
                URL + "setdata",
                data = data,
            )
    except Exception as e:
        print(f"post時エラー{e}")
        return

def getdata():
    try:
        res = requests.get(
                URL + "getdata",
            )
    except Exception as e:
        print(f"get時エラー{e}")
        return
    
    print(res.text)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("type",choices=["exec","setdata","getdata"])
    args=parser.parse_args()
    
    if args.type == "exec":
        exec()
    if args.type == "setdata":
        setdata()
    if args.type == "getdata":
        getdata()