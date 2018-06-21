# from datetime import datetime
from flask import Flask, session, g, render_template
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = 'some_secret'  # Change this!

# 初始化flask_login
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'view.login'
login_manager.init_app(app)
login_manager.login_message = u"账号可以输入用户名、身份证、手机号、考勤号"
from app.views import view

app.register_blueprint(view.mod)

from app.admin import view

app.register_blueprint(view.admin)

from app.database import User

# 导入自定义过滤器
from app.custFilter import register_filters

register_filters(app)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.before_request
def load_current_user():
    print("进入页面")


@login_manager.user_loader  # 使用user_loader装饰器的回调函数非常重要，他将决定 user 对象是否在登录状态
def user_loader(userid):  # 这个id参数的值是在 login_user(user)中传入的 user 的 id 属性
    user = User.query.get(int(userid))
    # if not user:
    #     print("登陆用户: " + user.truename)
    return user


@login_manager.request_loader
def request_loader(request):
    return
