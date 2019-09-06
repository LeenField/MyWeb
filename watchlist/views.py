from watchlist.models import User, Movie
from flask import Flask, render_template, url_for, flash, request, redirect
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
import re
from watchlist import app, db
from urllib.parse import urlencode, quote
import requests

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


