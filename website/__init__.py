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
    """Create and configure the Flask application

    This function sets up and initializes the Flask application with 
    the necessary configurations, extensions, and blueprints. It also 
    registers the user loader for the login manager and error handlers.

    The following components are initialized:
    - Flask application instance
    - Bootstrap for front-end styling
    - Database (SQLAlchemy)
    - Login Manager for user authentication
    - Error handler for 404 (page not found)
    - Blueprints for authentication, admin, and general views

    Returns
    -------
    Flask
        The configured Flask application instance.

    Examples
    --------
    >>> app = create_app()
    The application is configured, and blueprints for auth, admin, and views 
    are registered, making it ready to run.
    """
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
    """Create the database tables

    This function creates the necessary database tables by calling 
    `db.create_all()` within the app's context.

    It is intended to be run when the application is first set up or 
    when new database models are added.

    Parameters
    ----------
    app : Flask
        The Flask application instance that provides the app context 
        for creating the tables.

    Returns
    -------
    None
        This function does not return anything, it only modifies the 
        database.

    Examples
    --------
    >>> create_database(app)
    Creates the tables defined by the app's models in the database.
    """
    with app.app_context():
        db.create_all()


def create_admin(app):
    """Create default admin user and admin entry

    This function checks if there are any existing admins in the database. 
    If no admins are found, it creates a default admin user and adds it 
    to the database, followed by creating an associated admin entry.

    It is useful for setting up a default administrative account on 
    the first run of the application.

    Parameters
    ----------
    app : Flask
        The Flask application instance that provides the app context 
        for creating the admin user.

    Returns
    -------
    None
        This function does not return anything, it only modifies the 
        database by adding a default admin user and entry.

    Examples
    --------
    >>> create_admin(app)
    If no admins exist, a default admin user is created and added to 
    the database.
    """
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
