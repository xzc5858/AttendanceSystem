import os
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE_URI ="mysql+pymysql://root:123456@127.0.0.1:3306/attendance?charset=utf8"
# DATABASE_URI ="mssql+pyodbc://root:123456@localhost:1433/att?driver=SQL+Server+Native+Client+11.0"
# Flask-Security config
# SECURITY_URL_PREFIX = "/admin"
# SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
# SECURITY_PASSWORD_SALT = "ATGUOHAELKiubahiughaerGOJAEGj"
#
# # Flask-Security URLs, overridden because they don't put a / at the end
# SECURITY_LOGIN_URL = "/login/"
# SECURITY_LOGOUT_URL = "/logout/"
# SECURITY_REGISTER_URL = "/register/"
#
# SECURITY_POST_LOGIN_VIEW = "/admin/"
# SECURITY_POST_LOGOUT_VIEW = "/admin/"
# SECURITY_POST_REGISTER_VIEW = "/admin/"
#
# # Flask-Security features
# SECURITY_REGISTERABLE = True
# SECURITY_SEND_REGISTER_EMAIL = False
# SQLALCHEMY_TRACK_MODIFICATIONS = False

del os