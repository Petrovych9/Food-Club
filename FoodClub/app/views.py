import os.path

import flask
import base64
from flask import Blueprint,render_template, request, url_for, redirect
from flask_login import current_user, login_required
from .menu import menu
from .models import Recipe
from . import db


mainBlueprint = Blueprint('main', __name__)


#main
@mainBlueprint.route("/", methods=["GET", ' POST'])
@login_required
def home():
    return render_template('base.html', menu=menu(), user=current_user)

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

@mainBlueprint.route('/new-recipe', methods=["POST", 'GET'])
@login_required
def new_recipe():
    if request.method == "POST":
        dish_name = request.form['dish_name']
        cooking_time = request.form['cooking_time']
        description = request.form['description']
        ingredients = request.form['ingredients']
        image = request.files['photo']
        button = request.form['button']

        print(request.form)
        if dish_name != '':
            if button == 'Drafts':
                status = 'Drafts'
            elif button == 'Published':
                status = 'Published'
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
            db.session.add(new_rec)
            db.session.commit()
            if status =='Published':
                flask.flash("Recipe Published!", category="success")
            elif status == 'Drafts':
                flask.flash("Recipe in your drafts!", category="success")
            else:flask.flash("Occur some error. Try again", category="error")
        else: flask.flash("Enter a dish name", category='error')
    return render_template('new-recipe.html', menu=menu(), user=current_user)


@mainBlueprint.route('/my-drafts', methods=["POST", 'GET'])
@login_required
def draft_recipes():
    if request.form:
        id = request.form['id']
        print(request.form)
        recipe = Recipe.query.filter_by(id=id).first()
        return redirect(f'/my-drafts-edit/{id}')

    recipes = Recipe.query.filter_by(status='Drafts', user_id=current_user.id).all()
    return render_template('my-drafts.html', menu=menu(), user=current_user, recipes=recipes)


@mainBlueprint.route('/my-drafts-edit/<int:recipe_id>', methods=["POST", 'GET'])
@login_required
def update_draft(recipe_id):
    recipe = Recipe.query.filter_by(id=recipe_id).first()
    if request.method == 'POST':
        recipe.dish_name = request.form['dish_name']
        recipe.cooking_time = request.form['cooking_time']
        recipe.description = request.form['description']
        recipe.ingredients = request.form['ingredients']
        image = request.files['photo']
        if image.filename == "":
            print('Photo left old')
        else:
            recipe.image=convert_image(image)
            print("Photo updated")

        button = request.form['button']
        status = recipe.status
        if button == 'Drafts':
            recipe.status ='Drafts'
            db.session.commit()
            print(recipe.status, recipe.id)
            flask.flash("Recipe saved to drafts!", category='success')

        elif button == 'Published':
            recipe.status = 'Published'
            db.session.commit()
            print(recipe.status, recipe.id)
            flask.flash("Recipe published!", category='success')

        elif button == 'Delete':
            db.session.delete(recipe)
            db.session.commit()
            flask.flash("Recipe deleted!", category='success')
        else:
            recipe.status = "Drafts"
            recipe.dish_name = 'Causing some error'
            db.session.commit()
            flask.flash('Error!!! Set "Drafts" status for recipe. Edit and publish its later.', category='error')

        return redirect(url_for('main.draft_recipes'))
    return render_template('my-drafts-edit.html',menu=menu(), user=current_user, recipe=recipe, id=recipe.id)


@mainBlueprint.route('/all-recipes', methods=["POST", 'GET'])
@login_required
def all_recipes():
    recipes = Recipe.query.filter_by(status='Published').all()
    return render_template('all-recipes.html', menu=menu(), user=current_user, recipes=recipes)


@mainBlueprint.route('/profile')
@login_required
def profile():
    return render_template('profile.html', menu=menu(), user=current_user)