import os.path

import flask
import base64
from flask import Blueprint,render_template, request, url_for, redirect
from flask_login import current_user, login_required
from .menu import menu
from .models import Recipe, User, Category, recipe_category
from . import db


mainBlueprint = Blueprint('main', __name__)


def convert_image(image):
    img = image.read()
    if img == b'':
        def_image_path = 'app/static/images/new_recipe/default.jpg'
        with open(def_image_path, 'rb') as def_image:
            def_img = def_image.read()
            base64_data = base64.b64encode(def_img).decode('utf-8')
        return base64_data
    else:
        base64_data = base64.b64encode(img).decode('utf-8')
        return base64_data

def add_recipe_category(recipe, categories):
    for category in categories:
        cat = Category.query.get(category)
        recipe.categories.append(cat)

def select_status(button):
    if button == 'Drafts':
        status = 'Drafts'

    elif button == 'need-submit':
        status = 'need-submit'

    elif button == 'Delete':
        status = 'Delete'

    else:status = 'default'

    return status

def send_feedback(status):
    if status == 'Drafts':
        return flask.flash("Recipe in your drafts!", category="success")
    elif status == 'need-submit':
        return flask.flash("Recipe sent for submission!", category="success")
    elif status == 'Delete':
        return flask.flash("Recipe deleted!", category='success')
    else:
        return flask.flash("Occur some error. Try again", category="error")


#main
@mainBlueprint.route("/", methods=["GET", ' POST'])
@login_required
def home():
    recipes = Recipe.query.filter_by(status='Published').order_by(Recipe.id.desc()).limit(6).all()
    return render_template('home.html', menu=menu(), user=current_user, recipes=recipes)


@mainBlueprint.route("/categories", methods=["GET", ' POST'])
@login_required
def categories():
    all_categories = Category.query.all()
    return render_template('categories.html', menu=menu(), user=current_user, categories=all_categories)




@mainBlueprint.route('/new-recipe', methods=["POST", 'GET'])
@login_required
def new_recipe():
    categories_all = Category.query.all()

    if request.method == "POST":
        dish_name = request.form['dish_name']
        cooking_time = request.form['cooking_time']
        description = request.form['description']
        ingredients = request.form['ingredients']
        image = request.files['photo']
        selected_categories = request.form.getlist('checkbox')
        button = request.form['button']

        if dish_name != '':
            if selected_categories:
                new_rec = Recipe(
                    dish_name=dish_name,
                    cooking_time=cooking_time,
                    description=description,
                    ingredients=ingredients,
                    image=convert_image(image),
                    status=select_status(button),
                    user_id=current_user.id)

                add_recipe_category(new_rec, selected_categories)

                db.session.add(new_rec)
                db.session.commit()

                send_feedback(new_rec.status)

            else: flask.flash("Please select category.", category='error')
        else: flask.flash("Enter a dish name", category='error')

    return render_template('new-recipe.html', menu=menu(), user=current_user, categories=categories_all)


@mainBlueprint.route('/my-drafts', methods=["POST", 'GET'])
@login_required
def draft_recipes():
    if request.form:
        id = request.form['id']
        return redirect(url_for('main.update_draft', recipe_id=id))

    recipes = Recipe.query.filter_by(status='Drafts', user_id=current_user.id).all()
    return render_template('my-drafts.html', menu=menu(), user=current_user, recipes=recipes)


@mainBlueprint.route('/my-drafts/<int:recipe_id>', methods=["POST", 'GET'])
@login_required
def update_draft(recipe_id):
    recipe = Recipe.query.filter_by(id=recipe_id).first()
    selected_categories = recipe.categories
    categories = Category.query.all()

    if request.method == 'POST':
        recipe.dish_name = request.form['dish_name']
        recipe.cooking_time = request.form['cooking_time']
        recipe.description = request.form['description']
        recipe.ingredients = request.form['ingredients']
        image = request.files['photo']
        new_selected_categories = request.form.getlist('checkbox')
        button = request.form['button']

        if image.filename != "":
            recipe.image = convert_image(image)
            print("Photo updated")

        if new_selected_categories:
            recipe.categories.clear()
            add_recipe_category(recipe, new_selected_categories)

            if button == 'Delete':
                db.session.delete(recipe)
            else:
                recipe.status = select_status(button)

            db.session.commit()
            send_feedback(button)
            return redirect(url_for('main.draft_recipes'))

        else: flask.flash("Please select category.", category='error')


    return render_template('my-drafts-edit.html',menu=menu(), user=current_user, recipe=recipe, id=recipe.id,
                           categories=categories, selected_categories=selected_categories)


@mainBlueprint.route('/all-recipes', methods=["POST", 'GET'])
@login_required
def all_recipes():
    recipes = Recipe.query.filter_by(status='Published').all()
    return render_template('all-recipes.html', menu=menu(), user=current_user, recipes=recipes)


@mainBlueprint.route('/recipe/<int:id>', methods=["POST", 'GET'])
@login_required
def recipe(id):
    recipe = Recipe.query.filter_by(id=id).first()
    return render_template('recipe.html', menu=menu(), user=current_user, recipe=recipe)

@mainBlueprint.route('/profile', methods=["POST", 'GET'])
@login_required
def profile():
    user = User.query.filter_by(id=current_user.id).first()
    if request.method == 'POST':
        user.firstname = request.form.get('firstname')
        user.lastname = request.form.get('lastname')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        user.password = request.form.get('password')
        db.session.commit()
        flask.flash('Information updated!', category='success')
    return render_template('profile.html', menu=menu(), user=current_user)