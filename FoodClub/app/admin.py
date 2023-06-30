import flask
from flask import Blueprint,render_template, request
from flask_login import current_user, login_required

from .menu import menu
from .models import Recipe,User, Category
from . import db

adminBlueprint = Blueprint('admin', __name__)

def total_users():
    users = User.query.count()
    return users

def total_recipes():
    recipes = Recipe.query.count()
    print(recipes)
    return recipes

def get_recipe(id):
    recipe = Recipe.query.filter_by(id=id).first()
    return recipe


@adminBlueprint.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.role == 'admin' or 'moderator':
        return render_template('admin.html', menu=menu(), user=current_user,
                               total_users=total_users(), total_recipes=total_recipes())
    else:
        return 'Access Denied'

@adminBlueprint.route('/users', methods=['GET', 'POST'])
@login_required
def dashboard_users():
    users = User.query.all()
    return render_template('admin_users.html', menu=menu(), user=current_user,
                           users=users)

@adminBlueprint.route('/new-role', methods=['GET', 'POST'])
@login_required
def dashboard_user_role():
    if request.method == "POST":
        user_id = request.form.get('user_id')
        role = request.form.get('user_role')
        user = User.query.filter_by(id=user_id).first()
        user.role = role
        db.session.commit()
        flask.flash(f'User {user.id} now is {role}!', category='success')

    return render_template('admin_new_role.html', menu=menu(), user=current_user)


@adminBlueprint.route('/recipes', methods=['GET', 'POST'])
@login_required
def dashboard_recipes():
    recipes = Recipe.query.all()
    return render_template('admin_recipes.html', menu=menu(), user=current_user, recipes=recipes)


@adminBlueprint.route('/recipes-submission', methods=['GET', 'POST'])
@login_required
def dashboard_recipes_for_submit():
    recipes = Recipe.query.filter_by(status='need-submit').all()
    if request.method == "POST":
        recipe_id_publish = request.form.get('publish')
        recipe_id_return = request.form.get('return')
        if request.form.get('publish'):
            recipe = get_recipe(recipe_id_publish)
            recipe.status = 'Published'
            flask.flash('Recipe published!', category='success')
        elif request.form.get('return'):
            recipe = get_recipe(recipe_id_return)
            recipe.status = 'Drafts'
            flask.flash('Recipe returned to drafts!', category='success')
        db.session.commit()

    return render_template('admin_recipes_for_submit.html', menu=menu(), user=current_user, recipes=recipes)


@adminBlueprint.route('/manage-categories', methods=['GET', 'POST'])
@login_required
def dashboard_categories():
    categories = Category.query.all()
    rename_button = 0
    rename_id = -1
    if request.method == "POST":
        if request.form.get('category_name'):              #is not empty
            new_category_name = request.form.get('category_name')
            new_category = Category(name=new_category_name)
            db.session.add(new_category)
            db.session.commit()
            flask.flash(f'Category {new_category_name} added!', category='success')

        elif  request.form.get('delete'):
            category = Category.query.filter_by(id=request.form.get('delete')).first()
            db.session.delete(category)
            db.session.commit()
            flask.flash(f"Category {category.name} deleted!", category='success')

        # elif request.form.get('rename'):
        #     category = Category.query.filter_by(id=request.form.get('rename')).first()
        #     rename_button = 1
        #     rename_id = category.id
        #     print(rename_id)
        #     if request.method == 'POST':
        #         print('submit',request.form.get('submit_rename'))
        #         if request.form.get('submit_rename'):
        #             flask.flash(f"Category renamed!", category='success')
    categories = Category.query.all()
    return render_template('admin_manage_categories.html', menu=menu(), user=current_user,categories=categories, rename_button=rename_button,rename_id=rename_id)


@adminBlueprint.route('/manage-categories', methods=['GET', 'POST'])
@login_required
def dashboard_categories_all():
    categories = Category.query.all()
    return render_template('admin_manage_categories.html', menu=menu(), user=current_user, categories=categories)
