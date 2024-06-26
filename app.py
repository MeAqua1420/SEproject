import urllib
import os
from _curses import flash

from flask import Flask, request, jsonify, render_template,send_file,redirect, url_for, flash,g, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
import logging
import webbrowser
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://qiurui:qiurui5312@localhost/algorithmdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '/Users/qiurui/PycharmProjects/SEdemo'
app.secret_key = 'supersecretkey'

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
    type = db.Column(db.String(255),nullable = False)

class Repositories(db.Model):
    __tablename__ = 'repositories'
    id = db.Column(db.Integer, primary_key=True)
    alid = db.Column(db.Integer)
    ownerid = db.Column(db.Integer)

class DBaction:
    def AddUser(self):
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']

        logging.info(f"Received registration data: username={username}, phone={phone}")
        new_user = User(username=username, password=password, phone=phone)
        db.session.add(new_user)
        db.session.commit()

@app.route('/register', methods=['POST'])
def register_user():
    try:
        DBaction.AddUser(act)
        logging.info(f"User {request.form['username']} registered successfully.")

        return render_template('error5.html', message="注册成功")
    except IntegrityError as e:
        db.session.rollback()
        logging.error(f"IntegrityError: {e}")
        return render_template('error2.html', message="用户名已存在，请重新注册")
    except Exception as e:
        logging.error(f"Error: {e}")
        return render_template('error.html', message="注册失败，请重试")

@app.before_request
def before_request():
    g.username = session.get('username')
@app.route('/login', methods=['POST'])
def login_user():
    try:
        username = request.form['username']
        password = request.form['password']
        logging.info(f"Received login data: username={g.username}")
        user = User.query.filter_by(username=username, password=password).first()
        app.config['UPLOAD_FOLDER'] = app.config['UPLOAD_FOLDER']+"/"+username
        comd = 'mkdir '+app.config['UPLOAD_FOLDER']
        os.system(comd)
        if user:
            print("gooduser")
            session['username'] = username
            logging.info(f"User {username} logged in successfully.")
            sort_count = Algorithm.query.filter_by(type='SORT').count()
            search_count = Algorithm.query.filter_by(type='Search').count()
            math_count = Algorithm.query.filter_by(type='Math').count()
            graph_count = Algorithm.query.filter_by(type='Graph').count()
            return render_template('ku.html', message="登录成功",data1 = [sort_count,search_count,math_count,graph_count])
        else:
            logging.warning(f"Invalid credentials for user {username}.")

            return render_template('error.html', message="登录失败")
    except Exception as e:
        logging.error(f"Error: {e}")
        return render_template('error.html', message="登录失败，请重试")


@app.route('/overview', methods=['GET'])
def overview():
    sort_count = Algorithm.query.filter_by(type='SORT').count()
    search_count = Algorithm.query.filter_by(type='Search').count()
    math_count = Algorithm.query.filter_by(type='Math').count()
    graph_count = Algorithm.query.filter_by(type='Graph').count()

    return render_template("overview.html",data1 = [sort_count, search_count, math_count, graph_count])

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    results = Algorithm.query.filter(
        (Algorithm.name.ilike(f'%{query}%')) | (Algorithm.type.ilike(f'%{query}%'))
    ).all()
    results_list = [{'name': alg.name, 'type': alg.type} for alg in results]
    return jsonify(results_list)

@app.route('/searchpage', methods=['GET'])
def searchpage():
    return render_template("hello.html")

@app.route('/algorithm/<name>', methods=['GET'])
def get_algorithm(name):
    print("hello")
    decoded_name = urllib.parse.unquote(name)
    print(decoded_name)
    algorithm = Algorithm.query.filter_by(name = name).first()
    print(algorithm)
    print(algorithm.type)
    file_content = ""
    try:
        with open(algorithm.storage_location, 'r') as file:
            file_content = file.read()
    except Exception as e:
        file_content = f"Error reading file: {e}"
    #print(file_content)
    if algorithm:
        return render_template("algorithm.html",
            name= algorithm.name,
            type= algorithm.type,
            time_complexity= algorithm.time_complexity,
            uploader=algorithm.uploader,
            storage_location=algorithm.storage_location,
            upload_date=algorithm.upload_date.strftime('%Y-%m-%d %H:%M:%S'),
            file_content = file_content
        )
    else:
        return jsonify({'error': 'Algorithm not found'}), 404
    return jsonify({'error': 'Algorithm not found'}), 404


@app.route('/download/<name>', methods=['GET'])
def download_algorithm(name):
    decoded_name = urllib.parse.unquote(name)
    algorithm = Algorithm.query.filter_by(name=decoded_name).first()
    if algorithm:
        return send_file(algorithm.storage_location, as_attachment=True, download_name=f"{algorithm.name}.py")
    else:
        return jsonify({'error': 'Algorithm not found'}), 404
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

@app.route('/uploadpage', methods=['GET', 'POST'])
def uploadpage():
    print(g.username)
    return render_template('upload.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_algorithm():
    if 'username' not in session:
        flash('You must be logged in to upload an algorithm.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        time_complexity = request.form['time_complexity']
        alg_type = request.form['type']
        file = request.files['file']

        if file and name and time_complexity and alg_type:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            new_algorithm = Algorithm(
                name=name,
                time_complexity=time_complexity,
                type=alg_type,
                uploader=g.username,  # 使用全局变量中的用户名
                storage_location=file_path,
                upload_date=datetime.now()
            )

            try:
                db.session.add(new_algorithm)
                db.session.commit()
                flash('Algorithm uploaded successfully!', 'success')
                return redirect(url_for('upload_algorithm'))
            except IntegrityError as e:
                db.session.rollback()
                flash('Error uploading algorithm: {}'.format(e), 'danger')
        else:
            flash('All fields are required!', 'danger')

    return render_template('upload.html')

@app.route('/my_repository', methods=['GET'])
def my_repository():
    if 'username' not in session:
        flash('You must be logged in to view your repository.', 'danger')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()
    if user:
        repositories = db.session.query(Repositories, Algorithm).join(Algorithm, Repositories.alid == Algorithm.id).filter(Repositories.ownerid == user.id).all()
        return render_template('my_repository.html', repositories=repositories)
    else:
        flash('User not found!', 'danger')
        return redirect(url_for('login'))

@app.route('/add_to_repository', methods=['POST'])
def add_to_repository():
    if 'username' not in session:
        return jsonify({'message': 'You must be logged in to add to your repository.'}), 401

    user_name = session['username']
    algorithm_name = request.form['name']
    user = User.query.filter_by(username = user_name).first()
    algorithm = Algorithm.query.filter_by(name=algorithm_name).first()
    print(user.id)
    print(algorithm.id)
    if not algorithm:
        return jsonify({'message': 'Algorithm not found.'}), 404

    existing_entry = Repositories.query.filter_by(ownerid=user.id, alid=algorithm.id).first()
    if existing_entry:
        return jsonify({'message': 'Algorithm already in your repository.'}), 409

    new_entry = Repositories(ownerid=user.id, alid=algorithm.id)
    try:
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({'message': 'Algorithm added to your repository successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error adding algorithm to repository: {e}'}), 500




if __name__ == '__main__':
    act = DBaction()
    with app.app_context():
        db.create_all()
    app.run(debug=True, use_reloader=False, port=6699)
