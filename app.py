from flask import Flask, render_template, request, url_for, redirect, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
import time, math
from flask_cors import CORS
from flask_bootstrap import Bootstrap
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/blog_cap'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
CORS(app)
ctx = app.app_context()
ctx.push()
app.secret_key = "flaskProject4"
bcrypt = Bcrypt()

db = SQLAlchemy(app)
# 初始化Bootstrap
bootstrap = Bootstrap(app)


# db imformation
# class User(db.Model):
#     id=db.Column(db.Integer,primary_key=True)
#     username=db.Column(db.String(80),unique=True,nullable=False)
#     email=db.Column(db.String(120),unique=True,nullable=False)
# 用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80), nullable=True)
    name = db.Column(db.String(64))

    def password_hash(self, password):
        self.password = generate_password_hash(password);


# 博客类型
class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80))


# 博客文章类型

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128))
    text = db.Column(db.TEXT)
    create_time = db.Column(db.String(64))
    # 关联关系映射

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='user')
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'))
    type = db.relationship('Type', backref='type')


# 博客评论类型
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(256))  # 评论内容
    create_time = db.Column(db.String(64))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='user1')
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))
    blog = db.relationship('Blog', backref='blog')

def login_limit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 我们这里用来区分是否登录的方法很简答，就是查看session中是否赋值了username，如果赋值了，说明已经登录了
        if session.get('username'):
            # 如果登录了，我们就正常的访问函数的功能
            return func(*args, **kwargs)
        else:
            # 如果没登录，我们就将它重定向到登录页面，这里大家也可以写一个权限错误的提示页面进行跳转
            return redirect(url_for('/login'))
    return wrapper

# db.create_all()
@app.route("/", methods=['POST', 'GET'])
def index():
    return redirect('/list/1')


@app.route("/list/<int:page_no>")
def show_blog_by_page(page_no=1):
    page_no = int(page_no)
    total_count = Blog.query.count()
    if total_count % 5 == 0 and total_count != 0:
        total_page = int(total_count / 5)
    else:
        total_page = int(total_count / 5) + 1
    # 分页5
    blogs = Blog.query.order_by(Blog.create_time.desc()).limit(5).offset((page_no - 1) * 5).all()
    return render_template('index.html', blogs=blogs, total_page=total_page, page_no=page_no)


@app.route("/blog/myblogs/<int:page_no>", methods=['GET', 'POST'])
def myblogs(page_no=1):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    user = User.query.filter_by(username=username).first()
    total_count = Blog.query.filter_by(user_id=user.id).count()

    if total_count % 5 == 0 and total_count != 0:
        total_page = int(total_count / 5)
    else:
        total_page = int(total_count / 5) + 1

    blogs = Blog.query.filter_by(user_id=user.id).order_by(Blog.create_time.desc()).limit(5).offset(
        (page_no - 1) * 5).all()

    return render_template('myblogs.html', blogs=blogs, total_page=total_page, page_no=page_no)


@app.route("/blog/myComments/1", methods=['GET', 'POST'])
def myComments():
    username = session.get('username')
    # 使用 filter_by(username=username) 而不是 filter_by(User.username==username)
    user = User.query.filter_by(username=username).first()
    if user is None:
        # 处理未找到用户的情况

        return redirect(url_for('login'))

    commentList = Comment.query.filter(Comment.user_id == user.id).order_by(Comment.create_time.desc()).all()
    return render_template('myComments.html', commentList=commentList, username=username)


@app.route('/deleteCom/<id>', methods=['GET', 'POST'])
def deleteCom(id):
    comentList = Comment.query.filter(Comment.id == id).first()
    db.session.delete(comentList)
    db.session.commit()

    return redirect(url_for('myComments'))


@app.route("/edit_blogs/<int:id>", methods=['GET', 'POST'])
def edit_blogs(id):
    blog = Blog.query.get(id)
    if request.method == 'POST':
        blog.title = request.form['title']
        blog.text = request.form['text']
        db.session.commit()
        flash("修改成功")
        return redirect(url_for('myblogs', page_no=1))
    return render_template('edit_blogs.html', blog=blog)


@app.route("/delete_blogs/<int:id>", methods=['GET', 'POST'])
def delete_blogs(id):
    blog = Blog.query.filter_by(id=id).first()
    db.session.delete(blog)
    db.session.commit()
    return redirect(url_for('myblogs', blog=blog, page_no=1))

    # page_no=session.get('page_no',1)

    # blog=Blog.query.get(id)
    # if request.method=='POST':
    #     blog.title = request.form['title']
    #     blog.text = request.form['text']
    #     db.session.commit()
    #     return redirect(url_for('/blog/myblogs/1',page_no=1,total_page=1))
    # page_no=session.get('page_no',1)
    # total_page=session.get('total_page',1)
    #
    # return render_template('myblogs.html', blog=blog,title=blog.title, text=blog.text,page_no=page_no,total_page=total_page)


@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')

    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # 直接比较明文密码，这是非常不安全的做法！
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            # 登录成功
            session['username'] = user.username
            # 返回JSON响应给前端
            return jsonify({'status': 'success', 'message': 'Login successful'})
        else:
            # 登录失败
            # 返回JSON响应给前端
            return jsonify({'status': 'failure', 'message': 'Invalid username or password'}), 401


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        # 检查用户名是否已存在
        existing_user_by_username = User.query.filter_by(username=username).first()
        if existing_user_by_username:
            return jsonify({'success': False, 'message': '用户名已存在'})
            # 检查昵称是否已存在
        existing_user_by_name = User.query.filter_by(name=name).first()
        if existing_user_by_name:
            return jsonify({'success': False, 'message': '昵称已存在'})
            # 创建新用户并保存到数据库
        new_user = User(username=username, password=password, name=name)
        db.session.add(new_user)
        try:
            db.session.commit()

            return jsonify({'success': True})  # 注册成功
        except Exception as e:
            db.session.rollback()  # 如果出现错误，回滚数据库操作
            return jsonify({'success': False, 'message': str(e)})  # 返回错误信息

    return render_template('register.html')  # 显示注册表单


@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect("/")


@app.route("/blog/writeBlog", methods=['POST', 'GET'])
def write_blog():
    if request.method == 'GET':
        types = Type.query.all()
        return render_template('writeBlog.html', types=types)
    elif request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        create_time = time.strftime("%Y-%m-%d %H:%M:%S")
        username = session['username']
        user = User.query.filter(User.username == username).first()
        type_id = request.form['type_id']
        blog = Blog(title=title, text=content, create_time=create_time, user_id=user.id, type_id=type_id)
        db.session.add(blog)
        db.session.commit()
        return render_template("blogSuccess.html", title=title, id=blog.id)


@app.route("/showBlog/<id>/<page_no>", methods=['GET', 'POST'])
def show_blog(id, page_no=1):
    id = int(id)
    page_no = int(page_no)
    blog = Blog.query.filter(Blog.id == id).first()

    count = Blog.query.filter(Comment.blog_id == blog.id).count()
    if count % 5 == 0 and count != 0:
        total_page = int(count / 5)
    else:
        total_page = int(count / 5) + 1

    comments = Comment.query.filter(Comment.blog_id == blog.id).limit(5).offset((page_no - 1) * 5).all()

    return render_template("showBlog.html", blog=blog, total_page=total_page, comments=comments, page_no=page_no)


@app.route("/comment", methods=['GET', 'POST'])
def comment():
    blog_id = request.form['blog_id']
    text = request.form['text']
    username = session.get("username")

    # 查询用户，并检查是否找到了用户
    user = User.query.filter(User.username == username).first()
    if user is None:
        # 如果没有找到用户，可以返回错误信息或者重定向到登录页面
        return "用户未找到或未登录，请先登录。", 401  # 401 表示未授权

    create_time = time.strftime("%Y-%m-%d %H:%M:%S")
    comment = Comment(blog_id=blog_id, text=text, create_time=create_time, user_id=user.id)
    db.session.add(comment)
    db.session.commit()
    return redirect('showBlog/' + blog_id + "/" + str(1))


@app.route('/updatePwd', methods=['GET','POST'])
@login_limit
def update():
    if request.method == "GET":
        return render_template("updatePwd.html")
    if request.method == 'POST':
        lodPwd = request.form.get("lodPwd")
        newPwd1 = request.form.get("newPwd1")
        newPwd2 = request.form.get("newPwd2")
        username = session.get("username")
        user = User.query.filter(User.username == username).first()
        if user.password == lodPwd:
            if newPwd1 != newPwd2:
                flash("两次新密码不一致！")
                return render_template("updatePwd.html")
            else:
                # 直接更新密码
                user.password = newPwd1
                db.session.commit()
                flash("修改成功！")
                return render_template("login.html")
        else:
            flash("原密码错误！")
            return render_template("updatePwd.html")

@app.route("/about")
def about():
    return render_template("about.html")


@app.context_processor
def login_statue():
    username = session.get("username")
    if username:
        try:
            user = User.query.filter(User.username == username).first()
            if user is not None:
                return {"username": username, "password": user.password, "name": user.name}
        except Exception as e:
            return e
    else:
        return {}


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)

