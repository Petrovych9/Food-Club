from flask import Blueprint,render_template
from flask_login import current_user, login_required

from .menu import menu
from .models import Recipe,User

adminBlueprint = Blueprint('admin', __name__)

def total_users():
    users = User.query.count()
    return users

def total_recipes():
    recipes = Recipe.query.count()
    print(recipes)
    return recipes


@adminBlueprint.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.role == 'admin':
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


@adminBlueprint.route('/recipes', methods=['GET', 'POST'])
@login_required
def dashboard_recipes():
    recipes = Recipe.query.all()
    return render_template('admin_recipes.html', menu=menu(), user=current_user, recipes=recipes)
