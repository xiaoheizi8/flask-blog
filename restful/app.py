# from flask import Flask, request, jsonify, session, redirect, url_for, render_template, flash
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_cors import CORS
# import time
# from functools import wraps
#
# app = Flask(__name__)
# CORS(app)
# ctx = app.app_context()
# ctx.push()
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/blog_cap'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# app.secret_key = "flaskProject4"
# bcrypt = Bcrypt()
#
# db = SQLAlchemy(app)
#
# # 用户模型
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True)
#     password = db.Column(db.String(80), nullable=True)
#     name = db.Column(db.String(64))
#
#     def password_hash(self, password):
#         self.password = generate_password_hash(password)
#
# # 博客类型
# class Type(db.Model):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String(80))
#
# # 博客文章类型
# class Blog(db.Model):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     title = db.Column(db.String(128))
#     text = db.Column(db.TEXT)
#     create_time = db.Column(db.String(64))
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     type_id = db.Column(db.Integer, db.ForeignKey('type.id'))
#
# # 博客评论类型
# class Comment(db.Model):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     text = db.Column(db.String(256))
#     create_time = db.Column(db.String(64))
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))
#
# # 登录限制装饰器
# def login_limit(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         if session.get('username'):
#             return func(*args, **kwargs)
#         else:
#             return jsonify({'error': 'Unauthorized access'}), 401
#     return wrapper
#
# # 首页路由，重定向到文章列表
# @app.route("/", methods=['GET'])
# def index():
#     return redirect('/list/1')
#
# # 文章列表路由
# @app.route("/list/<int:page_no>", methods=['GET'])
# def show_blog_by_page(page_no=1):
#     page_no = int(page_no)
#     # 查询文章总数
#     total_count = Blog.query.count()
#     # 计算总页数
#     total_page = total_count // 5 + (1 if total_count % 5 != 0 else 0)
#     # 分页查询文章
#     blogs = Blog.query.order_by(Blog.create_time.desc()).limit(5).offset((page_no - 1) * 5).all()
#     # 构造返回数据
#     blog_list = []
#     for blog in blogs:
#         blog_list.append({
#             'id': blog.id,
#             'title': blog.title,
#             'text': blog.text,
#             'create_time': blog.create_time,
#             'user_id': blog.user_id,
#             'type_id': blog.type_id
#         })
#     return jsonify({'blogs': blog_list, 'total_page': total_page, 'current_page': page_no})
#
# # 我的文章列表路由
# @app.route("/blog/myblogs/<int:page_no>", methods=['GET'])
# @login_limit
# def myblogs(page_no=1):
#     username = session['username']
#     user = User.query.filter_by(username=username).first()
#     # 查询当前用户的文章总数
#     total_count = Blog.query.filter_by(user_id=user.id).count()
#     # 计算总页数
#     total_page = total_count // 5 + (1 if total_count % 5 != 0 else 0)
#     # 分页查询用户的文章
#     blogs = Blog.query.filter_by(user_id=user.id).order_by(Blog.create_time.desc()).limit(5).offset((page_no - 1) * 5).all()
#     # 构造返回数据
#     blog_list = []
#     for blog in blogs:
#         blog_list.append({
#             'id': blog.id,
#             'title': blog.title,
#             'text': blog.text,
#             'create_time': blog.create_time,
#             'user_id': blog.user_id,
#             'type_id': blog.type_id
#         })
#     return jsonify({'blogs': blog_list, 'total_page': total_page, 'current_page': page_no})
#
# # 我的评论列表路由
# @app.route("/blog/myComments/<int:page_no>", methods=['GET'])
# @login_limit
# def myComments(page_no=1):
#     username = session.get('username')
#     user = User.query.filter_by(username=username).first()
#     if user is None:
#         return jsonify({'error': 'User not found'}), 404
#
#     # 查询当前用户的评论总数
#     total_count = Comment.query.filter_by(user_id=user.id).count()
#     # 计算总页数
#     total_page = total_count // 5 + (1 if total_count % 5 != 0 else 0)
#     # 分页查询用户的评论
#     comments = Comment.query.filter_by(user_id=user.id).order_by(Comment.create_time.desc()).limit(5).offset((page_no - 1) * 5).all()
#     # 构造返回数据
#     comment_list = []
#     for comment in comments:
#         comment_list.append({
#             'id': comment.id,
#             'text': comment.text,
#             'create_time': comment.create_time,
#             'user_id': comment.user_id,
#             'blog_id': comment.blog_id
#         })
#     return jsonify({'comments': comment_list, 'total_page': total_page, 'current_page': page_no})
#
# # 删除评论路由
# @app.route('/deleteCom/<int:id>', methods=['DELETE'])
# @login_limit
# def deleteCom(id):
#     comment = Comment.query.get(id)
#     if not comment:
#         return jsonify({'error': 'Comment not found'}), 404
#     db.session.delete(comment)
#     db.session.commit()
#     return jsonify({'message': 'Comment deleted successfully'})
#
# # 编辑文章路由
# @app.route("/blog/edit_blogs/<int:id>", methods=['PUT'])
# @login_limit
# def edit_blogs(id):
#     blog = Blog.query.get(id)
#     if not blog:
#         return jsonify({'error': 'Blog not found'}), 404
#
#     data = request.get_json()
#     if 'title' in data:
#         blog.title = data['title']
#     if 'text' in data:
#         blog.text = data['text']
#     db.session.commit()
#     return jsonify({'message': 'Blog updated successfully'})
#
# # 删除文章路由
# @app.route("/blog/delete_blogs/<int:id>", methods=['DELETE'])
# @login_limit
# def delete_blogs(id):
#     blog = Blog.query.get(id)
#     if not blog:
#         return jsonify({'error': 'Blog not found'}), 404
#
#     db.session.delete(blog)
#     db.session.commit()
#     return jsonify({'message': 'Blog deleted successfully'})
#
# # 注册路由
# @app.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')
#     name = data.get('name')
#
#     # 检查用户名和昵称是否已存在
#     existing_user_by_username = User.query.filter_by(username=username).first()
#     if existing_user_by_username:
#         return jsonify({'error': 'Username already exists'}), 400
#
#     existing_user_by_name = User.query.filter_by(name=name).first()
#     if existing_user_by_name:
#         return jsonify({'error': 'Name already exists'}), 400
#
#     # 创建新用户并保存到数据库
#     new_user = User(username=username, password=password, name=name)
#     db.session.add(new_user)
#     db.session.commit()
#     return jsonify({'message': 'User registered successfully'})
#
# # 登录路由
# @app.route('/login', methods=['POST'])
# def login():
#     data = request.json
#     username = data.get('username')
#     password = data.get('password')
#
#     # 查询用户
#     user = User.query.filter_by(username=username).first()
#     if user and user.check_password(password):
#         session['username'] = user.username
#         return jsonify({'message': 'Login successful'})
#     else:
#         return jsonify({'error': 'Invalid username or password'}), 401
# # 登出路由
# @app.route("/logout", methods=['GET'])
# def logout():
#     session.pop('username', None)
#     return jsonify({'message': 'Logged out successfully'})
#
# # 修改密码路由
# @app.route('/updatePwd', methods=['PUT'])
# @login_limit
# def update():
#     username = session.get("username")
#     user = User.query.filter_by(username=username).first()
#
#     data = request.get_json()
#     old_password = data.get('old_password')
#     new_password = data.get('new_password')
#
#     if check_password_hash(user.password, old_password):
#         user.password = generate_password_hash(new_password)
#         db.session.commit()
#         return jsonify({'message': 'Password updated successfully'})
#     else:
#         return jsonify({'error': 'Incorrect old password'}), 400
#
# if __name__ == "__main__":
#     app.run(debug=True)
