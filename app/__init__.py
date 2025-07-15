from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from app.admin.admin_routes import admin_bp


db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)  # create the Flask app
    app.config.from_object('app.config.Config')  # load the config file

    db.init_app(app)  # initialize the database
    Migrate(app, db)  # initialize the migration engine
    login_manager.init_app(app)  # initialize the login manager
    bcrypt.init_app(app)  # initialize the bcrypt

    login_manager.login_view = 'auth.login'  # set the login view

    # Register blueprints
    from app.routes import main  # import the blueprint
    from app.routes import tasks  # import the blueprint
    from app.auth import auth  # import the auth blueprint
    app.register_blueprint(main)  # register the main blueprint
    app.register_blueprint(tasks, url_prefix="/tasks")  # register the blueprint
    app.register_blueprint(auth, url_prefix="/auth")  # register the auth blueprint
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app  # return the Flask app


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))










