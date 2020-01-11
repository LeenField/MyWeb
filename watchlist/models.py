from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import relationship, backref
from flask_admin import BaseView
from flask_admin.contrib.sqla import ModelView

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from watchlist import app, db, admin
from wtforms import Form, TextAreaField, StringField, validators, SubmitField, BooleanField
Base = declarative_base()


class PostForm(Form):
    title = StringField('title')
    body = TextAreaField('Body', [validators.Required()])
    # brief = TextAreaField('brief', [validators.Required()])
    # tag_check = []
    # for tag in tags:
    #     tag_check.append(BooleanField(tag.tag_name, [validators.Required()]))

    # submit = SubmitField('保存')
class User(db.Model, UserMixin):  # 默认表名将会是 user（自动生成，小写处理） 继承Flask-login 的UserMixin类
    # 定义表名（复数）
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)  # 主键
    # name = db.Column(db.String(20))  # 名字
    username = db.Column(db.String(20))  # 用户名
    password_hash = db.Column(db.String(128))  # 密码散列值

    articles = relationship("Article", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    

    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password)  # 将生成的密码保持到对应字段

    def validate_password(self, password):  # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)  # 返回布尔值

def _tag_find_or_create(tag):
    tag = Tag.query.filter_by(tag_name=tag).first()
    print(tag)
    if not tag:
        print("Can find Tag~")
        tag = Tag(tag)
        # db.session.add(tag)
        # db.session.flush()
        # db.session.commit()
    return tag

class Article(db.Model):
    __tablename__ = "articles"
    __table_args__ = {'mysql_charset' : 'utf8mb4'}
    # sqlalchemy 自动自增PK
    id_article = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    title = db.Column(db.String(214), nullable=False)
    hits = db.Column(db.Integer, default=0, comment="点击量")
    brief = db.Column(db.String(500), default="", comment="文章简介")
    create_time = db.Column(db.DateTime, server_default=func.now(), comment="创建时间")
    # update_time = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    update_time = db.Column(db.DateTime, server_default=func.now(), comment="更新时间")
    content = db.Column(db.Text, nullable=False, comment="文章内容")
    content_html = db.Column(db.Text, comment="md渲染为HTML")
    # 多对一 子表外键
    user_id = db.Column(db.Integer, ForeignKey('users.id'))
    is_draft = db.Column(db.Boolean, default=False)
    
    comments = relationship("Comment", back_populates="article")

    user = relationship("User", back_populates="articles")
    # "tag" 为 Article_Has_Tag 的属性可以二阶映射, 这里直接Article.tags()得到映射的Tag
    # tags = association_proxy('article_has_tags', "tag", creator=_tag_find_or_create)
    tags = association_proxy('article_has_tags', "tag")
    # association_proxy of "article_has_tags" collection to "tags" attribute
    def updatetime(self):            
         # update time manually
        self.update_time = func.now()
        db.session.commit()
    def increase_hits(self):
        self.hits += 1
        db.session.commit()
class Comment(db.Model):
    __tablename__ = "comments"
    __table_args__ = {'mysql_charset' : 'utf8mb4'}   # 支持表情emoji
    id_comment = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    # 外键
    id_user = db.Column(db.Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="comments")

    id_article = db.Column(db.Integer, ForeignKey('articles.id_article'))
    article = relationship("Article", back_populates="comments")

    content = db.Column(db.String(200), nullable=False, comment="评论内容")
    create_time = db.Column(db.DateTime, default=func.now(), comment="创建评论时间")

class Article_Has_Tag(db.Model):
    __tablename__ = "article_has_tags"
    id_article = db.Column(db.Integer, ForeignKey("articles.id_article"), primary_key=True)
    id_tag = db.Column(db.Integer, ForeignKey("tags.id_tag"), primary_key=True)
    # 引用文章 删除孤儿模式
    article = relationship(Article, backref=backref("article_has_tags", cascade="all, delete-orphan"))
    # 引用标签对象
    tag = relationship("Tag")
    # article.tag.append(Tag(), Tag())
    # def __init__(self, tag=None, article=None):
    #     self.article = article
    #     self.tag = tag
    def __repr__(self):
        return f"Article({self.id_article})-Tag({self.id_tag})"

class Tag(db.Model):
    __tablename__ = "tags"
    id_tag = db.Column(db.Integer, primary_key=True, nullable=False)
    tag_name = db.Column('tags', db.String(125), nullable=False)
    # def __init__(self, tag_name):
    #     self.tag_name = tag_name
    
association_table = db.Table()
class Movie(db.Model):  # 表名将会是 movie
    __tablename__ = 'movies'
    
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4))  # 电影年份