import json

from flask import Flask, render_template, redirect, request, abort, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from data import db_session
from data.add_job import AddJobForm
from data.login_form import LoginForm
from data.users import User
from data.tovar import Tovar
from data.payments import Payment

from data.register import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/jobs_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def jobs_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(Tovar).filter(Tovar.id == id).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/addtovar', methods=['GET', 'POST'])
def addjob():
    add_form = AddJobForm()
    if add_form.validate_on_submit():
        db_sess = db_session.create_session()
        tovars = Tovar(
            name=add_form.job.data,
            cost=add_form.team_leader.data,
            user_id_create=add_form.work_size.data
        )
        db_sess.add(tovars)
        db_sess.commit()
        return redirect('/')
    return render_template('addjob.html', title='Adding a job', form=add_form)


@app.route('/info/<int:id>', methods=['GET', 'POST'])
def info(id):
    form = AddJobForm()
    db_sess = db_session.create_session()
    infos = db_sess.query(Tovar).filter(Tovar.id == id).first()

    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.basket = str(current_user.basket) + ' ' + str(id)
        db_sess.commit()
        return redirect('/')

    tovars_user_col = 0
    if current_user.is_authenticated:
        basket = current_user.basket
        if basket is not None:
            basket = basket.split()
            tovars_user_col = len(basket)
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={infos.adress}&format=json"
    print(geocoder_request)
    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        print(toponym_coodrinates)
    else:
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
    coodrinates = toponym_coodrinates.split()
    x = coodrinates[0]
    y = coodrinates[1]
    print(x, y)
    print(type(55.887422))
    x = float(x)
    print(type(x))
    return render_template('info.html', info=infos, tovars_user_col=tovars_user_col, title='Информация о товаре',
                           form=form, x=x, y=y)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Wrong login or password", form=form)
    return render_template('login.html', title='Authorization', form=form)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    tovars = db_sess.query(Tovar).all()
    tovars_user_col = 0
    if current_user.is_authenticated:
        basket = current_user.basket
        if basket is not None:
            basket = basket.split()
            tovars_user_col = len(basket)
    return render_template("index.html", jobs=tovars, tovars_user_col=tovars_user_col, title='Наши товары')


@app.route("/profile")
@login_required
def profile():
    db_sess = db_session.create_session()
    tovars = db_sess.query(Tovar).all()
    basket = current_user.basket
    tovars_user_col = 0
    payments = db_sess.query(Payment).filter(Payment.user_id == current_user.id).all()
    if basket is not None:
        basket = basket.split()
        tovars_user_col = len(basket)
    return render_template("profile.html", my_towar=tovars, payments=payments, tovars_user_col=tovars_user_col, user=current_user,
                           title='Профиль')


@app.route("/basket", methods=['GET', 'POST'])
@login_required
def basket():
    form = AddJobForm()
    db_sess = db_session.create_session()
    basket = current_user.basket
    tovars_user_col = 0
    if basket is not None:
        basket = basket.split()
        tovars_user_col = len(basket)
    baskets = []
    all_cost = 0
    for i in basket:
        t = db_sess.query(Tovar).filter(Tovar.id == i).first()
        all_cost += int(t.cost)
        baskets.append(t)
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.basket = ''
        db_sess.commit()
        db_sess = db_session.create_session()
        payments = Payment(
            sum_cost=all_cost,
            quantity=tovars_user_col,
            status=2,
            user_id=current_user.id
        )
        db_sess.add(payments)
        db_sess.commit()

        msg = MIMEMultipart()

        message = f"Спасибо за заказ. \nСумма заказа: {all_cost}\nСтатус заказа: отправлено"

        # setup the parameters of the message
        password = "15052004Nikita"
        msg['From'] = "nikita.masha1315@gmail.com"
        msg['To'] = current_user.email
        msg['Subject'] = "Subscription"

        # add in the message body
        msg.attach(MIMEText(message, 'plain'))

        # create server
        server = smtplib.SMTP('smtp.gmail.com: 587')

        server.starttls()

        # Login Credentials for sending the mail
        server.login(msg['From'], password)

        # send the message via the server.
        server.sendmail(msg['From'], msg['To'], msg.as_string())

        server.quit()
        return redirect('/profile')
    print(baskets)
    return render_template("basket.html", basket=baskets, tovars_user_col=tovars_user_col, user=current_user,
                           title='Корзина', form=form, all_cost=all_cost)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Register', form=form,
                                   message="Passwords don't match")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Register', form=form,
                                   message="This user already exists")
        user = User(
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        msg = MIMEMultipart()

        message = f"Спасибо за регистрацию. \nДанные для входа: \nПочта: {form.email.data} \nПароль: {form.password.data}"

        # setup the parameters of the message
        password = "15052004Nikita"
        msg['From'] = "nikita.masha1315@gmail.com"
        msg['To'] = form.email.data
        msg['Subject'] = "Subscription"

        # add in the message body
        msg.attach(MIMEText(message, 'plain'))

        # create server
        server = smtplib.SMTP('smtp.gmail.com: 587')

        server.starttls()

        # Login Credentials for sending the mail
        server.login(msg['From'], password)

        # send the message via the server.
        server.sendmail(msg['From'], msg['To'], msg.as_string())

        server.quit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.errorhandler(401)
def not_found(error):
    return redirect('/login')


def main():
    db_session.global_init("E:\project/baza.sqlite")

    app.run(port=6660)


if __name__ == '__main__':
    main()
