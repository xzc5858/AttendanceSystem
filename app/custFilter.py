# from app import app
from app.database import User, writtenForleave, association, Cat, Role, Menu
# from flask import Markup, render_template_string


def get_user(id):
    user = User.query.filter_by(userid=id).first()
    if not user:
        return ''
    return user.truename


def get_ParentPos(url):
    st = url.split('?')
    st = st[0].split('-')
    ms = Menu.query.filter_by(url=st[0]).first()
    if not ms:
        return ''
    return ms.ParentPos


def get_MenuID(url):
    st = url.split('?')
    st = st[0].split('-')
    ms = Menu.query.filter_by(url=st[0]).first()
    if not ms:
        return ''
    return ms.ID


def sendzt(value):
    role = Role.query.filter_by(RoleChar=value).first()
    tt = ""
    if value == "0":
        tt = "未发送"
    elif value == "1":
        tt = "已完成"
    else:
        tt = role.RoleName + "处理中"
    return tt


def Category(id):
    cat = Cat.query.get(id)
    if not cat:
        return ""
    return cat.catname


def jieguo(Agree):
    tt = "未完成"
    if (Agree == 1):
        tt = "通过"
    elif (Agree == 0):
        tt = "未通过"
    else:
        tt = "未完成"
    return tt


def getOtheruser(id):
    leave = writtenForleave.query.get(id)
    items = leave.otherUser.split(',')
    return items


def jifen(item):
    value = 20.0
    if item.迟到早退 >= 3:
        value = value - (item.迟到早退 * 0.5) - (item.迟到早退) / 3
    else:
        value = value - item.迟到早退 * 0.5

    if item.脱岗 >= 3:
        value = value - item.脱岗 * 0.5 - (item.脱岗) / 3
    else:
        value = value - item.脱岗 * 0.5

    value = value - item.未按指纹 * 1.5

    if item.公差 > 2:
        value = value - item.公差 * 0.25

    if item.病假 < 6:
        value = value - item.病假 * 0.5
    else:
        value = value - item.病假 * 0.5 - item.病假 / 3.0

    if item.事假 < 6:
        value = value - item.事假 * 0.75
    else:
        value = value - item.事假 * 0.75 - item.事假 / 3.0

    if value < 0:
        value = 0

    return round(value, 1)


def jintie(item, jf):
    value = jf
    ge = value % 10
    value = value - ge
    if ge < 3:
        ge = 0
    elif ge >= 3 and ge <= 7:
        ge = 5
    elif ge > 7:
        ge = 10
    value = value + ge
    # print(ge)
    return value


# 注册自定义过滤器
def register_filters(app):
    app.jinja_env.filters['getuser'] = get_user
    app.jinja_env.filters["getParentPos"] = get_ParentPos
    app.jinja_env.filters["zt"] = sendzt
    app.jinja_env.filters["jg"] = jieguo
    app.jinja_env.filters['getcat'] = Category
    app.jinja_env.filters['getmenuid'] = get_MenuID
    app.jinja_env.filters['sele'] = getOtheruser
    app.jinja_env.filters['jifen'] = jifen
    app.jinja_env.filters['jintie'] = jintie
