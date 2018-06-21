from app import app  # 导入APP文件夹
import threading

HOST="127.0.0.1"
PORT=6000
WEBPORT=4000





def statisticsData():
    print('ddd')

def http():
    app.run(host=HOST, port=WEBPORT, debug=True,threaded=True)


if __name__ == '__main__':
    # threading.Thread(target=statisticsData).start()
    http()
