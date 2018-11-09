from flask import Blueprint, render_template, session, redirect, url_for, \
    request, flash, g, jsonify, abort, json
from app.database import db, User, writtenForleave, association, Cat, WrittenforLeaveSign, Audited, Role, Menu, \
    machines, schclass, holidays, cycle, shift, temporaryscheduling, machinesstate, system, Sumlist
from flask_login import login_required, login_user, logout_user, current_user
from app import app
from app.views.forms import changePassword
from datetime import datetime
from flask import jsonify
# from app.leave import leave
import threading

from . import admin


# 用户列表
@admin.route('/users')
# @admin.route('/users?<int:page>', methods=['GET', 'POST'])
@login_required
def getuser(page=1):
    page = request.args.get('page')
    dept = request.args.get('dept')
    custname = request.args.get('custname')
    qx = request.args.get('role')
    print(dept)
    sql = ""
    if page != None:
        page = int(page)

    if dept != "all":
        try:
            sql = " AssociationID=" + dept + " and "
        except TypeError:
            pass
    if qx != "all":
        try:
            sql = sql + " RoleID=" + qx + " and "
        except TypeError:
            pass
    if custname != "":
        try:
            sql = sql + "  EnrollNumber ='" + custname + "' or " + sql + "  LoginName='" + custname + "' or " + sql + "  UserName='" + custname + "' and";
        except TypeError:
            pass
    if sql != "":
        sql = sql.strip()
        sql = sql[:-3]
    # sql = "select * from d_user " + sql
    print(sql)
    users = User.query.filter(sql).order_by(User.userid).paginate(page, per_page=10, error_out=False)
    # users=db.session.execute(db.text(sql).paginate(page, per_page=10, error_out=False))
    # if (custname != "" and dept != "all"):
    #
    #     users = User.query.filter(db.or_(db.and_(User.DepID == dept, User.EnrollNumber == custname),
    #                                      db.and_(User.DepID == dept, User.username == custname),
    #                                      db.and_(User.DepID == dept, User.truename == custname))).order_by(
    #         User.DepID.desc(), User.userid.desc()).paginate(page,
    #                                                         per_page=10,
    #                                                         error_out=False)
    # elif (custname != "" and dept == "all"):
    #     users = User.query.filter(db.or_(User.EnrollNumber == custname,
    #                                      User.username == custname,
    #                                      User.truename == custname)).order_by(
    #         User.DepID.desc(), User.userid.desc()).paginate(page,
    #                                                         per_page=10,
    #                                                         error_out=False)
    #     # elif(qx!="all"):
    #     #     users=db.session.query(db.text("select * from  d_user  ")).paginate(page,
    #     #                                                         per_page=10,
    #     #                                                         error_out=False)
    #     #     users=db.session.ex
    #     # users = User.query.filter(db.or_(User.EnrollNumber == custname,
    #     #                                  User.username == custname,
    #     #                                  User.truename == custname)).order_by(
    #     #     User.DepID.desc(), User.userid.desc()).paginate(page,
    #     #                                                     per_page=10,
    #     #                                                     error_out=False)
    # else:
    #     users = User.query.filter(User.DepID == dept).order_by(User.DepID.desc(), User.userid.desc()).paginate(page,
    #                                                                                                            per_page=10,
    #                                                                                                            error_out=False)
    #
    # users = User.query.order_by(User.DepID.desc(), User.userid.desc()).paginate(page, per_page=10, error_out=False)

    return render_template("t-users.html", users=users, Dept=association.query.all(), roles=Role.query.all())


# 增加用户
@admin.route('/users-add', methods=['GET', 'POST'])
@login_required
def adduser():
    depts = association.query.all()
    roles = Role.query.all()
    shifts = shift.query.all()
    cycles = cycle.query.all()
    print('1')
    if request.method == "POST":
        print('2')
        username = request.form['username']
        truename = request.form['truename']
        EnrollNumber = request.form['EnrollNumber']
        password = '000000'
        deptid = request.form['dept']
        roleid = request.form['role']
        shiftid = request.form['shift']
        cycleid = request.form['cycle']
        startdate = request.form['startdate']
        db.session.add(User(username, truename, password, deptid, roleid, shiftid, cycleid, startdate, EnrollNumber))

        db.session.commit()
        flash('添加成功')
        print('2')
        return redirect(url_for('.getuser'))

    return render_template("t-users-add.html", depts=depts, roles=roles, shifts=shifts, cycles=cycles)


# 修改用户资料
@admin.route('/users-edit/<id>', methods=['GET', 'POST'])
@login_required
def edituser(id):
    dataview = User.query.get(id)
    # print(dataview.deps.DepName)
    depts = association.query.all()
    roles = Role.query.all()
    shifts = shift.query.all()
    cycles = cycle.query.all()
    if request.method == 'POST':
        print("sssss")
        dataview.username = request.form['username']
        dataview.truename = request.form['truename']
        dataview.EnrollNumber = request.form['EnrollNumber']
        dataview.DepID = request.form['dept']
        dataview.RoleID = request.form['role']
        dataview.ShiftID = request.form['shift']
        dataview.CycleID = request.form['cycle']
        dataview.StartDate = request.form['startdate']
        db.session.add(dataview)
        db.session.commit()
        flash('更新成功')
        return redirect(url_for('.getuser'))
    return render_template("t-users-edit.html", dataview=dataview, depts=depts, roles=roles, shifts=shifts,
                           cycles=cycles)


# 删除用户
@admin.route('/users-del/<id>', methods=['GET', 'POST'])
@login_required
def userdel(id):
    dataview = User.query.get(int(id))
    db.session.delete(dataview)
    db.session.commit()
    flash("删除成功！")
    return redirect(url_for('.getuser'))


# 角色设置----------------------------
@admin.route('/role/<page>', methods=['GET', 'POST'])
@admin.route('/role', methods=['GET', 'POST'])
@login_required
def role(page=1):
    return render_template("t-role.html", leaves=Role.query.order_by(Role.ID).paginate(
        page, per_page=10, error_out=False))


# 修改权限
@admin.route('/role-edit/<int:id>', methods=['GET', 'POST'])
@login_required
def editrole(id):
    dataview = Role.query.get(id)
    menu = Menu.query.all()

    if request.method == 'POST':
        dataview.RoleName = request.form['rolename']
        items = request.form.getlist('cc')
        st = ','.join(items)
        dataview.Menus = st
        db.session.add(dataview)
        db.session.commit()
        return redirect(url_for('.role'))

    return render_template("t-role-edit.html", dataview=dataview, pmenu=menu)


# 设置上传时间
@admin.route('/setrole', methods=['GET', 'POST'])
@login_required
def roleset():
    dataview = system.query.first()
    if request.method == "POST":
        print(request.form["riqi"])
        dataview.updateDate = dataview.updateDate.strftime("%Y-%m-%d") + " " + request.form["riqi"]
        dataview.updatefrequency = request.form['fre']

        db.session.add(dataview)
        db.session.commit()
        flash("修改成功")

    return render_template("t-setParameter.html", dataview=dataview)


# 删除权限
@admin.route('/role-del/<id>', methods=['GET', 'POST'])
@login_required
def roledel(id):
    dataview = writtenForleave.query.get(int(id))
    db.session.delete(dataview)
    db.session.commit()
    flash("删除成功！")
    return redirect(url_for('.role'))


# 部门设置--------------------------------
@admin.route('/dept/<int:page>', methods=['GET', 'POST'])
@admin.route('/dept', methods=['GET', 'POST'])
@login_required
def dept(page=1):
    dept = association.query.order_by(association.DepID).paginate(
        page, per_page=10, error_out=False)
    return render_template("t-dept.html", leaves=dept)


# 增加部门
@admin.route('/dept-add', methods=['GET', 'POST'])
@login_required
def adddept():
    if request.method == 'POST':
        DepName = request.form["deptname"]
        db.session.add(association(DepName))
        db.session.commit()
        return redirect(url_for('.dept'))

    return render_template("t-dept-add.html")


# 修改部门
@admin.route('/dept-edit/<int:id>', methods=['GET', 'POST'])
@login_required
def editdept(id):
    dataview = association.query.get(int(id))
    if request.method == 'POST':
        dataview.DepName = request.form["deptname"]
        db.session.add(dataview)
        db.session.commit()
        flash('更新成功')
        return redirect(url_for('.dept'))

    return render_template("t-dept-edit.html", dataview=dataview)


# 删除部门
@admin.route('/dept-del/<id>', methods=['GET', 'POST'])
@login_required
def deldept(id):
    dataview = association.query.get(int(id))
    db.session.delete(dataview)
    db.session.commit()
    flash("删除成功！")
    return redirect(url_for('.dept'))


# 时段设置
@admin.route('/shiftwork/<int:page>', methods=['GET', 'POST'])
@admin.route('/shiftwork', methods=['GET', 'POST'])
@login_required
def shiftwork(page=1):
    dataview = schclass.query.paginate(
        page, per_page=10, error_out=False)
    return render_template("t-shiftwork.html", dataview=dataview)


# 主机列表
@admin.route('/serverhost/<int:page>', methods=['GET', 'POST'])
@admin.route('/serverhost', methods=['GET', 'POST'])
@login_required
def serverhost(page=1):
    dataview = machines.query.order_by(machines.ID.desc()).paginate(
        page, per_page=10, error_out=False)
    return render_template("t-serverhost.html", dataview=dataview)


# 主机列表add
@admin.route('/serverhost-add', methods=['GET', 'POST'])
@login_required
def addserverhost():
    if request.method == "POST":
        MachineAlias = request.form['MachineAlias']
        IP = request.form['IP']
        Port = request.form['Port']
        Baudrate = request.form['Baudrate']
        MachineNumber = request.form['MachineNumber']
        EnterOrOut = request.form['EnterOrOut']
        db.session.add(machines(MachineAlias, IP, Port, Baudrate, MachineNumber, EnterOrOut))
        db.session.commit()
        return redirect(url_for('.serverhost'))

    return render_template("t-serverhost-add.html")


# 主机列表edit
@admin.route('/serverhost-edit/<int:id>', methods=['GET', 'POST'])
@login_required
def editserverhost(id):
    dataview = machines.query.get(int(id))
    if request.method == 'POST':
        dataview.MachineAlias = request.form['MachineAlias']
        dataview.IP = request.form['IP']
        dataview.Port = request.form['Port']
        dataview.Baudrate = request.form['Baudrate']
        dataview.MachineNumber = request.form['MachineNumber']
        dataview.EnterOrOut = request.form['EnterOrOut']
        db.session.add(dataview)
        db.session.commit()
        return redirect(url_for('.serverhost'))
    return render_template("t-serverhost-edit.html", dataview=dataview)


# 删除主机
@admin.route('/serverhost-del/<id>', methods=['GET', 'POST'])
@login_required
def delserverhost(id):
    dataview = machines.query.get(int(id))
    db.session.delete(dataview)
    db.session.commit()
    flash("删除成功！")
    return redirect(url_for('.serverhost'))


# 主机状态列表
@admin.route('/machinesstate/<int:page>', methods=['GET', 'POST'])
@admin.route('/machinesstate', methods=['GET', 'POST'])
@login_required
def getmachinesstate(page=1):
    dataview = machinesstate.query.order_by(machinesstate.id.desc()).paginate(
        page, per_page=10, error_out=False)
    return render_template("t-machinesstate.html", dataview=dataview)


# 数据导入
@admin.route('/importdata', methods=['GET', 'POST'])
@login_required
def importdata():
    list = association.query.all()
    dataview = []
    for item in list:
        items = []
        sql = "d_association.AssociationID=" + str(item.DepID)
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

    return render_template("t-importdata.html", list=dataview, Dept=association.query.all(), user=User.query.all(),
                           roles=Role.query.all(), sttime=datetime.now().strftime('%Y-%m-01'),
                           edtime=datetime.now().strftime('%Y-%m-%d'))  # 节日设置


@admin.route('/holidays/<int:page>', methods=['GET', 'POST'])
@admin.route('/holidays', methods=['GET', 'POST'])
@login_required
def festival(page=1):
    dataview = holidays.query.order_by(holidays.HOLIDAYID.desc()).paginate(page, per_page=10, error_out=False)
    return render_template("t-holidays.html", dataview=dataview)


# 删除节日设置
@admin.route('/holidays-del/<id>', methods=['GET', 'POST'])
@login_required
def delholidays(id):
    dataview = holidays.query.get(int(id))
    db.session.delete(dataview)
    db.session.commit()
    flash("删除成功！")
    return redirect(url_for('.festival'))


# 增加节日设置
@admin.route('/holidays-add', methods=['GET', 'POST'])
@login_required
def addholidays():
    if request.method == 'POST':
        HOLIDAYNAME = request.form["HOLIDAYNAME"]
        STARTTIME = request.form["startdate"]
        DURATION = request.form["DURATION"]
        CatID = request.form["CatID"]
        db.session.add(holidays(HOLIDAYNAME, STARTTIME, DURATION, CatID))
        db.session.commit()
        return redirect(url_for('.festival'))
    return render_template("t-holidays-add.html")


# 修改节日设置
@admin.route('/holidays-edit/<int:id>', methods=['GET', 'POST'])
@login_required
def editholidays(id):
    dataview = holidays.query.get(int(id))
    if request.method == 'POST':
        dataview.HOLIDAYNAME = request.form["HOLIDAYNAME"]
        dataview.STARTTIME = request.form["startdate"]
        dataview.DURATION = request.form["DURATION"]
        dataview.CatID = request.form["CatID"]
        db.session.add(dataview)
        db.session.commit()
        flash('更新成功')
        return redirect(url_for('.festival'))

    return render_template("t-holidays-edit.html", dataview=dataview)


# 循环规则设置
@admin.route('/cycle')
@login_required
def getcycle():
    return render_template("t-cycle.html", dataview=cycle.query.all())


# del规则设置
@admin.route('/cycle-del/<id>', methods=['GET', 'POST'])
@login_required
def delcycle(id):
    dataview = cycle.query.get(int(id))
    db.session.delete(dataview)
    db.session.commit()
    flash("删除成功！")
    return redirect(url_for('.getcycle'))


# 循环规则添加
@admin.route('/cycle-add', methods=['GET', 'POST'])
@login_required
def addcycle():
    if request.method == 'POST':
        sn = request.form['Sname']
        days = request.form['days']
        cyclevs = request.form.getlist("cycles")
        cyclevalues = ",".join(cyclevs)
        db.session.add(cycle(sn, days, cyclevalues))
        db.session.commit()
        return redirect(url_for('.getcycle'))
    return render_template("t-cycle-add.html")


# 循环规则edit
@admin.route('/cycle-edit/<id>', methods=['GET', 'POST'])
@login_required
def editcycle(id):
    dataview = cycle.query.get(int(id))
    if request.method == 'POST':
        dataview.Sname = request.form['Sname']
        dataview.days = request.form['days']
        cyclevs = request.form.getlist("cycles")
        dataview.cyclevalue = ",".join(cyclevs)
        print(dataview.cyclevalue)
        db.session.add(dataview)
        db.session.commit()
        return redirect(url_for('.getcycle'))
    return render_template("t-cycle-edit.html", dataview=dataview)


# 临时排班
@admin.route('/tempschedule/<int:page>', methods=['GET', 'POST'])
@admin.route('/tempschedule', methods=['GET', 'POST'])
@login_required
def tempschedule(page=1):
    return render_template('t-tempschedule.html',
                           dataview=temporaryscheduling.query.paginate(page, per_page=10, error_out=False))


# del临时排班
@admin.route('/tempschedule-del/<id>', methods=['GET', 'POST'])
@login_required
def deltempschedule(id):
    dataview = temporaryscheduling.query.get(int(id))
    db.session.delete(dataview)
    db.session.commit()
    flash("删除成功！")
    return redirect(url_for('.tempschedule'))


# 临时排班添加
@admin.route('/tempschedule-add', methods=['GET', 'POST'])
@login_required
def addtempschedule():
    if request.method == 'POST':
        dept = request.form['depts']
        UserID = request.form['user']
        STARTTIME = request.form['startdate']
        DURATION = request.form["days"]

        cyclevs = request.form.getlist("cycles")
        WorkStatus = ",".join(cyclevs)
        db.session.add(temporaryscheduling(UserID, dept, STARTTIME, DURATION, WorkStatus))
        db.session.commit()
        return redirect(url_for('.tempschedule'))
    return render_template("t-tempschedule-add.html", depts=association.query.all(), users=User.query.all())


# 修改临时排班
@admin.route('/tempschedule-edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edittempschedule(id):
    dataview = temporaryscheduling.query.get(int(id))
    if request.method == 'POST':
        dataview.AssociationID = request.form["depts"]
        dataview.UserID = request.form['user']
        dataview.STARTTIME = request.form["startdate"]
        dataview.DURATION = request.form["days"]
        cyclevs = request.form.getlist("cycles")
        dataview.WorkStatus = ",".join(cyclevs)
        db.session.add(dataview)
        db.session.commit()
        flash('更新成功')
        return redirect(url_for('.tempschedule'))

    return render_template("t-tempschedule-edit.html", depts=association.query.all(), dataview=dataview)


# 班次设置列表
@admin.route('/shift')
@login_required
def get_shift():
    return render_template('/t-shift.html', dataview=shift.query.all(), schclass=schclass.query.all())


# 修改班次设置
@admin.route('/shift-edit/<int:id>', methods=['GET', 'POST'])
@login_required
def editshift(id):
    dataview = shift.query.get(int(id))
    if request.method == "POST":
        dataview.shiftname = request.form['shiftname']
        schclasslist = request.form.getlist('cycles')
        dataview.SchClassList = ",".join(schclasslist)
        db.session.add(dataview)
        db.session.commit()
        return redirect(url_for('.get_shift'))

    return render_template('/t-shift-edit.html', dataview=dataview, schclass=schclass.query.all())


# 增加班次设置
@admin.route('/shift-add', methods=['GET', 'POST'])
@login_required
def addshift():
    if request.method == "POST":
        st = request.form['shiftname']
        schclasslist = request.form.getlist('cycles')
        SchClassList = ",".join(schclasslist)
        db.session.add(shift(st, SchClassList))
        db.session.commit()
        return redirect(url_for('.get_shift'))

    return render_template('/t-shift-add.html', schclass=schclass.query.all())


# 删除班次设置
@admin.route('/shift-del/<id>', methods=['GET', 'POST'])
@login_required
def delshift(id):
    dataview = shift.query.get(int(id))
    db.session.delete(dataview)
    db.session.commit()
    flash("删除成功！")
    return redirect(url_for('.get_shift'))


# 自动上传
@admin.route('/auto', methods=['GET', 'POST'])
@login_required
def autodata():
    threading.Thread(target=statisticsData).start()
import subprocess
def statisticsData():
    print('3')
    subprocess.call('E:\\CodeProject\\养老保险金系统\\PensionInsurance\\WinAtt\\bin\\Debug\\WinAtt.exe')
