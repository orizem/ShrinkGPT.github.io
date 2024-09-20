# init.py

# import os
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask import session
from datetime import datetime

# LOCAL IMPORTS
from .models import Admin, User, Status, db
from .views import page_not_found


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
    create_admin(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # page not found
    app.register_error_handler(404, page_not_found)

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    # blueprint for admin routes in our app
    from .admin import admin as admin_blueprint

    app.register_blueprint(admin_blueprint)

    # blueprint for non-auth parts of app
    from .views import views as views_blueprint

    app.register_blueprint(views_blueprint)
    return app


def create_database(app):
    with app.app_context():
        db.create_all()

def create_admin(app):
    with app.app_context():
        # Check if needs to add a default admin
        is_there_any_admins = Admin.query.all()
        if len(is_there_any_admins) > 0:
            return
    
        # add new user to the database
        user_data = {
            "username": "admin",
            "password": "eK9HIEXwVNin8d2AYeIlS8f",
            "name": "admin",
            "lastname": "admin",
            "image_data": None,
            "image_filename": "default.png",
        }
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()

        user = User.query.filter_by(username=user.username).first()

        status_data = {
            "user_id": user.id,
            "status": 0,
            "register_date": datetime.today(),
            "last_deactivate_date": None,
        }  
        status = Status(**status_data)
        db.session.add(status)
        db.session.commit()

        new_admin = Admin(user_id=1)

        # Add the new admin entry to the session
        db.session.add(new_admin)

        # Commit the session to save the changes to the database
        db.session.commit()

