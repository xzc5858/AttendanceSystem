from app import app  # 导入APP文件夹
import threading
<<<<<<< HEAD
import os,signal
import subprocess
import datetime
import calendar

HOST = ""
PORT = 6000
WEBPORT = 4000
AutoStData = False
AutoLoadData = False
PS = None
=======
import calendar
import time
import datetime
HOST="127.0.0.1"
PORT=6000
WEBPORT=4000
>>>>>>> 59ea19bb39b5f508c1f37a233b9e0e6e78e1fcaf


def statisticsData():
    # print('3')
    tday = datetime.datetime.today().date()
    tnow = datetime.datetime.today()
    firstDayWeekDay, monthRange = calendar.monthrange(tday.year, tday.month)
    firstTime = datetime.datetime(year=tday.year, month=tday.month, day=1, hour=18, minute=0, second=0)
    lastTime = datetime.datetime(year=datetime.date.today().year, month=datetime.date.today().month, day=monthRange,
                                 hour=18, minute=0, second=0)
    # print(datetime.date(firstDay.year,firstDay.month,firstDay.day))
    # print(lastDay)
    # print(datetime.timedelta(days=3))
    global AutoStData
    global AutoLoadData
    global PS
    # if (lastTime == datetime.datetime(year=2018, month=10, day=31, hour=14, minute=tnow.minute, second=0)):
    if(lastTime<=tnow):
        print(10)
        if (AutoLoadData == False):
            AutoLoadData = True
            PS = subprocess.Popen('E:\\CodeProject\\养老保险金系统\\PensionInsurance\\WinAtt\\bin\\Debug\\WinAtt.exe')
            # print(PS.pid)

    elif (tday == datetime.date(firstTime.year, firstTime.month, firstTime.day) and tnow >= firstTime):
        if (PS != None):
            os.kill(PS.pid, signal.SIGINT)
            PS = None
        AutoLoadData = False
        if (AutoStData == False):
            AutoStData = True
            from app.statisticalData import start_tongji
            first = datetime.date(datetime.date.today().year, datetime.date.today().month - 1, 1)
            last = datetime.date(datetime.date.today().year, datetime.date.today().month, 1) - datetime.timedelta(1)
            start_tongji(first.strftime("%Y-%m-%d"), last.strftime("%Y-%m-%d"))
            # print('AutoStData')

    else:
        print(12)
        AutoStData = False
        AutoLoadData = False

    global timer
    timer = threading.Timer(5, statisticsData)
    timer.start()


<<<<<<< HEAD
=======
def statisticsData():
    firstDayWeekDay, monthRange=calendar.monthrange(2018, 10)
    lastDay = datetime.date(year=datetime.date.today().year, month=datetime.date.today().month, day=monthRange)
    print(lastDay)


>>>>>>> 59ea19bb39b5f508c1f37a233b9e0e6e78e1fcaf

def http():
    print('2')
    app.run(host=HOST, port=WEBPORT, debug=False, threaded=True)


if __name__ == '__main__':
<<<<<<< HEAD
    print('1')
=======
>>>>>>> 59ea19bb39b5f508c1f37a233b9e0e6e78e1fcaf
    threading.Thread(target=statisticsData).start()
    http()
