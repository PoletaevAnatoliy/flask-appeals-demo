import os

from flask import Flask, render_template, redirect
from flask_login import login_user, LoginManager, login_required, logout_user, \
    current_user
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash
from wtforms import StringField, SubmitField, SelectField, PasswordField, \
    BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

from appeals_database import AppealsDatabase, Appeal, EngineersDatabase, Engineer


class NewAppealForm(FlaskForm):
    address = StringField("Адрес", validators=[DataRequired()])
    appeal_type = SelectField("Тип поломки",
                              choices=[('Горячая вода', "Горячая вода"),
                                       ('Холодная вода', "Холодная вода")])
    submit = SubmitField("Создать заявку")


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


def create_repair_site(name):
    app = Flask(name)
    print(os.getenv("SECRET_KEY"))
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

    appeals = AppealsDatabase()
    engineers = EngineersDatabase()
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return engineers.by_id(user_id)

    @app.route('/')
    def index():
        return redirect('/add_appeal')

    @app.route('/add_appeal', methods=['GET', 'POST'])
    def add_appeal():
        form = NewAppealForm()
        if form.validate_on_submit():
            appeals.add(Appeal(address=form.address.data,
                               kind=form.appeal_type.data))
            return render_template("appeal_added.html",
                                   title="Заявка успешно добавлена",
                                   form=form)
        return render_template("add_appeal.html",
                               title="Добавление заявки",
                               form=form)

    @app.route('/list_appeals')
    def list_appeals():
        return render_template("appeals_list.html",
                                appeals=appeals.get_all())

    @app.route('/take/<int:appeal_id>')
    @login_required
    def take_appeal(appeal_id):
        appeals.take(appeal_id, current_user.get_id())
        return redirect('/list_appeals')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            engineer = engineers.by_email(email=form.email.data)
            if engineer and engineer.check_password(form.password.data):
                login_user(engineer, remember=form.remember_me.data)
                return redirect("/")
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
        return render_template('login.html', title='Авторизация', form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect("/")

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            engineers.add(Engineer(name=form.name.data,
                                surname=form.surname.data,
                                email=form.email.data,
                                password=generate_password_hash(form.password.data)))
            return redirect("/")
        return render_template('register.html', title='Регистрация', form=form)

    return app


def main(name, port):
    app = create_repair_site(name)
    app.run(port=port)


if __name__ == '__main__':
    # Для упрощения примера; НЕЛЬЗЯ использовать на практике
    os.environ["SECRET_KEY"] = 'a'
    main("Repair site", 8000)
