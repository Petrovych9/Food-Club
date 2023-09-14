import flask
from flask import Blueprint, render_template, request, url_for, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from .views import menu
from . import db
from .models import User
from flask_login import login_user, login_required, logout_user, current_user

authBlueprint = Blueprint('auth', __name__)


@authBlueprint.route("/sign-up", methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        print(first_name, last_name, email, phone, password)
        user = User.query.filter_by(email=email).first()
        print(user)
        if user:
            flask.flash('Email already sign up. Try to sign IN.', category="error")
        elif first_name == "":
            flask.flash('Enter the First name', category="error")
        elif last_name == "":
            flask.flash('Enter the Last name', category="error")
        elif email == "@gmail.com":
            flask.flash('Enter the Email', category="error")
        elif len(phone) < 3:
            flask.flash('Invalid phone number', category="error")
        elif len(password) < 1:
            flask.flash('Password too short', category="error")
        else:
            new_user = User(firstname=first_name, lastname=last_name,
                           email=email, phone=phone, role='user',
                           password=generate_password_hash(password, method='scrypt'))
            db.session.add(new_user)
            db.session.commit()
            flask.flash('Account created', category="success")
            return redirect(url_for('main.home'))

    return render_template('signUP.html', menu=menu(), email='@gmail.com', phone='+380', user=current_user)


@authBlueprint.route("/sign-in", methods=["GET", 'POST'])
def signin():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flask.flash('Welcome!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('main.home'))
            else:
                flask.flash('Invalid password', category='error')
        else:
            flask.flash('Invalid email', category='error')

    return render_template('signIN.html', menu=menu(), email='@gmail.com', user=current_user)


@authBlueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.signin'))
