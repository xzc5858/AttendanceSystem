from app import app  # 导入APP文件夹
import threading
import calendar
import time
import datetime
HOST="127.0.0.1"
PORT=6000
WEBPORT=4000





def statisticsData():
    firstDayWeekDay, monthRange=calendar.monthrange(2018, 10)
    lastDay = datetime.date(year=datetime.date.today().year, month=datetime.date.today().month, day=monthRange)
    print(lastDay)



def http():
    app.run(host=HOST, port=WEBPORT, debug=True,threaded=True)


if __name__ == '__main__':
    threading.Thread(target=statisticsData).start()
    http()
