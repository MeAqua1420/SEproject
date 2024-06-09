from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
import logging
import webbrowser

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://qiurui:qiurui5312@localhost/algorithmdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 配置日志
logging.basicConfig(level=logging.INFO)


class User(db.Model):
    __tablename__ = 'users'  # 确保表名与数据库中的表名一致
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=False)


class Algorithm(db.Model):
    __tablename__ = 'algorithms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    time_complexity = db.Column(db.String(255), nullable=False)
    uploader = db.Column(db.String(255), nullable=False)
    storage_location = db.Column(db.Text, nullable=False)
    upload_date = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

@app.route('/register', methods=['POST'])
def register_user():
    try:
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']
        logging.info(f"Received registration data: username={username}, phone={phone}")
        new_user = User(username=username, password=password, phone=phone)
        heap_sort = Algorithm(name='monkey Sort', time_complexity='O(n!)', uploader='fuck', storage_location='/Users/qiurui/PycharmProjects/SEdemo/test.txt')
        db.session.add(new_user)
        db.session.add(heap_sort)
        db.session.commit()
        logging.info(f"User {username} registered successfully.")

        return render_template('error5.html', message="注册成功")
    except IntegrityError as e:
        db.session.rollback()
        logging.error(f"IntegrityError: {e}")
        return render_template('error2.html', message="用户名已存在，请重新注册")
    except Exception as e:
        logging.error(f"Error: {e}")
        return render_template('error.html', message="注册失败，请重试")


@app.route('/login', methods=['POST'])
def login_user():
    try:
        print(request.form)
        username = request.form['username']
        password = request.form['password']
        print("username ="+username)
        print("password =" + password)
        logging.info(f"Received login data: username={username}")
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            print("gooduser")
            logging.info(f"User {username} logged in successfully.")

            return render_template('ku.html', message="登录成功");
        else:
            logging.warning(f"Invalid credentials for user {username}.")

            return render_template('error.html', message="登录失败");
    except Exception as e:
        logging.error(f"Error: {e}")
        return render_template('error.html', message="登录失败，请重试")


@app.route('/reset_password', methods=['POST'])
def reset_password():
    try:
        print(request.form)
        username = request.form['username']
        phone = request.form['phone']
        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']

        logging.info(f"Received reset password data: username={username}, phone={phone}")

        if new_password != confirm_new_password:
            logging.warning("Passwords do not match.")
            return render_template('error1.html', message="两次输入的密码不一致，请重新输入")

        user = User.query.filter_by(username=username, phone=phone).first()
        if user:
            user.password = new_password
            db.session.commit()
            logging.info(f"Password for user {username} reset successfully.")
            return render_template('error4.html', message="密码重置成功")
        else:
            logging.warning(f"User {username} not found or invalid phone number.")
            return render_template('error3.html', message="用户未找到或手机号不正确")
    except Exception as e:
        logging.error(f"Error: {e}")
        return render_template('error.html', message="密码重置失败，请重试")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, use_reloader=False, port=6699)
