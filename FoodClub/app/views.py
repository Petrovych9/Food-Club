import os.path

import flask
import base64
from flask import Blueprint,render_template, request, url_for, redirect
from flask_login import current_user, login_required
from .menu import menu
from .models import Recipe, User, Category, recipe_category
from . import db


mainBlueprint = Blueprint('main', __name__)


#main
@mainBlueprint.route("/", methods=["GET", ' POST'])
@login_required
def home():
    recipes = Recipe.query.filter_by(status='Published').order_by(Recipe.id.desc()).limit(6).all()
    return render_template('home.html', menu=menu(), user=current_user, recipes=recipes)

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
    if categories:
        for category in categories:
            cat = Category.query.get(category)
            recipe.categories.append(cat)
        return 1
    else:
        if recipe.status != 'Drafts':
            flask.flash("Your recipe in your drafts! You can send for review after selection category.", category='error')
            recipe.status = "Drafts"
            return 0
        else:return 1

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
            if button == 'Drafts':
                status = 'Drafts'
            elif button == 'need-submit':
                status = 'need-submit'
            else:
                flask.flash('Default status', category='error')
                status = "default"

            new_rec = Recipe(
                dish_name=dish_name,
                cooking_time=cooking_time,
                description=description,
                ingredients=ingredients,
                image=convert_image(image),
                status=status,
                user_id=current_user.id)

            add_categ = add_recipe_category(new_rec, selected_categories)

            db.session.add(new_rec)
            db.session.commit()
            if add_categ != 0:
                if new_rec.status =='need-submit':
                    flask.flash("Recipe sent for submission!", category="success")
                elif new_rec.status == 'Drafts':
                    flask.flash("Recipe in your drafts!", category="success")
                else:flask.flash("Occur some error. Try again", category="error")

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

        recipe.categories.clear()
        add_categor = add_recipe_category(recipe, new_selected_categories)

        if image.filename != "":
            recipe.image=convert_image(image)
            print("Photo updated")

        if button == 'Drafts':
            recipe.status = 'Drafts'
            db.session.commit()
            flask.flash("Recipe saved to drafts!", category='success')
        elif button == 'Delete':
            db.session.delete(recipe)
            db.session.commit()
            flask.flash("Recipe deleted!", category='success')

        elif not selected_categories:
            flask.flash("Your recipe in your drafts! You can send for review after selection category.",
                        category='error')
        elif  selected_categories:
            button == 'need-submit'
            recipe.status = 'need-submit'
            db.session.commit()
            flask.flash("Recipe sent for submission!", category="success")
        else:
            recipe.status = "Drafts"
            recipe.dish_name = 'Causing some error'
            db.session.commit()
            flask.flash('Error!!! Set "Drafts" status for recipe. Edit and publish its later.', category='error')


        return redirect(url_for('main.draft_recipes'))
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