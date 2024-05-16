import flask
from flask import Flask, render_template, request, flash, url_for, redirect
from models import Session, Users, POSTGRES_DB
from errors import HttpError
import time
from flask_login import LoginManager, login_user, login_required, current_user
from login import UserLogin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qweqweqweqwe'
login_manager = LoginManager(app)
@app.before_request
def before_request():
    session = Session()
    request.session = session

@app.after_request
def after_request(response: flask.Response):
    request.session.close()
    return response

@login_manager.user_loader
def get_user(user: Users):
    try:
        user = request.session.get(Users, user)
        if not user:
            return HttpError(404, 'user not found')
        return user
    except:
        print('ошибка в get_user')
def add_user(user: Users):
    try:
        request.session.add(user)
        request.session.commit()
    except Exception as error:
        print(error)
        raise HttpError(status_code=409, description='cant add user')

@app.route('/')
def index():
    return render_template('index.html')

def load_user(user_id):
    return UserLogin().fromDB(user_id, Users)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':

        user_id = Users.get_user_by_login(request.form['login'])
        if user_id:
            user = request.session.get(Users, user_id)
            if user and user.password == request.form['password']:
                userlogin = UserLogin().create(user.dict)
                print(userlogin)
                print(userlogin.is_authenticated())
                print(type(userlogin))
                login_user(userlogin)
                return redirect(url_for('start_page'))
        flash('Неверный пароль или пользовател я не существует', 'error')
    return render_template('login.html')

@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        try:
            login = request.form['login']
            password = request.form['password']
            user = Users(login=login, password=password)
            add_user(user)
            flash('Регистрация прошла успешно', category='success')
            return redirect(url_for('login'))
        except Exception as e:
            print(e)
            flash('Регистрация не получилась', category='error')
    return render_template('registration.html')


@app.route('/page_for_authorizated', methods=['GET'])
@login_required
def start_page():
    return 'Вы авторизованы'


if __name__ == '__main__':
    app.run(debug=True)