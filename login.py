# from flask import Flask,render_template,request,url_for,redirect,flash
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import login_user
# from flask_cors import CORS
# app=Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/flaskblog'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
# CORS(app)
# ctx=app.app_context()
# ctx.push()
#
# db=SQLAlchemy(app)
# #db imformation
# class User(db.Model):
#     id=db.Column(db.Integer,primary_key=True)
#     username=db.Column(db.String(80),unique=True,nullable=False)
#     password=db.Column(db.String(120),unique=True,nullable=False)
# # db.create_all()
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'GET':
#         username = request.form['username']
#         password = request.form['password']
#
#         if not username or not password:
#             flash('Invalid input.')
#             return render_template(login)
#
#         user = User.query.first()
#
#         if username == user.username and user.validate_password(password):
#             login_user(user)
#             flash('Login success.')
#             return render_template('index.html')
#
#         flash('Invalid username or password.')
#         return render_template('login.html')
#
#     return render_template('login.html')
#
# if __name__ == "__main__":
#
#     app.run(debug=True)