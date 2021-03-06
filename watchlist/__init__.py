from flask import Flask, render_template, url_for, flash, request, redirect
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
import requests
from flask_bootstrap import Bootstrap
from urllib.parse import urlencode, quote
from flask_admin import Admin, AdminIndexView

import os
import sys

app = Flask(__name__)
bootstrap = Bootstrap(app)
admin = Admin(app, index_view = AdminIndexView(
    name=u'博客后台管理', 
    template = 'AdminIndex.html')
    )

# WIN = sys.platform.startswith('win')
# if WIN:  # 如果是 Windows 系统，使用三个斜线
#     prefix = 'sqlite:///'
# else:  # 否则使用四个斜线
#     prefix = 'sqlite:////'

app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'   浏览器签名密钥
# app.config['SQLALCHEMY_DATABASE_URI'] = prefix + \
#     os.path.join(app.root_path, 'data.db')

# 数据库信息
host = 'verygoodstyle.cn'
port = '3306'
database = 'MyCMS?charset=utf8mb4'
username = 'root'
password = '22350622SUN'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@127.0.0.1:3306/watch_list_2'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:22350622SUN@cdb-gfobj32i.cd.tencentcdb.com:10034/MyCMS?charset=utf8mb4'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)

login_manager = LoginManager(app)  # 实例化扩展类
login_manager.login_view = "login" # 保护视图的 登录界面跳转
login_manager.login_message = "请登录之后再执行该操作"


# 用户加载回调函数
@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    #  函数中导入类模型
    from watchlist.models import User             
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    # user = current_user
    return user  # 返回用户对象

from watchlist.models import User, Article, Tag

# 对于多个模板都有引用的 变量 例如 user 需要处理
@app.context_processor
def inject_user():  # 函数名可以随意修改
    from watchlist.models import User             
    user = User.query.first()

    query_key = {'city': "厦门".encode("utf-8"), 'key': '7b4a753f47383e4b65594b2f96ca20e3'.encode("utf-8")}
    # 注意城市名的编码问题
    weather = requests.get("http://apis.juhe.cn/simpleWeather/query", urlencode(query_key))
    # weather = requests.get("http://apis.juhe.cn/simpleWeather/query/get?city=%E7%A6%8F%E5%B7%9E&key=7b4a753f47383e4b65594b2f96ca20e3")
    candidate_tags = Tag.query.all()

    print(weather.text)
    data = weather.json()
    temperature, info = None, None
    if data['reason'] == "查询成功!":
        temperature = data['result']['realtime']['temperature']
        info = data['result']['realtime']['info']

    return dict(user=user, temperature = temperature, \
        info = info, candidate_tags=candidate_tags)  # 需要返回字典，等同于return {'user': user}

from watchlist import views, errors, adminViews