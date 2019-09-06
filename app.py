from flask import Flask, render_template, url_for, flash, request, redirect
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, BooleanField, StringField, validators
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from urllib.parse import urlencode, quote
import click
import re
import os
import sys

app = Flask(__name__)

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'   浏览器签名密钥
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + \
    os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)


class User(db.Model, UserMixin):  # 表名将会是 user（自动生成，小写处理） 继承Flask-login 的UserMixin类
    id = db.Column(db.Integer, primary_key=True)  # 主键
    # name = db.Column(db.String(20))  # 名字
    username = db.Column(db.String(20))  # 用户名
    password_hash = db.Column(db.String(128))  # 密码散列值

    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password)  # 将生成的密码保持到对应字段

    def validate_password(self, password):  # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)  # 返回布尔值

class Movie(db.Model):  # 表名将会是 movie
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4))  # 电影年份


login_manager = LoginManager(app)  # 实例化扩展类
login_manager.login_view = "login" # 保护视图的 登录界面跳转
login_manager.login_message = "请登录之后再执行该操作"

# 用户加载回调函数
@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    # user = current_user
    return user  # 返回用户对象


@app.route('/register', methods=['GET', 'POST'])
def register():
    # db.drop_all()
    # db.create_all()       # 只有在数据库模型修改时使用
    if request.method == 'POST':
        user_name = request.form['username']
        passport = request.form['passport']
        passport_check = request.form['passport-check']
        name_pattern = re.compile(r"\w{4,8}")    # 逗号后面不需要空格
        pass_pattern = re.compile(r".{6,20}")
        if passport_check != passport:
            flash("两次输入密码不匹配")
        elif name_pattern.match(user_name) == None:
            flash("用户名为4~8位数字字母")
        elif pass_pattern.match(passport) == None:
            flash("密码为6~20位")
        elif User.query.filter_by(username="user_name").all():
            flash("该用户名已存在")
        else:
            temp_user = User(username=user_name)
            temp_user.set_password(passport)

            db.session.add(temp_user)
            db.session.commit()
            flash("注册成功")
            # return redirect(url_for('login'))
    return render_template("SignIn.html")

# 登出视图
@app.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    flash('再见')
    logout_user()  # 登出用户
    return redirect(url_for('index'))  # 重定向回首页

# 删除视图
@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required  # 登录保护
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))

@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        movie.title = request.form['title']
        movie.year = request.form['year']
        db.session.commit()
        flash("编辑成功")
        return redirect(url_for("index"))

    return render_template("edit.html", movie = movie)

# @app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
# @login_required
# def edit(movie_id):
#     movie = Movie.query.get_or_404(movie_id)

#     if request.method == 'POST':  # 处理编辑表单的提交请求
#         title = request.form['title']
#         year = request.form['year']

#         if not title or not year or len(year) > 4 or len(title) > 60:
#             flash('Invalid input.')
#             return redirect(url_for('edit', movie_id=movie_id))  # 重定向回对应的编辑页面

#         movie.title = title  # 更新标题
#         movie.year = year  # 更新年份
#         db.session.commit()  # 提交数据库会话
#         flash('Item updated.')
#         return redirect(url_for('index'))  # 重定向回主页

#     return render_template('edit.html', movie=movie)  # 传入被编辑的电影记录

# 登录视图
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form['username']
        passport = request.form['passport']
        user = User.query.filter_by(username=user_name).first()
        if user == None:
            flash("该用户不存在")
        elif user.validate_password(passport) == False:
            flash("密码不匹配")
        else:
            login_user(user)
            flash("登陆成功")
            return redirect(url_for("index"))
    return render_template("login.html")

@app.route('/', methods=["GET", "POST"])
def index():
    # name = User.query.first()
    query_key = {'city': "福州".encode("utf-8"), 'key': '7b4a753f47383e4b65594b2f96ca20e3'.encode("utf-8")}
    # 注意城市名的编码问题
    weather = requests.get("http://apis.juhe.cn/simpleWeather/query", urlencode(query_key))
    # weather = requests.get("http://apis.juhe.cn/simpleWeather/query/get?city=%E7%A6%8F%E5%B7%9E&key=7b4a753f47383e4b65594b2f96ca20e3")
    print(weather.text)
    data = weather.json()
    temperature, info = None, None
    if data['reason'] == "查询成功!":
        temperature = data['result']['realtime']['temperature']
        info = data['result']['realtime']['info']
    if request.method == "POST":
        title = request.form["title"]
        year  = request.form["year"]
        movie = Movie(title = title, year = year)
        db.session.add(movie)
        db.session.commit()
        flash("添加电影成功")
    movies = Movie.query.all()
    return render_template('index.html', movies=movies, temperature = temperature, info = info)


@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    # user = User.query.first()
    if request.method == 'POST':
        if not current_user.is_authenticated:  # 如果当前用户未认证
            return redirect(url_for('index'))  # 重定向到主页
    return render_template('404.html'), 404  # 返回模板和状态码

# 对于多个模板都有引用的 变量 例如 user 需要处理
@app.context_processor
def inject_user():  # 函数名可以随意修改
    user = User.query.first()
    return dict(user=user)  # 需要返回字典，等同于return {'user': user}
