from flask import Blueprint, render_template, session, redirect, url_for, \
    request, flash, g, jsonify, abort, json
from app.database import db, User, writtenForleave, association, Cat, WrittenforLeaveSign, Audited, Role, Menu, Sumlist, \
    machinesstate, chidao, atttransaction, qingjia, tequan,log
from flask_login import login_required, login_user, logout_user, current_user
from app import app
from datetime import datetime, timedelta

# from flask_sqlalchemy import SQLAlchemy

# from sqlalchemy import create_engine, Column, Integer, String, func, select,case

mod = Blueprint('view', __name__)


# 申请---------------------------------------------------------------------
@mod.route('/', methods=['GET', 'POST'])
@login_required
def index():
    # return render_template("t-application.html")
    return redirect(url_for('.Application'))


# 申请
@mod.route('/Application/<int:page>')
@mod.route('/Application', methods=['GET', 'POST'])
@login_required
def Application(page=1):
    # if request.method == "POST":
    #     wid = request.form.get('wid', '')

    leaves = writtenForleave.query.order_by(writtenForleave.LeaveID.desc()).filter(
        db.or_(writtenForleave.LeaveUserId == current_user.userid,
               writtenForleave.WriteUserID == current_user.userid)).paginate(
        page, per_page=10, error_out=False)
    cats = Cat.query.all()
    return render_template("t-application.html", leaves=leaves, cats=cats)


# 新增申请
@mod.route('/application-add', methods=['GET', 'POST'])
@login_required
def Application_add():
    print(current_user.DepID)
    if request.method == "POST":
        items = request.form.getlist('other')
        others = ','.join(items)
        # print(items)
        LeaveUserId = request.form['leaveuser']
        LeaveUser = User.query.get(int(LeaveUserId))
        StartTime = request.form['StartTime']
        EndTime = request.form['EndTime']
        SubUser = request.form['SubUser']
        Category = request.form['Category']
        Wtext = request.form['Wtext']
        # print(type(StartTime))
        # print(request.form['StartTime'])
        sttt = datetime.strptime(StartTime, '%Y-%m-%d %H:%M')
        endt = datetime.strptime(EndTime, '%Y-%m-%d %H:%M')
        # sttt = StartTime
        # endt = EndTime
        # print(sttt)
        if (SubUser == LeaveUserId):
            flash("错误：替班人员不能为请假人")
        elif InspectTime(sttt, endt):
            db.session.add(
                writtenForleave(current_user.DepID, LeaveUserId, LeaveUser.username, LeaveUser.truename,
                                LeaveUser.EnrollNumber, sttt, endt, SubUser,
                                others, Category,
                                current_user.userid, Wtext))
            db.session.commit()
            return redirect(url_for('.Application'))

    return render_template("t-application-form.html",
                           users=User.query.filter_by(DepID=current_user.DepID).all(),
                           cats=Cat.query.filter_by(isVacation=True).all(),
                           firsttime=datetime.now().strftime('%Y-%m-%d 09:00'),
                           endtime=datetime.now().strftime('%Y-%m-%d 17:00'))


# 修改请假
@mod.route('/application-edit/<id>', methods=['GET', 'POST'])
@login_required
def Application_edit(id):
    dataview = writtenForleave.query.get(int(id))
    if dataview.Send != '0':
        flash('已经发送的不能再修改')
        return redirect(url_for('.Application'))

    if request.method == "POST":
        items = request.form.getlist('other')
        print(items)
        others = ','.join(items)
        # print(others)
        dataview.LeaveUserId = request.form['leaveuser']
        LeaveUser = User.query.get(int(dataview.LeaveUserId))
        dataview.UserName = LeaveUser.username
        dataview.LoginName = LeaveUser.truename
        dataview.EnrollNumber = LeaveUser.EnrollNumber
        dataview.SubUserID = request.form['SubUser']
        dataview.otherUser = others
        dataview.Category = request.form['Category']
        dataview.Send = '0'
        dataview.Wtext = request.form['Wtext']

        StartTime = request.form['StartTime']
        EndTime = request.form['EndTime']

        # print(request.form['StartTime'])
        # print(request.form['EndTime'])
        # sttt = StartTime
        # endt = EndTime
        # print(type(sttt))
        sttt = datetime.strptime(StartTime, '%Y-%m-%d %H:%M')
        endt = datetime.strptime(EndTime, '%Y-%m-%d %H:%M')

        # print(type(sttt))
        if InspectTime(sttt, endt):
            dataview.StartTime = sttt
            dataview.EndTime = endt
            db.session.add(dataview)
            db.session.commit()
        return redirect(url_for('.Application'))

    return render_template("t-application-edit.html", dataview=dataview,
                           users=User.query.filter_by(DepID=current_user.DepID).all(),
                           cats=Cat.query.filter_by(isVacation=True).all())


# 删除请假
@mod.route('/application-del/<id>', methods=["GET", "POST"])
@login_required
def Application_del(id):
    dataview = writtenForleave.query.get(int(id))

    if (dataview.Send == '0'):
        db.session.delete(dataview)
        db.session.commit()
        flash("删除成功！")
        return redirect(url_for('.Application'))
    else:
        flash("已经发送的不可以删除！")
        return redirect(url_for('.Application'))


# 发送请假
@mod.route('/application-send/<id>', methods=["GET", "POST"])
@login_required
def Application_send(id):
    dataview = writtenForleave.query.get(int(id))
    send = dataview.Send
    # print(send)
    if (dataview.Send != '0'):
        flash("已发送完成的不可再发送")
    else:
        dataview.Send = leavesendwhere(dataview, 0)
        db.session.add(dataview)
        db.session.commit()
        flash("发送成功")
    return redirect(request.args.get("next") or url_for('.Application'))


# 批示-------------------------------------------------------------------

# 这里决定你能看到什么。
# @mod.route('/Instructions/<int:page>')


@mod.route('/Instructions', methods=["GET", "POST"])
@login_required
def Instructions(page=1):
    if request.method == "POST":
        agree = request.form['act']
        ls = request.form.getlist('xz')
        for it in ls:
            if it != "":
                piliangpishi(it, agree)

    page = request.args.get('page')
    dept = request.args.get('dept')
    custname = request.args.get('custname')
    leaves = type(object)
    Roles = Role.query.filter_by(ID=current_user.RoleID).first()
    RoleChar = Roles.RoleChar
    RoleCanSeeData = Roles.CanSeeData
    OnlyAssociation = Roles.OnlyAssociation
    where = ""
    if page != None:
        page = int(page)
    if dept != "all":
        try:
            where = " d_writtenForleave.AssociationID=" + dept + " and "
        except TypeError:
            pass
    if custname != "":
        try:
            where = where + "  d_writtenForleave.EnrollNumber ='" + custname + "' or " + where + "  d_writtenForleave.LoginName='" + custname + "' or " + where + "  d_writtenForleave.UserName='" + custname + "' and";
        except TypeError:
            pass
    if OnlyAssociation:
        # 只能看本单位的
        where = " d_writtenForleave.associationID = " + str(current_user.DepID) + " and "
    if RoleCanSeeData == 0:
        # 只能看发送到本人的
        st = WrittenforLeaveSign.query.filter_by(UserID=current_user.userid).all()
        ls = []
        for item in st:
            ls.append(item.LeaveID)

        if len(ls) > 1:
            where = where + " d_writtenForleave.Send= '" + RoleChar + "' or d_writtenForleave.LeaveID in " + str(
                tuple(ls)) + " and "
        elif len(ls) == 1:
            where = where + " d_writtenForleave.Send= '" + RoleChar + "' or d_writtenForleave.LeaveID =" + str(
                ls[0]) + " and "
        else:
            where = where + " d_writtenForleave.Send= '" + RoleChar + "'  and "
    else:
        where = where + " d_writtenForleave.Send <> '0' and "
    if where != "":
        where = where.strip()
        where = where[:-3]
    print(where)

    leaves = writtenForleave.query.filter(where).order_by(writtenForleave.LeaveID.desc()).paginate(page, per_page=10,
                                                                                                   error_out=False)

    return render_template("t-instruct.html", leaves=leaves, cats=Cat.query.all(), Dept=association.query.all())


# @mod.route('/instructions/pl',methods=['POST'])
# @login_required
# def InstructionsPl:


# 批示审批
@mod.route('/Instructions-opinion/<id>', methods=["GET", "POST"])
@login_required
def instruct_opinion(id):
    # return redirect(url_for('.Instructions'))
    dataview = writtenForleave.query.get(int(id))
    if request.method == 'POST':
        # print('aa')
        agree = request.form['agree']
        # print("agree::" + agree)
        bz = request.form['bz']
        # print("bz::" + bz)
        gongcai = request.form.getlist('gongcai')
        gc = ','.join(gongcai)
        # print("gc::" + gc)
        # print(request.form['gongcai'])

        # print('dd')

        pishi(id, agree, bz, gongcai)
        return redirect(url_for('.Instructions'))

    return render_template("t-instruct-opinion.html", dataview=dataview,
                           users=User.query.filter_by(DepID=current_user.DepID).all(), cats=Cat.query.filter_by().all())


def pishi(id, agree, bz, gc):
    # print("pishi............")
    dataview = writtenForleave.query.get(int(id))
    if (int(agree) == 1):
        send = leavesendwhere(dataview, current_user.RoleID)
        # print('send:' + str(send))
        dataview.Send = str(send)
        dataview.ifTolerance = gc
        # 完成了批示。
        if (str(send) == '1'):
            # print('ee')
            dataview.ifComplete = 1
            dataview.Agree = 1
            # print('EE')
    else:
        # print('FF')
        dataview.Send = '1'
        dataview.ifComplete = True
        dataview.Agree = False
        # print('fff')
        # print('gggg')
    db.session.add(dataview)
    db.session.commit()

    db.session.add(WrittenforLeaveSign(dataview.LeaveID, current_user.userid, agree, bz))
    db.session.commit()


def piliangpishi(id, agree):
    dataview = writtenForleave.query.get(int(id))
    if (int(agree) == 1):
        send = leavesendwhere(dataview, current_user.RoleID)
        print('send:' + str(send))
        dataview.Send = str(send)
        # dataview.ifTolerance = gc
        if (str(send) == '1'):
            # print('ee')
            dataview.ifComplete = 1
            dataview.Agree = 1
            # print('EE')
    else:
        # print('FF')
        dataview.Send = '1'
        dataview.ifComplete = True
        dataview.Agree = False
        print('fff')
        # print('gggg')
    db.session.add(dataview)
    db.session.commit()

    db.session.add(WrittenforLeaveSign(dataview.LeaveID, current_user.userid, agree, ""))
    db.session.commit()


@mod.route('/instruct-back/<id>', methods=["GET", "POST"])
@login_required
def instruct_back(id):
    dataview = writtenForleave.query.get(id)
    if dataview.ifComplete == True:
        flash('已经结束的不可以再退回！')
    else:
        dataview.Send = 0
        # dataview.Agree=None
        db.session.add(dataview)
        db.session.commit()

    return redirect(url_for('.Instructions'))


# 特批
@mod.route('/tepi', methods=['GET', 'post'])
@login_required
def tepi(page=1):
    sql = "1=1"
    dept = request.args.get('dept')
    # qx = request.args.get('role')
    # startime = request.args.get('startime')
    # endtime = request.args.get('endtime')
    custname = request.args.get('custname')
    # if (startime != None and endtime != None):
    #     sql = "t_tequan.AssociationID <>1 and t_tequan.Date BETWEEN '" + startime + "' and '" + endtime + "' "
    if (dept != 'all' and dept != None):
        sql = sql + " and t_tequan.associationID=" + dept
    # if qx != "all":
    #     try:
    #         sql = sql + " and t_tequan.RoleID=" + qx
    #     except TypeError:
    #         pass
    if (custname != '' and custname != None):
        sql = sql + " and t_tequan.LoginName='" + custname + "' or " + sql + " and  t_tequan.UserName='" + custname + "' or " + sql + " and t_tequan.enrollnumber='" + custname + "'"
    print(sql)

    # dataview=db.session.query(tequan.DepID,tequan.LeaveID,tequan.EnrollNumber,tequan.LoginName,tequan.StartTime,tequan.EndTime,tequan.Categorys).order_by(tequan.LeaveID.desc()).paginate(page,per_page=20,error_out=False)
    dataview = tequan.query.filter(sql).order_by(tequan.LeaveID.desc()).paginate(page,
                                                                                 per_page=20,
                                                                                 error_out=False)
    # dataview = db.session.query(qingjia.zhuangtai, qingjia.schName, qingjia.riqi, User.truename, User.EnrollNumber,
    #                             association.DepName, Cat.catname).order_by(qingjia.id.desc()).outerjoin(
    #     User, User.userid == qingjia.userid).outerjoin(association, association.DepID == User.DepID).outerjoin(Cat,
    #                                                                                                            Cat.id == qingjia.zhuangtai).paginate(
    #     page, per_page=10, error_out=False)

    return render_template("t-tepilist.html", dataview=dataview, users=User.query.all(), cats=Cat.query.all(),
                           Dept=association.query.all())


# 特批
@mod.route('/addtepi', methods=['GET', 'post'])
@login_required
def addtepi(page=1):
    if request.method == 'POST':
        depts = request.form['depts']
        user = request.form['user']
        StartTime = request.form['StartTime']
        EndTime = request.form['EndTime']
        sttt = datetime.strptime(StartTime, '%Y-%m-%d %H:%M')
        endt = datetime.strptime(EndTime, '%Y-%m-%d %H:%M')
        Category = request.form['Category']
        db.session.add(tequan(depts, user, sttt, endt, Category, current_user.userid))

        db.session.commit()

        flash("特权审批提交成功！")
        return redirect(url_for('.tepi'))

        print(depts)
        print(user)
        print(StartTime)
        print(EndTime)

    return render_template("t-tepi.html", users=User.query.all(), cats=Cat.query.all(), Dept=association.query.all(),
                           firsttime=datetime.now().strftime('%Y-%m-%d 09:00'),
                           endtime=datetime.now().strftime('%Y-%m-%d 17:00'))


@mod.route('/tepi-del/<id>', methods=['GET', 'post'])
@login_required
def deltepi(id):
    dataview = tequan.query.get(int(id))
    db.session.delete(dataview)
    db.session.commit()
    flash("删除成功！")
    return redirect(url_for('.tepi'))


# 修改请假特批
@mod.route('/tepi-edit/<id>', methods=['GET', 'post'])
@login_required
def tepiedit(id):
    # return redirect(url_for('.tepi'))
    dataview = tequan.query.get(int(id))
    if request.method == "POST":
        dataview.DepID = request.form['depts']
        dataview.LeaveUserId = request.form['user']
        StartTime = request.form['StartTime']
        EndTime = request.form['EndTime']
        dataview.StartTime = datetime.strptime(StartTime, '%Y-%m-%d %H:%M')
        dataview.EndTime = datetime.strptime(EndTime, '%Y-%m-%d %H:%M')
        dataview.Category = request.form['Category']
        db.session.add(dataview)
        db.session.commit()
        flash('修改成功')
        return redirect(url_for('.tepi'))

    return render_template('t-tepi-edit.html', users=User.query.all(), cats=Cat.query.all(),
                           Dept=association.query.all(),
                           firsttime=datetime.now().strftime('%Y-%m-%d 09:00'),
                           endtime=datetime.now().strftime('%Y-%m-%d 17:00'), dataview=dataview)


# 统计------------------------------------------------------------------------------
@mod.route('/generatereports', methods=['GET', 'POST'])
@login_required
def generatereports():
    if request.method == "POST":
        from app.statisticalData import start_tongji
        # startdate = datetime.strptime(request.form['startdate'],"%Y-%m-%d").date()
        # enddate =datetime.strptime(request.form['enddate'],"%Y-%m-%d").date()
        startdate = request.form['startdate']
        enddate = request.form['enddate']
        # print(startdate)
        # print(enddate)
        # print(type(startdate))
        start_tongji(startdate, enddate)
    return render_template("t-generatereports.html")


@mod.route('/statistics')
@login_required
def statistics(page=1):
    page = request.args.get('page')
    dept = request.args.get('dept')
    startime = request.args.get('startime')
    endtime = request.args.get('endtime')
    custname = request.args.get('custname')
    sql = " d_sumlist.LeaveID<>0 "
    if page != None:
        page = int(page)
    if (startime != None and endtime != None):
        sql = sql + " and d_sumlist.Date BETWEEN '" + startime + "' and '" + endtime + "' "
    if (dept != 'all' and dept != None):
        sql = sql + " and d_association.AssociationID=" + dept
    if (custname != '' and custname != None):
        sql = sql + " and d_user.LoginName='" + custname + "' or " + sql + " and  d_user.UserName='" + custname + "' or " + sql + " and d_user.EnrollNumber='" + custname + "'"
    print(sql)
    dataview = db.session.query(Sumlist.UserID, User.truename, User.EnrollNumber, association.DepName, Sumlist.Date,
                                (db.func.count(db.case([(Sumlist.LeaveID == 1, Sumlist.UserID)])) / 2.00).label(
                                    "事假"),
                                (db.func.count(db.case([(Sumlist.LeaveID == 2, Sumlist.UserID)])) / 2.00).label(
                                    "病假"),
                                (db.func.count(db.case([(Sumlist.LeaveID == 3, Sumlist.UserID)])) / 2.00).label(
                                    "公差"),
                                (db.func.count(db.case([(Sumlist.LeaveID == 4, Sumlist.UserID)])) / 2.00).label(
                                    "产假"),
                                (db.func.count(db.case([(Sumlist.LeaveID == 5, Sumlist.UserID)])) / 2.00).label(
                                    "婚假"),
                                (db.func.count(db.case([(Sumlist.LeaveID == 6, Sumlist.UserID)])) / 2.00).label(
                                    "休假"),
                                (db.func.count(db.case([(Sumlist.LeaveID == 7, Sumlist.UserID)])) / 2.00).label(
                                    "其他假"),
                                db.func.count(db.case([(Sumlist.LeaveID == 8, Sumlist.UserID)])).label("应到"),
                                (db.func.count(db.case([(Sumlist.LeaveID == 9, Sumlist.UserID)])) / 2.00).label(
                                    "实到"),
                                db.func.count(db.case(
                                    [(db.or_(Sumlist.LeaveID == 10, Sumlist.LeaveID == 11), Sumlist.UserID)])).label(
                                    "迟到早退"),
                                db.func.count(db.case([(Sumlist.LeaveID == 12, Sumlist.UserID)])).label("脱岗"),
                                (db.func.count(db.case([(Sumlist.LeaveID == 13, Sumlist.UserID)])) / 2.00).label(
                                    "未按指纹")
                                ).outerjoin(User, Sumlist.UserID == User.userid).outerjoin(
        association, association.DepID == User.DepID).filter(sql).group_by(Sumlist.Date, Sumlist.UserID,
                                                                           User.EnrollNumber,
                                                                           User.truename, association.DepName).order_by(
        association.DepName, Sumlist.UserID, Sumlist.Date).paginate(page, per_page=10, error_out=False)
    #
    #
    #     dataview = db.session.query(Sumlist.Date, Sumlist.LeaveID, User.EnrollNumber, User.truename,
    #                                 association.DepName).outerjoin(User,
    #                                                                Sumlist.UserID == User.userid).outerjoin(
    #         association, association.DepID == User.DepID).paginate(page, per_page=10, error_out=False)
    #     # return redirect(url_for('.statistics'))
    return render_template("t-statistics.html", dataview=dataview, Dept=association.query.all(),
                           sttime=datetime.now().strftime('%Y-%m-01'),
                           edtime=datetime.now().strftime('%Y-%m-%d'))


@mod.route('/search')
@login_required
def search():
    list = association.query.all()
    dataview = []
    sql = "1<>1"
    dept = request.args.get('dept')
    qx = request.args.get('role')
    startime = request.args.get('startime')
    endtime = request.args.get('endtime')
    custname = request.args.get('custname')
    for item in list:
        items = []
        if (startime != None and endtime != None):
            sql = "d_association.AssociationID=" + str(
                item.DepID) + " and d_user.AssociationID <>1 and d_sumlist.Date BETWEEN '" + startime + "' and '" + endtime + "' "
        if (dept != 'all' and dept != None):
            sql = sql + " and d_association.AssociationID=" + dept
        if qx != "all":
            try:
                sql = sql + " and d_user.RoleID=" + qx
            except TypeError:
                pass
        if (custname != '' and custname != None):
            sql = sql + " and d_user.LoginName='" + custname + "' or " + sql + " and  d_user.UserName='" + custname + "' or " + sql + " and d_user.EnrollNumber='" + custname + "'"


        sumlist = db.session.query(Sumlist.UserID, User.truename, User.EnrollNumber, association.DepName,
                                   (db.func.count(db.case([(Sumlist.LeaveID == 1, Sumlist.UserID)])) / 2.00).label(
                                       "事假"),
                                   (db.func.count(db.case([(Sumlist.LeaveID == 2, Sumlist.UserID)])) / 2.00).label(
                                       "病假"),
                                   (db.func.count(db.case([(Sumlist.LeaveID == 3, Sumlist.UserID)])) / 2.00).label(
                                       "公差"),
                                   (db.func.count(db.case([(Sumlist.LeaveID == 4, Sumlist.UserID)])) / 2.00).label(
                                       "产假"),
                                   (db.func.count(db.case([(Sumlist.LeaveID == 5, Sumlist.UserID)])) / 2.00).label(
                                       "婚假"),
                                   (db.func.count(db.case([(Sumlist.LeaveID == 6, Sumlist.UserID)])) / 2.00).label(
                                       "休假"),
                                   (db.func.count(db.case([(Sumlist.LeaveID == 7, Sumlist.UserID)])) / 2.00).label(
                                       "其他假"),
                                   db.func.count(db.case([(Sumlist.LeaveID == 8, Sumlist.UserID)])).label("应到"),
                                   (db.func.count(db.case([(Sumlist.LeaveID == 9, Sumlist.UserID)])) / 2.00).label(
                                       "实到"),
                                   db.func.count(db.case(
                                       [(db.or_(Sumlist.LeaveID == 10, Sumlist.LeaveID == 11), Sumlist.UserID)])).label(
                                       "迟到早退"),
                                   db.func.count(db.case([(Sumlist.LeaveID == 12, Sumlist.UserID)])).label("脱岗"),
                                   (db.func.count(db.case([(Sumlist.LeaveID == 13, Sumlist.UserID)])) / 2.00).label(
                                       "未按指纹")
                                   ).group_by(Sumlist.UserID, User.truename, User.EnrollNumber,
                                              association.DepName).outerjoin(User,
                                                                             Sumlist.UserID == User.userid).outerjoin(
            association, association.DepID == User.DepID).filter(sql).order_by(association.DepName).all()
        items.append(sumlist)
        pj = len(sumlist)
        dwlist = db.session.query((db.func.count(db.case([(Sumlist.LeaveID == 1, Sumlist.UserID)])) / 2.00 / pj).label(
            "事假"),
            (db.func.count(db.case([(Sumlist.LeaveID == 2, Sumlist.UserID)])) / 2.00 / pj).label(
                "病假"),
            (db.func.count(db.case([(Sumlist.LeaveID == 3, Sumlist.UserID)])) / 2.00 / pj).label(
                "公差"),
            (db.func.count(db.case([(Sumlist.LeaveID == 4, Sumlist.UserID)])) / 2.00 / pj).label(
                "产假"),
            (db.func.count(db.case([(Sumlist.LeaveID == 5, Sumlist.UserID)])) / 2.00 / pj).label(
                "婚假"),
            (db.func.count(db.case([(Sumlist.LeaveID == 6, Sumlist.UserID)])) / 2.00 / pj).label(
                "休假"),
            (db.func.count(db.case([(Sumlist.LeaveID == 7, Sumlist.UserID)])) / 2.00 / pj).label(
                "其他假"),
            (db.func.count(db.case([(Sumlist.LeaveID == 8, Sumlist.UserID)])) / pj).label("应到"),
            (db.func.count(db.case([(Sumlist.LeaveID == 9, Sumlist.UserID)])) / 2.00 / pj).label(
                "实到"),
            (db.func.count(db.case(
                [(db.or_(Sumlist.LeaveID == 10, Sumlist.LeaveID == 11), Sumlist.UserID)])) / pj).label(
                "迟到早退"),
            (db.func.count(db.case([(Sumlist.LeaveID == 12, Sumlist.UserID)])) / pj).label("脱岗"),
            (db.func.count(db.case([(Sumlist.LeaveID == 13, Sumlist.UserID)])) / 2.00 / pj).label(
                "未按指纹"), association.DepName,
        ).group_by(association.DepName).outerjoin(User,
                                                  Sumlist.UserID == User.userid).outerjoin(
            association, association.DepID == User.DepID).filter(sql).order_by(association.DepName).all()
        items.append(dwlist)
        dataview.append(items)

    return render_template("t-search.html", Dept=association.query.all(), user=User.query.all(), roles=Role.query.all(),
                           dataview=dataview,
                           sttime=datetime.now().strftime('%Y-%m-01'),
                           edtime=datetime.now().strftime('%Y-%m-%d'))


@mod.route('/atttransaction')
@login_required
def att(page=1):
    page = request.args.get('page')
    dept = request.args.get('dept')
    startime = request.args.get('startime')
    endtime = request.args.get('endtime')
    custname = request.args.get('custname')
    sql = " 1<>1"
    if page != None:
        page = int(page)
    if (startime != None and endtime != None):
        sql = "d_user.AssociationID<>'' and d_atttransaction.Date BETWEEN '" + startime + "' and '" + endtime + "' "
    if (dept != 'all' and dept != None):
        sql = sql + " and d_association.AssociationID=" + dept
    if (custname != '' and custname != None):
        sql = sql + " and d_user.LoginName='" + custname + "' or " + sql + " and  d_user.UserName='" + custname + "' or " + sql + " and d_user.EnrollNumber='" + custname + "'"
    print(sql)
    data = db.session.query(atttransaction.MachineID, atttransaction.EnrollNumber, User.truename,
                            atttransaction.date, association.DepName).filter(
        sql).outerjoin(User,
                       User.EnrollNumber == atttransaction.EnrollNumber).outerjoin(
        association, association.DepID == User.DepID).order_by(association.DepName, User.username,
                                                               atttransaction.date).paginate(page, per_page=10,
                                                                                             error_out=False)

    return render_template('t-attransaction.html', dataview=data, Dept=association.query.all(),
                           sttime=datetime.now().strftime('%Y-%m-01'),
                           edtime=datetime.now().strftime('%Y-%m-%d'))


# --------------------------------------用户登陆之类----------------------------------------
@mod.route('/changepassword', methods=['GET', 'POST'])
@login_required
def changepassword():
    if request.method == "POST":
        oldpass = request.form["password"]
        newpass = request.form["newpass"]
        repass = request.form["repass"]

        value = md5(oldpass)

        print(value)
        if value == current_user.password:

            if newpass == repass:

                user = User.query.filter_by(userid=current_user.userid).first()
                hash2 = md5(newpass)
                user.password = hash2
                db.session.add(user)
                db.session.commit()

                flash('密码更新成功，请重新登陆.')
                return redirect(url_for('.login'))

            else:
                print("两次密码输入不一样。请重新输入！")
                flash("两次密码输入不一样。请重新输入！")
        else:
            print('原始密码输入错误')
            flash('原始密码输入错误')

    return render_template("t-changepassword.html")


@mod.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('.login'))


@mod.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if (username == ''):
            flash("用户名不能为空")
        elif (password == ''):
            flash("密码不能为空")
        else:
            value = md5(password)

            user = User.query.filter(db.or_(db.and_(User.username == username, User.password == value),
                                            db.and_(User.truename == username, User.password == value),
                                            db.and_(User.EnrollNumber == username, User.password == value))).first()
            if not user:
                flash('账号或密码错误！')
            else:
                login_user(user, remember=True)
                # menus = dict(menu=MenuRole.query.filter_by(RoleID=current_user.RoleID).outerjoin(Menu, MenuRole.MenuID == Menu.ID))
                flash("登陆成功")
                return redirect(request.args.get("next") or url_for('.index'))

    return render_template("login.html")


@mod.route("/settoken/<user>/<token>")
def settooken(user, token):
    print(user)
    print(token)
    return ""


@mod.route("/gettoken/<user>")
def gettoken(user):
    data = {user: 'sfd'}
    return json.dumps(data, ensure_ascii=False)


# 检查时间范围是否正确#
def InspectTime(sttt, endt):
    # sttt = datetime.strptime(sttt, '%Y-%m-%d %H:%M')
    # endt = datetime.strptime(endt, '%Y-%m-%d %H:%M')
    if (sttt >= endt):
        flash("错误：截止时间小于起始时间")
        return False

    if (sttt < datetime.now() or endt < datetime.now()):
        flash("错误：起止时间不能小于当天时间")
        return False
    else:
        return True


# 送到哪里
def leavesendwhere(dataview, roleid):
    delta = (dataview.EndTime - dataview.StartTime).total_seconds() / 3600 / 24
    leaveuser = User.query.filter_by(userid=dataview.LeaveUserId).first()  # 请假人的用户字段
    print('请假人权限ID：' + str(leaveuser.RoleID))
    aulist = Audited.query.filter_by(RoleID=leaveuser.RoleID).all()  # 该请假人的执行规则
    # aulist = Audited.query.filter().all()

    # 查询请假人的规则
    for item in aulist:
        if delta <= int(item.days) and item.Da == False and delta > int(item.days2) and item.Da2 == True:
            SH = item.SH1
        elif delta > int(item.days) and item.Da == True:
            SH = item.SH1
    list = SH.split('|')
    lon = len(list)
    print(list)
    role = Role.query.filter_by(ID=roleid).first()  # 登陆用户的权限

    if role:
        cr = role.RoleChar
        wz = list.index(cr)  # 确定当前在哪一个。
    else:
        wz = -1

    if lon == (wz + 1):
        # 结束
        send = 1
    else:
        st = list[wz + 1]
        # print(st)
        # ro = Role.query.filter_by(RoleChar=st).first()
        # send = ro.ID
        send = st
    print('送到：' + str(send))
    return send


def md5(str):
    import hashlib
    m = hashlib.md5()
    m.update(str.encode('utf-8'))
    return m.hexdigest()


@mod.route('/getusers', methods=['GET', 'POST'])
@login_required
def ajaxgetusers():
    if request.method == "POST":
        id = request.form['key']
        dataview = db.session.query(User.userid, User.truename).filter(User.DepID == id).all()
        dt = jsonify(dataview)
        return dt


def insert_log(data,event):
    userid=current_user.userid
    rq=datetime.now()
    log(userid,data,rq,event)


# 设置全局变量------------------------------------------------------
def getrole():
    role = Role.query.get(current_user.RoleID)
    return role


def get_parentmenu():
    role = getrole()
    menuRole = str(role.Menus).split(',')
    dt = Menu.query.filter(Menu.ID.in_(menuRole)).all()
    list = []
    for item in dt:
        if item.ParentPos not in list:
            list.append(item.ParentPos)
    # print(list)
    dt = Menu.query.filter(db.and_(Menu.Position.in_(list), Menu.ParentPos == 10000)).order_by(Menu.Position).all()
    # print(dt)

    return dt

    # return Menu.query.filter(db.and_(MenuRole.RoleID == current_user.RoleID, Menu.ParentPos == 10000)).join(
    #     MenuRole, Menu.ID == MenuRole.MenuID).all()


def get_var(pos):
    role = getrole()
    menuRole = str(role.Menus).split(',')
    dt = Menu.query.filter(db.and_(Menu.ID.in_(menuRole)), Menu.ParentPos == int(pos)).order_by(Menu.Position).all()
    return dt
    # return Menu.query.filter(db.and_(MenuRole.RoleID == current_user.RoleID, Menu.ParentPos == int(pos))).outerjoin(
    #     MenuRole, Menu.ID == MenuRole.MenuID).all()


# def current_time():
#     dt = datetime.now().strftime('%Y-%m-%d %H:%M')
#     # dt=datetime.now()
#     # print(dt)
#     return dt

def get_sbdowndata():
    data = db.session.query(db.func.count(machinesstate.id).label("count")).filter(
        db.and_(machinesstate.sj >= (datetime.now() + timedelta(days=-2)).strftime("%Y-%m-%d"),
                machinesstate.zt != "下载完成")).first()
    return data.count


def get_sumlistbumen(bumen, jifen):
    bm = ''
    jf = 0
    if bm != bumen:
        bm = bumen
        jf = 0
    else:
        jf = jf + jifen

    return bumen


app.add_template_global(get_parentmenu, 'get_parentmenu')
app.add_template_global(get_var, 'get_varmenu')
app.add_template_global(get_sbdowndata, 'sbcount')
app.add_template_global(get_sumlistbumen, 'get_bmlist')
