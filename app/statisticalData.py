# from app.database import User, Menu
# from numpy import *
from app.database import db, association, User, Sumlist, Audited, Cat, cycle, writtenForleave, \
    yingdao, holidays, shift, schclass, chidao, atttransaction, kuanggong, shidao, qingjia, tequan
import calendar, datetime


def start_tongji(st, ed):
    # s_yingdao(st, ed)
    s_chidaozaotui(st, ed)
    s_qingjia(st, ed)
    s_tequan(st, ed)
    s_sumlist(st, ed)


# 第一步，统计应到
def s_yingdao(st, ed):
    stt = datetime.datetime.strptime(st, '%Y-%m-%d')
    edt = datetime.datetime.strptime(ed, '%Y-%m-%d')
    delsql = "delete from t_yingdao where riqi BETWEEN '" + st + "' and '" + ed + "'"
    db.session.execute(delsql)
    db.session.commit()
    users = User.query.filter(User.DepID != None).all()
    # 循环每个用户
    for item in users:
        lists = list(
            get_yingdaolist(item.userid, item.EnrollNumber, item.ShiftID, item.CycleID, item.StartDate, stt, edt))
        print(lists)


def get_yingdaolist(userid, EnrollNumber, ShiftID, CycleID, StartDate, st, ed):
    if (CycleID != None):
        cycleDATA = cycle.query.get(CycleID)
        days = cycleDATA.days  # 循环几天
        StartDate = datetime.datetime.strptime(str(StartDate), '%Y-%m-%d')  # 什么时候开始
        cyclevalue = cycleDATA.cyclevalue  # 怎么循环
        while st <= ed:
            yield call_work_rest(userid, days, StartDate, cyclevalue, st, EnrollNumber, ShiftID, CycleID)
            st += datetime.timedelta(days=1)


# 计算某一天是否该上班
def call_work_rest(userid, days, StartDate, cyclevalue, st, EnrollNumber, ShiftID, CycleID):
    dangqianDate = st  # 这一天日期
    jiange = (dangqianDate - StartDate).days % days
    st = datetime.date(st.year, st.month, st.day)
    shangban = 0

    if str(jiange) in cyclevalue.split(','):
        shangban = 1
        db.session.add(yingdao(userid, 8, st))
        db.session.commit()
    else:
        db.session.add(yingdao(userid, 0, st))
        db.session.commit()

    return [userid, EnrollNumber, st, shangban, ShiftID, CycleID]


def s_chidaozaotui(st, ed):
    stt = datetime.datetime.strptime(st, '%Y-%m-%d')
    edt = datetime.datetime.strptime(ed, '%Y-%m-%d')

    delshidaosql = "delete from t_shidao where riqi BETWEEN '" + st + "' and '" + ed + "'"
    db.session.execute(delshidaosql)

    delkuanggongsql = "delete from t_kuanggong where riqi BETWEEN '" + st + "' and '" + ed + "'"
    db.session.execute(delkuanggongsql)

    delsql = "delete from t_chidaozaotui where convert(varchar(10),date,121) BETWEEN '" + st + "' and '" + ed + "'"
    db.session.execute(delsql)

    holidayssql = "UPDATE t_yingdao set zhuangtai=dbo.SumlistGetLeaveID(d_HOLIDAYS.CatID) from d_HOLIDAYS where convert(varchar(10),t_yingdao.riqi ,121) between convert(varchar(10),d_HOLIDAYS.STARTTIME,121) and convert(varchar(10),Dateadd(day,d_HOLIDAYS.DURATION-1,d_HOLIDAYS.STARTTIME),121)"
    db.session.execute(holidayssql)

    db.session.commit()

    users = User.query.filter(User.DepID != None).all()
    # 循环每个用户
    for item in users:
        userid = item.userid
        EnrollNumber = item.EnrollNumber
        ShiftID = item.ShiftID
        CycleID = item.CycleID
        StartDate = item.StartDate

        yingdaolist = yingdao.query.filter(db.and_(yingdao.riqi.between(stt, edt), yingdao.userid == userid)).all()
        schiftlist = db.session.query(shift.SchClassList).filter(shift.ID == ShiftID).first()
        if schiftlist != None:
            sclist = schiftlist.SchClassList.split(',')
            schclasslist = schclass.query.filter(schclass.schClassid.in_(sclist)).all()
            for item in yingdaolist:
                # 记录没有指纹的数量
                ifkuanggong = 0
                # 是否是中午
                ifzhongwu = 0
                # 循环每一天的数据，如果等于8，就说明这一天上班。
                wuzw = []
                # 循环上下午的上班时间
                for scclass_item in schclasslist:
                    ifkuanggong = ifkuanggong + 1
                    # 上班日期
                    sbdt = str(item.riqi)
                    # ==1,这个班是需要上的。
                    #  开始时间
                    sttm = scclass_item.StartTime.strftime('%H:%M:%S')
                    edtm = scclass_item.EndTime.strftime('%H:%M:%S')
                    shangbantm = sbdt + ' ' + sttm
                    xiabantm = sbdt + ' ' + edtm
                    # xuhaoshangban
                    if item.zhuangtai == 8:
                        db.session.add(shidao(userid, 9, item.riqi, scclass_item.schName, shangbantm, xiabantm))
                        db.session.commit()

                        # a 迟到
                        if ifkuanggong == 1:
                            ifzhongwu = ifzhongwu + 1
                        else:
                            ifzhongwu = ifzhongwu

                        chidaosql = " EnrollNumber=" + EnrollNumber + " and convert(varchar(10),date,121)='" + str(
                            item.riqi) + "' and  convert(varchar(5),date,108)  BETWEEN  '" + scclass_item.CheckInTime1.strftime(
                            '%H:%M') + "' and '" + scclass_item.CheckInTime2.strftime('%H:%M') + "'  "
                        dataview = db.session.query(atttransaction.date, atttransaction.EnrollNumber,
                                                    atttransaction.MachineID).filter(chidaosql).order_by(
                            atttransaction.date).first()
                        # 上班又有数据，
                        if dataview != None:
                            sjc = (datetime.datetime.strptime(shangbantm,
                                                              "%Y-%m-%d %H:%M:%S") - dataview.date).total_seconds() / 60
                            db.session.add(
                                chidao(dataview.date, shangbantm, str(ifzhongwu), sjc, 10, scclass_item.schName,
                                       userid))
                            # db.session.add(kuanggong(userid, 9, sbdt, scclass_item.schName, shangbantm, xiabantm))
                            # db.session.commit()

                        else:
                            # 没有数据记为旷工
                            wuzw.append(ifzhongwu)

                            db.session.add(kuanggong(userid, 13, sbdt, scclass_item.schName, shangbantm, xiabantm))
                            db.session.commit()

                        # b 早退
                        if ifkuanggong == 1:
                            ifzhongwu = ifzhongwu + 1
                        else:
                            ifzhongwu = ifzhongwu - 1
                        zaotuisql = " EnrollNumber=" + EnrollNumber + " and convert(varchar(11),date,121)='" + str(
                            item.riqi) + "' and  convert(varchar(5),date,108)  BETWEEN  '" + scclass_item.CheckOutTime1.strftime(
                            '%H:%M') + "' and '" + scclass_item.CheckOutTime2.strftime('%H:%M') + "'  "
                        dataview = db.session.query(atttransaction.date, atttransaction.EnrollNumber,
                                                    atttransaction.MachineID).filter(zaotuisql).order_by(
                            atttransaction.date.desc()).first()
                        if dataview != None:
                            sjc = (dataview.date - datetime.datetime.strptime(xiabantm,
                                                                              "%Y-%m-%d %H:%M:%S")).total_seconds() / 60
                            db.session.add(
                                chidao(dataview.date, xiabantm, str(ifzhongwu), sjc, 11, scclass_item.schName,
                                       userid))
                            # db.session.add(kuanggong(userid, 9, sbdt, scclass_item.schName, shangbantm, xiabantm))
                            # db.session.commit()
                        else:
                            # 没有数据记为旷工

                            wuzw.append(ifzhongwu)
                            db.session.add(kuanggong(userid, 13, sbdt, scclass_item.schName, shangbantm, xiabantm))
                            db.session.commit()
                    else:
                        # 不是应到，则为不上班，所以直接提交为0.
                        db.session.add(shidao(userid, 0, item.riqi, scclass_item.schName, shangbantm, xiabantm))
                        db.session.commit()
    print("迟到早退生成完成！")
    # 先记为实到，然后没有记为旷工，然后看有没有假条
    # if ifkuanggong == 2:
    #     print(wuzw)
    #     hj = 0
    #     for i in range(0, len(wuzw)):
    #         hj = hj + int(wuzw[i])
    #     print(hj)
    #     if hj >= 3:
    #         # dataview=yingdao.query.filter(db.and_(yingdao.userid==userid,yingdao.riqi==sbdt,yingdao.zhuangtai==9)).all()
    #         # dataview.zhuangtai=13
    #         print('h')
    #         # sql = "update t_shidao set zhuangtai=13 where userid=" + str(
    #         #     userid) + " and riqi='" + sbdt + "' and zhuangtai=9"
    #         # db.session.execute(sql)
    #         db.session.add(kuanggong(userid, 13, sbdt, '2'))
    #         db.session.commit()
    #
    #     elif hj < 3 and hj > 0:
    #         print('l')
    #         # sql = "update t_yingdao set zhuangtai=13 where userid=" + userid + " and riqi='" + sbdt + "' and zhuangtai=9  and schName='上午班' or userid=" + userid + " and riqi='" + sbdt + "' and zhuangtai=9  and schName='下午班'"
    #         # db.session.execute(sql)
    #         # dataview = shidao.query.filter(
    #         #     db.and_(shidao.userid == userid, shidao.riqi == sbdt, shidao.zhuangtai == 9)).first()
    #         # if dataview != None:
    #         #     dataview.zhuangtai = 13
    #         #     db.session.add(dataview)
    #         db.session.add(kuanggong(userid, 13, sbdt, '1'))
    #         db.session.commit()
    # sql = "update t_shidao set zhuangtai=" + str(leaves[i].Category) + " where userid=" + str(
    #     item.userid) + " and sttime >= '" + str(leaves[i].StartTime) + "' and edtime<= '" + str(
    #     leaves[i].EndTime) + "'"
    # db.session.execute(sql)
    # db.session.commit()


def s_qingjia(st, ed):
    stt = datetime.datetime.strptime(st, '%Y-%m-%d')
    edt = datetime.datetime.strptime(ed, '%Y-%m-%d')

    users = User.query.filter(User.DepID != None).all()
    # 循环每个用户
    for item in users:
        leaves = writtenForleave.query.filter(db.and_(writtenForleave.StartTime >= st, writtenForleave.EndTime <= ed,
                                                      writtenForleave.LeaveUserId == item.userid,
                                                      writtenForleave.ifComplete == 1,
                                                      writtenForleave.Agree == 1)).all()
        for i in range(0, len(leaves)):
            # jiange = (leaves[i].EndTime - leaves[i].StartTime).days
            # print(type(leaves[i].StartTime))
            sql = "update t_kuanggong set zhuangtai=" + str(leaves[i].Category) + " where userid=" + str(
                item.userid) + " and sttime >= '" + str(leaves[i].StartTime) + "' and sttime <= '" + str(
                leaves[i].EndTime) + "' and zhuangtai=13 or userid=" + str(
                item.userid) + " and edtime >= '" + str(leaves[i].StartTime) + "' and edtime<= '" + str(
                leaves[i].EndTime) + "' and zhuangtai=13"
            # print(sql)
            db.session.execute(sql)
            db.session.commit()
    dataviews = db.session.query(db.func.count(kuanggong.schName).label("cishu"), kuanggong.schName, kuanggong.userid,
                                 kuanggong.riqi, kuanggong.zhuangtai).filter(
        db.and_(kuanggong.riqi >= st, kuanggong.riqi <= ed, kuanggong.zhuangtai == 13)).group_by(kuanggong.schName,
                                                                                                 kuanggong.userid,
                                                                                                 kuanggong.riqi,
                                                                                                 kuanggong.zhuangtai).all()
    # print(dataviews)把旷工的导进去
    for i in range(0, len(dataviews)):
        # print (dataviews[i].cishu)
        sql = "update t_shidao set zhuangtai=" + str(dataviews[i].zhuangtai) + " where userid =" + str(
            dataviews[i].userid) + " and riqi='" + str(dataviews[i].riqi) + "' and schName='" + dataviews[
                  i].schName + "'"
        print(sql)
        db.session.execute(sql)
        db.session.commit()

    dataviews = db.session.query(db.func.count(kuanggong.schName).label("cishu"), kuanggong.schName, kuanggong.userid,
                                 kuanggong.riqi, kuanggong.zhuangtai).filter(
        db.and_(kuanggong.riqi >= st, kuanggong.riqi <= ed, kuanggong.zhuangtai != 9,
                kuanggong.zhuangtai != 13)).group_by(kuanggong.schName,
                                                     kuanggong.userid,
                                                     kuanggong.riqi,
                                                     kuanggong.zhuangtai).all()
    # print(dataviews)把不是旷工也不是实到的更新进去
    for i in range(0, len(dataviews)):
        # print (dataviews[i].cishu)
        sql = "update t_shidao set zhuangtai=" + str(dataviews[i].zhuangtai) + " where userid =" + str(
            dataviews[i].userid) + " and riqi='" + str(dataviews[i].riqi) + "' and schName='" + dataviews[
                  i].schName + "'"
        print(sql)
        db.session.execute(sql)
        db.session.commit()
    print("请假生成完成！")


def s_tequan(st, ed):
    stt = datetime.datetime.strptime(st, '%Y-%m-%d')
    edt = datetime.datetime.strptime(ed, '%Y-%m-%d')

    users = User.query.filter(User.DepID != None).all()
    # 循环每个用户
    for item in users:
        leaves = tequan.query.filter(db.and_(tequan.StartTime >= st, tequan.EndTime <= ed,
                                             tequan.LeaveUserId == item.userid)).all()
        for i in range(0, len(leaves)):
            # jiange = (leaves[i].EndTime - leaves[i].StartTime).days
            # print(type(leaves[i].StartTime))
            sql = "update t_shidao set zhuangtai=" + str(leaves[i].Category) + " where userid=" + str(
                item.userid) + " and sttime >= '" + str(leaves[i].StartTime) + "' and sttime <= '" + str(
                leaves[i].EndTime) + "'  and zhuangtai<>0  or userid=" + str(
                item.userid) + " and edtime >= '" + str(leaves[i].StartTime) + "' and edtime<= '" + str(
                leaves[i].EndTime) + "' and zhuangtai<>0 "
            print(sql)
            db.session.execute(sql)
            db.session.commit()
    print("特权生成完成！")


# 最后一步，把所有数据统一到统计表里。
def s_sumlist(st, ed):
    stt = datetime.datetime.strptime(st, '%Y-%m-%d')
    edt = datetime.datetime.strptime(ed, '%Y-%m-%d')
    delsumlistsql = "DELETE FROM [d_sumlist] where Date BETWEEN '" + st + "' and '" + ed + "'"
    db.session.execute(delsumlistsql)
    db.session.commit()

    yingdaosql = "INSERT into d_sumlist (UserID,LeaveID,Date) SELECT userid,zhuangtai,riqi FROM t_yingdao where zhuangtai <>0 and t_yingdao.riqi BETWEEN '" + st + "' and '" + ed + "'"
    db.session.execute(yingdaosql)
    db.session.commit()
    shidaosql = "INSERT into d_sumlist (UserID,LeaveID,Date) SELECT userid,zhuangtai,riqi FROM t_shidao where zhuangtai <>0 and t_shidao.riqi BETWEEN '" + st + "' and '" + ed + "'"
    db.session.execute(shidaosql)
    db.session.commit()
    chidaosql = "insert into d_sumlist (UserID,LeaveID,Date) select userid,LeaveID,date from t_chidaozaotui where  sjc<0 and convert(varchar(11),date,121) BETWEEN '" + st + "' and '" + ed + "'"
    db.session.execute(chidaosql)
    db.session.commit()
    print("生成完成！")
