from flask_login import UserMixin
from . import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(150))
    lastname = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    phone = db.Column(db.Integer)
    password = db.Column(db.String(150))
    recipes = db.relationship('Recipe', backref=db.backref('user'))


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dish_name = db.Column(db.String(120))
    cooking_time = db.Column(db.Integer)
    description = db.Column(db.Text)
    ingredients = db.Column(db.Text)
    image = db.Column(db.Text)
    # new column 26.06.2023
    status = db.Column(db.String(20))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


