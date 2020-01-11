from watchlist.models import User, Movie, PostForm, Article, Tag, Article_Has_Tag
from flask import Flask, render_template, url_for, flash, request, redirect, Response, jsonify
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
import re, os, datetime
from flask_wtf.csrf import CSRFProtect
from watchlist import app, db, admin
from werkzeug.routing import  BaseConverter
csrf = CSRFProtect()   # 惰性加载
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_babelex import Babel

from werkzeug.routing import BaseConverter


babel = Babel(app)

app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'



class AdminView(BaseView):
    @login_required               # 提示需要登录
    @expose('/')
    def index(self):
        return self.render('AdminIndex.html')

class BaseModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class UserView(BaseModelView):
    # 隐藏用户名密码
    column_exclude_list = ('password_hash', ) 

# 在 Flask-Admin 增加数据库模型视图

# if __name__ == "__main__":
# admin.add_view(AdminView(name=u'Hello'))
    # if current_user.username == "XieCK":
# admin.add_view(UserView(User, db.session, name=u'信息', category=u'用户'))      # 用户模型
admin.add_view(UserView(User, db.session, name=u'信息'))      # 用户模型
admin.add_view(BaseModelView(Article, db.session))   # 文章模型
admin.add_view(BaseModelView(Tag, db.session))       # 标签模型
admin.add_view(BaseModelView(Article_Has_Tag, db.session))   # 文章X标签模型