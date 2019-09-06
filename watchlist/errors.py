from watchlist import app, db
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from flask import Flask, render_template, url_for, flash, request, redirect

@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    # user = User.query.first()
    if request.method == 'POST':
        if not current_user.is_authenticated:  # 如果当前用户未认证
            return redirect(url_for('index'))  # 重定向到主页
    return render_template('errors/404.html'), 404  # 返回模板和状态码
