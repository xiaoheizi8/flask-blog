from flask import Flask,request,url_for,redirect,session,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
import time,math
from flask_cors import CORS
from flask_bootstrap import Bootstrap
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/blog_cap'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
CORS(app)
ctx=app.app_context()
ctx.push()
app.secret_key="flaskProject4"
bcrypt=Bcrypt()

db=SQLAlchemy(app)

#用户模型
class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(80),unique=True)
    password=db.Column(db.String(80),nullable=True)
    name=db.Column(db.String(64))
 #博客类型
class Type(db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    name = db.Column(db.String(80))
#博客文章类型

class Blog(db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    title=db.Column(db.String(128))
    text=db.Column(db.TEXT)
    create_time=db.Column(db.String(64))
 #关联关系映射

    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    user=db.relationship('User',backref='user')
    type_id=db.Column(db.Integer,db.ForeignKey('type.id'))
    type=db.relationship('Type',backref='type')

#博客评论类型
class Comment(db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    text=db.Column(db.String(256))#评论内容
    create_time=db.Column(db.String(64))

    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    user=db.relationship('User',backref='user1')
    blog_id=db.Column(db.Integer,db.ForeignKey('blog.id'))
    blog=db.relationship('Blog',backref='blog')

@app.route("/",methods=['POST','GET'])
def index():
    return jsonify({'message': 'Welcome to the blog_cap API'})
@app.route("/list/<int:page_no>")
def show_blog_by_page(page_no=1):
    page_no=int(page_no)
    total_count=Blog.query.count()
    if total_count%5==0 and total_count!=0:
        total_page=int(total_count/5)
    else:
        total_page=int(total_count/5)+1
    blogs=Blog.query.order_by(Blog.create_time.desc()).limit(5).offset((page_no-1)*5).all()
    blog_list = []
    for blog in blogs:
        blog_data = {
            'id': blog.id,
            'title': blog.title,
            'text': blog.text,
            'user_id': blog.user_id,
            'type_id': blog.type_id,
            'create_time': blog.create_time
        }
        blog_list.append(blog_data)
    return jsonify({'total_page': total_page, 'page_no': page_no, 'blogs': blog_list})


@app.route("/blog/myblogs/<int:page_no>", methods=['GET','POST'])
def myblogs(page_no=1):
    if 'username' not in session:
        return jsonify({'message': 'Please log in'})

    username = session['username']
    user = User.query.filter_by(username=username).first()
    total_count = Blog.query.filter_by(user_id=user.id).count()

    if total_count % 5 == 0 and total_count != 0:
        total_page = int(total_count / 5)
    else:
        total_page = int(total_count / 5) + 1

    blogs = Blog.query.filter_by(user_id=user.id).order_by(Blog.create_time.desc()).limit(5).offset((page_no - 1) * 5).all()

    blog_list = []
    for blog in blogs:
        blog_data = {
            'id': blog.id,
            'title': blog.title,
            'text': blog.text,
            'user_id': blog.user_id,
            'type_id': blog.type_id,
            'create_time': blog.create_time
        }
        blog_list.append(blog_data)

    return jsonify({'total_page': total_page, 'page_no': page_no, 'blogs': blog_list})
@app.route("/blog/myComments/<int:page_no>",methods=['GET','POST'])
def myComments(page_no=1):
    username = session.get('username')
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify({'message': 'User not found or not logged in'})

    commentList = Comment.query.filter(Comment.user_id == user.id).order_by(Comment.create_time.desc()).all()

    comment_list = []
    for comment in commentList:
        comment_data = {
            'id': comment.id,
            'text': comment.text,
            'create_time': comment.create_time,
            'user_id': comment.user_id,
            'blog_id': comment.blog_id
        }
        comment_list.append(comment_data)

    return jsonify({'comments': comment_list})
@app.route('/deleteCom/<id>', methods=['GET','POST'])
def deleteCom(id):
    comentList = Comment.query.filter(Comment.id == id).first()
    db.session.delete(comentList)
    db.session.commit()

    return jsonify({})
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return jsonify('msg',"非法请求")

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

    # return jsonify({'success': True, 'message': '成功'})
@app.route("/logout")
def logout():
    session.pop('username',None)
    return redirect("/")
@app.route('/updatePwd', methods=['GET', 'POST'])
def updatePwd():
    if request.method == 'GET':
        return jsonify({"success":False,'message':'非法请求'})
    elif request.method == 'POST':
        username = session.get("username")
        if not username:
            return jsonify({'message': '用户未登录，请先登录'})

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'message': '用户不存在'})

        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')

        if not old_password or not new_password:
            return jsonify({'message': '请输入旧密码和新密码'})

        if not check_password_hash(user.password, old_password):
            return jsonify({'message': '旧密码错误'})

        user.password = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({'message': '密码修改成功'})
if __name__ == "__main__":
    app.run(debug=True,use_reloader=True)
