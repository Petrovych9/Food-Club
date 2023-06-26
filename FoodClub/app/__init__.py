from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()
DB_NAME = 'database.db'


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = 'ajnjfgfhfn!1tyuiop[92vgb9r5'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    Migrate().init_app(app, db)

    # Register blueprints
    from .views import mainBlueprint
    from .admin import adminBlueprint
    from .auth import authBlueprint

    app.register_blueprint(mainBlueprint, url_prefix='/')
    app.register_blueprint(adminBlueprint, url_prefix='/admin/')
    app.register_blueprint(authBlueprint, url_prefix='/auth/')

    from .models import User, Recipe

    create_database(app)

    migrate = Migrate(app,db)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.signin'  # sets the endpoint for the login page. will redirect to the login page
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        # print("Database created!")
