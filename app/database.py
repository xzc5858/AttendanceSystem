from flask_sqlalchemy import SQLAlchemy
from app import app
from datetime import datetime

# 初始化数据库
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['DATABASE_URI']
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


# 用户
class User(db.Model):
    __tablename__ = 'd_user'

    userid = db.Column('UserID', db.Integer, primary_key=True)
    username = db.Column('LoginName', db.String(200))
    truename = db.Column('UserName', db.String(200))
    password = db.Column('UserPassword', db.String(200))
    active = db.Column('AllowLogin', db.Boolean)
    EnrollNumber = db.Column('EnrollNumber', db.String(200))

    DepID = db.Column('AssociationID', db.Integer, db.ForeignKey('d_association.AssociationID'))
    deps = db.relationship('association', backref=db.backref('d_user'))
    RoleID = db.Column('RoleID', db.Integer, db.ForeignKey('d_role.ID'))
    Roles = db.relationship('Role', backref=db.backref('d_role'))
    ShiftID = db.Column(db.Integer)
    CycleID = db.Column(db.Integer)
    StartDate = db.Column(db.Date)

    def __init__(self, username, truename, password, deptid, roleid, ShiftID, CycleID, StartDate, EnrollNumber):
        self.username = username
        self.truename = truename
        self.password = password
        self.DepID = deptid
        self.RoleID = roleid
        self.active = True
        self.ShiftID = ShiftID
        self.CycleID = CycleID
        self.StartDate = StartDate
        self.EnrollNumber = EnrollNumber

    def get_id(self):
        return self.userid

    @property
    def is_active(self):
        return self.active

    def is_authenticated(self):
        return True


# 请假表
class writtenForleave(db.Model):
    __tablename__ = 'd_writtenForleave'

    LeaveID = db.Column('LeaveID', db.Integer, primary_key=True)
    DepID = db.Column('associationID', db.Integer)

    LeaveUserId = db.Column('userid', db.Integer, db.ForeignKey('d_user.UserID'))
    LeaveUsers = db.relationship(User, backref=db.backref('d_writtenForleave'))
    UserName = db.Column('UserName', db.String(60))
    LoginName = db.Column('LoginName', db.String(60))
    EnrollNumber = db.Column('enrollnumber', db.Integer)
    StartTime = db.Column('starttime', db.DateTime)
    duration = db.Column('duration', db.Integer)
    EndTime = db.Column('EndTime', db.DateTime)
    Wtext = db.Column('Wtext', db.String(5000))
    ifComplete = db.Column('ifComplete', db.Boolean)
    Agree = db.Column('Agree', db.Boolean)
    WorkStatus = db.Column('WorkStatus', db.Integer)
    # Category = db.Column('Category', db.Integer)
    Category = db.Column('CategoryID', db.Integer, db.ForeignKey('d_cat.id'))
    Categorys = db.relationship('Cat', backref=db.backref('d_writtenForleave'))

    SubUserID = db.Column('SubUserID', db.Integer)
    days = db.Column('days', db.Integer)
    otherUser = db.Column('otherUser', db.String(100))
    DayStart = db.Column('DayStart', db.Integer)
    WriteUserID = db.Column('WriteUserID', db.Integer)
    Send = db.Column('Send', db.String(1))
    ifTolerance = db.Column('ifTolerance', db.Boolean)

    # 定制显示的格式
    def __repr__(self):
        return '<writtenForleave %r>' % self.LeaveUserId

    def __init__(self, DepID, LeaveUserId, UserName, LoginName, EnrollNumber, StartTime, EndTime, SubUser, otherUser,
                 Category,
                 WriteUserID, Wtext):
        self.DepID = DepID
        self.LeaveUserId = LeaveUserId
        self.UserName = UserName
        self.LoginName = LoginName
        self.EnrollNumber = EnrollNumber
        self.StartTime =StartTime
        self.EndTime =EndTime
        self.SubUserID = SubUser
        self.otherUser = otherUser
        self.Category = Category
        self.ifComplete = False
        self.WriteUserID = WriteUserID
        self.Send = '0'
        self.ifTolerance = 0
        self.DayStart = datetime.now()
        self.Wtext = Wtext


# 请假明细表
class WrittenforLeaveSign(db.Model):
    __tablename__ = "d_WrittenforLeaveSign"
    id = db.Column(db.Integer, primary_key=True)
    LeaveID = db.Column(db.Integer)
    UserID = db.Column(db.Integer)
    Agree = db.Column(db.Boolean)
    riqi=db.Column(db.DateTime)
    Remarks = db.Column(db.String(5000))

    def __init__(self, LeaveID, UserID, Agree, Remarks):
        self.LeaveID = LeaveID
        self.UserID = UserID
        self.Agree = Agree
        self.Remarks = Remarks
        self.riqi=datetime.now()


# 部门表
class association(db.Model):
    __tablename__ = "d_association"
    DepID = db.Column('AssociationID', db.Integer, primary_key=True)
    DepName = db.Column('AssociationName', db.String(200))

    # users = db.relationship('User', backref='dept')
    def __init__(self, depname):
        self.DepName = depname


# 假期类别
class Cat(db.Model):
    __tablename__ = "d_cat"

    id = db.Column("id", db.Integer, primary_key=True)
    catname = db.Column("catname", db.String(50))
    isVacation = db.Column(db.Boolean)

    # writtenForleave=db.relationship('writtenForleave',backref="writtenForleave")


# 权限
class Role(db.Model):
    __tablename__ = 'd_role'

    ID = db.Column(db.Integer, primary_key=True)
    RoleChar = db.Column(db.String(1))
    RoleName = db.Column(db.String(50))
    Menus = db.Column(db.String(100))
    CanSeeData = db.Column(db.Boolean)
    OnlyAssociation = db.Column(db.Boolean)


# 这里设置请假审核的顺序
class Audited(db.Model):
    __tablename__ = "d_audited"
    ID = db.Column(db.Integer, primary_key=True)
    RoleID = db.Column(db.Integer)
    SH1 = db.Column(db.String(100))
    SH2 = db.Column(db.String(100))
    days = db.Column(db.Integer)
    Da = db.Column(db.Boolean)
    days2 = db.Column(db.Integer)
    Da2 = db.Column(db.Boolean)


# 菜单
class Menu(db.Model):
    __tablename__ = "d_menu"
    ID = db.Column(db.Integer, primary_key=True)
    menu = db.Column(db.String(50))
    url = db.Column(db.String(100))
    style = db.Column(db.String(50))
    Position = db.Column(db.Integer)
    ParentPos = db.Column(db.Integer)


# 机器列表
class machines(db.Model):
    __tablename__ = "d_machines"
    ID = db.Column(db.Integer, primary_key=True)
    MachineAlias = db.Column(db.String(50))
    ConnectType = db.Column(db.Integer)
    IP = db.Column(db.String(50))
    SerialPort = db.Column(db.String(1))
    Port = db.Column(db.Integer)
    Baudrate = db.Column(db.Integer)
    MachineNumber = db.Column(db.Integer)
    EnterOrOut = db.Column(db.String(1))

    def __init__(self, mc, ip, port, btl, nm, en):
        self.MachineAlias = mc
        self.ConnectType = 0
        self.IP = ip

        self.Port = port
        self.Baudrate = btl
        self.MachineNumber = nm
        self.EnterOrOut = en


class machinesstate(db.Model):
    __tablename__ = "d_machinesstate"
    id=db.Column(db.Integer, primary_key=True)
    sn = db.Column(db.String(50))
    zt = db.Column(db.String(50))
    sj = db.Column(db.DateTime)


# 统计表
class Sumlist(db.Model):
    __tablename__ = "d_SumList"
    ID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer)
    LeaveID = db.Column(db.Integer)
    Date = db.Column(db.Date)

    def __init__(self, LeaveID, UserID, Date):
        self.LeaveID = LeaveID
        self.UserID = UserID
        self.Date = Date


        # class cycle(db.Model):


# 节假日
class holidays(db.Model):
    __tablename__ = 'd_holidays'
    HOLIDAYID = db.Column(db.Integer, primary_key=True)
    HOLIDAYNAME = db.Column(db.String(20))
    STARTTIME = db.Column(db.DateTime)
    DURATION = db.Column(db.Integer)
    CatID = db.Column(db.Integer)

    def __init__(self, name, time, dur, cat):
        self.HOLIDAYNAME = name
        self.STARTTIME = time
        self.DURATION = dur
        self.CatID = cat


#
# # 这个是员工选择的哪个排班规则 要选择两个规则，一个是循环规则，一个是时间规则
# class employeescheduling(db.Model):
#     __tablename__ = "d_employeescheduling"
#     ESID = db.Column(db.Integer, primary_key=True)
#     # LeaveUserId = db.Column('userid', db.Integer, db.ForeignKey('d_user.UserID'))
#     # LeaveUsers = db.relationship(User, backref=db.backref('d_writtenForleave'))
#     UserID = db.Column(db.Integer, db.ForeignKey('d_user.UserID'))
#     Users = db.relationship(User, backref=db.backref('d_employeescheduling'))
#
#     # ctype = db.Column(db.Integer)
#     ShiftID = db.Column(db.Integer)  # 选择的是哪个时间规则
#     # NumName = db.Column(db.String(20))
#     CycleID = db.Column(db.Integer)  # 选择的是哪个循环规则
#     # RQ = db.Column(db.DateTime)
#     # Days = db.Column(db.Integer)
#     StartDate = db.Column(db.DateTime)
#     # Writable = db.Column(db.Integer)


# 循环规则cycle
class cycle(db.Model):
    __tablename__ = "d_cycle"
    ID = db.Column(db.Integer, primary_key=True)
    Sname = db.Column(db.String(30))
    days = db.Column(db.Integer)
    cyclevalue = db.Column(db.String(100))

    def __init__(self, sn, dys, cy):
        self.Sname = sn
        self.days = dys
        self.cyclevalue = cy


# 班次名称shift
class shift(db.Model):
    __tablename__ = "d_shift"
    ID = db.Column(db.Integer, primary_key=True)
    shiftname = db.Column(db.String(30))
    SchClassList = db.Column(db.String(100))

    # STARTDATE = db.Column(db.DateTime)
    # ENDDATE = db.Column(db.DateTime)
    def __init__(self, sn, sc):
        self.shiftname = sn
        self.SchClassList = sc


# 上下班时间段
class schclass(db.Model):
    __tablename__ = "d_schclass"
    schClassid = db.Column(db.Integer, primary_key=True)
    schName = db.Column(db.String(50))

    StartTime = db.Column(db.DateTime)
    EndTime = db.Column(db.DateTime)

    # LateMinutes = db.Column(db.Integer)
    # EarlyMinutes = db.Column(db.Integer)
    # CheckIn = db.Column(db.String(1))
    # CheckOut = db.Column(db.String(1))

    CheckInTime1 = db.Column(db.DateTime)
    CheckInTime2 = db.Column(db.DateTime)
    CheckOutTime1 = db.Column(db.DateTime)
    CheckOutTime2 = db.Column(db.DateTime)


# # 每个班选择了哪些时间段
# class shiftaddschlist(db.Model):
#     __tablename__ = "d_shiftaddschlist"
#     SID = db.Column(db.Integer, primary_key=True)
#     schClassid = db.Column(db.Integer)
#     NumID = db.Column(db.Integer)
# 临时值班表
class temporaryscheduling(db.Model):
    __tablename__ = "d_temporaryscheduling"
    id = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('d_user.UserID'))
    tempUsers = db.relationship(User, backref=db.backref('d_temporaryscheduling'))

    AssociationID = db.Column(db.Integer, db.ForeignKey('d_association.AssociationID'))
    ass = db.relationship(association, backref=db.backref('d_association'))

    STARTTIME = db.Column(db.Date)
    DURATION = db.Column(db.Integer)
    WorkStatus = db.Column(db.String)

    def __init__(self, user, ass, st, dur, WorkStatus):
        self.UserID = user
        self.AssociationID = ass
        self.STARTTIME = st
        self.DURATION = dur
        self.WorkStatus = WorkStatus


# 导入指纹表
class atttransaction(db.Model):
    __tablename__ = "d_atttransaction"
    id = db.Column(db.Integer, primary_key=True)
    EnrollNumber = db.Column(db.String(50))
    VerifyMethod = db.Column(db.Integer)
    InOutMode = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    WorkCode = db.Column(db.Integer)
    AttState = db.Column(db.Integer)
    Complete = db.Column(db.Integer)
    MachineID = db.Column(db.Integer)


# class temp_generate(db.Model):Model




class system(db.Model):
    __tablename__="d_system"
    id = db.Column(db.Integer, primary_key=True)
    updateDate = db.Column(db.DateTime)
    updatefrequency = db.Column(db.String(3))

# 迟到早退
class chidao(db.Model):
    __tablename__="t_chidaozaotui"
    id = db.Column(db.Integer, primary_key=True)
    date=db.Column(db.DateTime)
    otherdate=db.Column(db.DateTime)
    types=db.Column(db.String(3))
    sjc=db.Column(db.Integer)
    userid = db.Column(db.Integer)
    LeaveID=db.Column(db.Integer)
    schName=db.Column(db.String(50))

    def __init__(self,date,otherdate,types,sjc,leaveid,schname,userid):
        self.date=date
        self.otherdate=otherdate
        self.types=types
        self.sjc=sjc
        self.LeaveID=leaveid
        self.schName=schname
        self.userid=userid

# 应到
class yingdao(db.Model):
    __tablename__ = "t_yingdao"
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    zhuangtai = db.Column(db.Integer)
    riqi = db.Column(db.Date)
    schName=db.Column(db.String(10))
    sttime=db.Column(db.DateTime)
    edtime=db.Column(db.DateTime)

    def __init__(self, id, zt, rq):
        self.userid = id
        self.zhuangtai = zt
        self.riqi = rq


# 实到
class shidao(db.Model):
    __tablename__ = "t_shidao"
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    zhuangtai = db.Column(db.Integer)
    riqi = db.Column(db.Date)
    schName=db.Column(db.String(10))
    sttime=db.Column(db.DateTime)
    edtime=db.Column(db.DateTime)

    def __init__(self, id, zt, rq,sch,st,ed):
        self.userid = id
        self.zhuangtai = zt
        self.riqi = rq
        self.schName=sch
        self.sttime=st
        self.edtime=ed

# 旷工
class kuanggong(db.Model):
    __tablename__ = "t_kuanggong"
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    zhuangtai = db.Column(db.Integer)
    riqi = db.Column(db.Date)
    schName=db.Column(db.String(10))
    sttime=db.Column(db.DateTime)
    edtime=db.Column(db.DateTime)

    def __init__(self, id, zt, rq,sch,st,ed):
        self.userid = id
        self.zhuangtai = zt
        self.riqi = rq
        self.schName=sch
        self.sttime=st
        self.edtime=ed



# 请假
class qingjia(db.Model):
    __tablename__ = "t_qingjia"
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    zhuangtai = db.Column(db.Integer)
    riqi = db.Column(db.Date)
    schName=db.Column(db.String(10))
    sttime=db.Column(db.DateTime)
    edtime=db.Column(db.DateTime)

    def __init__(self, id, zt, rq,sch):
        self.userid = id
        self.zhuangtai = zt
        self.riqi = rq
        self.schName=sch


class tequan(db.Model):
    __tablename__="t_tequan"

    LeaveID = db.Column('LeaveID', db.Integer, primary_key=True)

    DepID = db.Column('associationID', db.Integer,db.ForeignKey('d_association.AssociationID'))
    Depts = db.relationship('association', backref=db.backref('t_tequan'))
    LeaveUserId = db.Column('userid', db.Integer, db.ForeignKey('d_user.UserID'))
    LeaveUsers = db.relationship(User, backref=db.backref('t_tequan'))
    StartTime = db.Column('starttime', db.DateTime)
    EndTime = db.Column('EndTime', db.DateTime)
    Category = db.Column('CategoryID', db.Integer, db.ForeignKey('d_cat.id'))
    Categorys = db.relationship('Cat', backref=db.backref('t_tequan'))
    WriteUserID = db.Column('WriteUserID', db.Integer)


    # # 定制显示的格式
    # def __repr__(self):
    #     return '<writtenForleave %r>' % self.LeaveUserId

    def __init__(self, DepID, UserId, StartTime, EndTime,
                 Category,
                 WriteUserID):
        self.DepID = DepID
        self.LeaveUserId = UserId
        self.StartTime = StartTime
        self.EndTime = EndTime
        self.Category = Category
        self.WriteUserID = WriteUserID


class log(db.Model):
    __tablename__="d_log"

    id=db.Column(db.Integer,primary_key=True)
    user=db.Column(db.Integer)
    data=db.Column(db.String)
    riqi=db.Column(db.DateTime)
    event=db.Column(db.String)
    def __init__(self,userid,data,rq,event):
        self.user=userid
        self.date=data
        self.riqi=rq
        self.event=event











