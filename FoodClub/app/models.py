from flask_login import UserMixin
from . import db

# for migration:
# flask db migrate -m "message"
# flask db upgrade


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(150))
    lastname = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    phone = db.Column(db.Integer)
    password = db.Column(db.String(150))

    role = db.Column(db.String(20))     # new column 26.06.2023

    recipes = db.relationship('Recipe', backref=db.backref('user'))


recipe_category = db.Table(                         # new reference table 29.06.2023
    'recipe_category',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dish_name = db.Column(db.String(120))
    cooking_time = db.Column(db.Integer)
    description = db.Column(db.Text)
    ingredients = db.Column(db.Text)
    image = db.Column(db.Text)

    status = db.Column(db.String(20))   # new column 26.06.2023

    # new relationship 29.06.2023
    categories = db.relationship('Category', secondary=recipe_category, backref=db.backref('recipe', lazy='dynamic'))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Category(db.Model):                           # new model 29.06.2023
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))


