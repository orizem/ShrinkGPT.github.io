# init.py

# import os
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

# LOCAL IMPORTS
from .models import db
from .views import page_not_found

# create application instance
# env = os.environ.get("FLASK_ENV", "dev")
# env = os.environ.get("FLASK_APP", "main.py")

def create_app():
    app = Flask(__name__)
    app.static_folder = "static"
    app.config.from_object("config")
    Bootstrap(app)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from .models import User
    
    create_database(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # page not found
    app.register_error_handler(404, page_not_found)

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .views import views as views_blueprint
    app.register_blueprint(views_blueprint)
    return app

def create_database(app):
    with app.app_context():
        db.create_all()