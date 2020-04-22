from watchlist.models import User, Movie, PostForm, Article, Tag, Article_Has_Tag
from flask import Flask, render_template, url_for, flash, request, redirect, Response, jsonify
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
import re, os, datetime
from flask_wtf.csrf import CSRFProtect
from watchlist import app, db, admin
from werkzeug.routing import  BaseConverter
csrf = CSRFProtect()   # 惰性加载
from flask_admin import Admin, BaseView, expose
from .HMM_IME.predict import predicter

from werkzeug.routing import BaseConverter

class RegexConverter(BaseConverter):
    def __init__(self, url_map,*items):
        super(RegexConverter,self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter

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
            return redirect(url_for('login'))
    print("Test!")
    return render_template("SignIn.html")

# 登出视图
@app.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    flash('我爱你，再见')
    logout_user()  # 登出用户
    return redirect(url_for('index'))  # 重定向回首页

@app.route('/IME', methods=['GET', 'POST'])
def IME():
    HMM_predict = predicter()
    best_list = [ ]
    if request.method == "POST":
        sentence = request.form['sentence']
        sentence_list = ["START"] + sentence.strip(' ').split(" ") + ["END"]
        print(sentence_list)
        best_list = HMM_predict.predict(sentence_list)
        print(best_list)
    return render_template("IME.html", best_list = best_list, load_time = HMM_predict.load_model_time)

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

@app.route('/article/add', methods=['GET', 'POST'])
@login_required
def article_add():
    candidate_tags = Tag.query.all()
    form = PostForm(request.form)
    print("test")
    if request.method == "POST":
        print("test2")
        if form.validate():
            title = form.title.data
            content = form.body.data
            # 如果form表单中有list元素长度大于1就取list，否则取单个元素
            data = dict((key, request.form.getlist(key) \
                if len(request.form.getlist(key)) > 1 else 
                request.form.getlist(key)[0]) \
                    for key in request.form.keys())
            content_HTML = data['test-editormd-html-code']
            print(form)
            print(data)

            temp_article = Article(title = title, \
                content = content, \
                    user_id=current_user.id, \
                        content_html = content_HTML)
            db.session.add(temp_article)
            db.session.commit()
            # 降序排列id_article得到刚刚添加的文章id
            current_article = Article.query\
                .order_by(Article.id_article.desc())\
                    .first()
                # 遍历标签找出选中的标签
            for can_tag in candidate_tags:
                if can_tag.tag_name in data:
                    temp_article_has_tag = Article_Has_Tag(\
                        # article = current_user,\
                        id_article = current_article.id_article,\
                        id_tag = can_tag.id_tag)
                        # tag = can_tag)
                    db.session.add(temp_article_has_tag)
                    db.session.commit()
            flash("文章保存成功")
            return redirect(url_for('edit_article', idx=current_article.id_article))
        else:
            flash("请填充一些内容再保存")
    return render_template("add_article.html", form=form)

@app.route('/upload/',methods=['POST'])
@login_required
def upload():
    print("Img upload")
    file=request.files.get('editormd-image-file')
    if not file:
        res={
            'success':0,
            'message':'上传失败'
        }
    else:
        ex=os.path.splitext(file.filename)[1]
        filename=datetime.datetime.now().strftime('%Y%m%d%H%M%S')+ex
        # 图片保存路径
        file.save(os.path.join("./watchlist/static/images", filename))
        res={
            'success':1,
            'message':'上传成功',
            'url':url_for('.image',name=filename)
        }
    return jsonify(res)

@app.route('/image/<name>')
@csrf.exempt
def image(name):
    with open(os.path.join('./watchlist/static/images',name),'rb') as f:
        resp=Response(f.read(),mimetype="image/jpeg")
    return resp
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

@app.route('/article/<int:idx>', methods=['GET'])
@login_required
def post(idx):
    article = Article.query \
        .filter_by(id_article = idx).first()
    if article == None:
        return redirect(url_for('article_add'))
    # article.hits += 1                # 点击量更新
    article.increase_hits()
    # try:
    #     db.session.commit()
    # except:
    #     db.session.rollback()
    # user = current_user._get_current_object()
    # if article.user_id == user.id:
    #     return redirect(url_for("edit_article", idx=idx))
    return render_template("post_article.html", article = article)

@app.route('/edit_article/<regex(r"\d{0,2}"):idx>', methods=['GET', 'POST'])
@login_required
def edit_article(idx):
    candidate_tags = Tag.query.all()
    idx = int(idx)
    print(idx)
    article = Article.query \
        .filter_by(id_article = idx).first()
    if article == None:
        return redirect(url_for('article_add'))
    user = current_user._get_current_object()
    auth = False
    if article.user_id != user.id:
        flash("抱歉您不是该文章的作者 无权限修改")
        return redirect(url_for("post", idx=idx))

    form = PostForm(request.form)
    # 表单初始化 
    form.title.data = article.title
    form.body.data = article.content
    print("test")
    if request.method == "POST":
        print("test2")
        if form.validate():
            title = form.title.data
            content = form.body.data
            # 如果form表单中有list元素长度大于1就取list，否则取单个元素
            data = dict((key, request.form.getlist(key) \
                if len(request.form.getlist(key)) > 1 else 
                request.form.getlist(key)[0]) \
                    for key in request.form.keys())
            content_HTML = data['test-editormd-html-code']
            print(form)
            print(data)
            article.title = title
            article.content = content
            article.content_html = content_HTML
            db.session.query(Article_Has_Tag)\
                .filter(Article_Has_Tag.id_article==article.id_article)\
                    .delete()
                    
                # 遍历标签找出选中的标签 先删再添加
            for can_tag in candidate_tags:
                if can_tag.tag_name in data:
                    temp_article_has_tag = Article_Has_Tag(\
                        # article = current_user,\
                        id_article = article.id_article,\
                        id_tag = can_tag.id_tag)
                        # tag = can_tag)
                    db.session.add(temp_article_has_tag)
                    db.session.commit()

            # temp_article = Article(title = title, \
            #     content = content, \
            #         user_id=current_user.id, \
            #             content_html = content_HTML)
            # db.session.add(temp_article)
            article.updatetime()
            db.session.commit()
            # 降序排列id_article得到刚刚添加的文章id
            # current_article = Article.query\
            #     .order_by(Article.id_article.desc())\
            #         .first()
            flash("文章修改成功")
    return render_template("edit_article.html", form=form, idx=idx, article=article)

@app.route('/', methods=["GET", "POST"])
@login_required
def index():
    # articles = User.query.first()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))
    selected_tag = int(request.args.get('selected_tag', 0))

    user = current_user._get_current_object()
    if selected_tag == 0:
        # 按更新时间倒序排列
        paginates = Article.query \
            .filter_by(user_id=user.id) \
            .order_by(Article.update_time.desc()) \
            .paginate(page, per_page, error_out = False)
    else: 
        # 被选中标签对应的文章列表
        article_list = db.session.query(Article_Has_Tag.id_article) \
            .filter_by(id_tag = selected_tag)\
            .all()
        article_list = [article[0] for article in article_list]
        paginates = Article.query \
            .filter_by(user_id=user.id) \
            .filter(Article.id_article.in_(article_list) ) \
            .order_by(Article.update_time.desc()) \
            .paginate(page, per_page, error_out = False)
    articles = paginates.items
    # print(articles)
    return render_template('index.html', articles=articles, paginates=paginates)
    # if request.method == "POST":
    #     title = request.form["title"]
    #     year  = request.form["year"]
    #     movie = Movie(title = title, year = year)
    #     db.session.add(movie)
    #     db.session.commit()
    #     flash("添加电影成功")
    # movies = Movie.query.all()
    # return render_template('index.html', movies=movies)


