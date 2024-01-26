# auth.py

import pyqrcode

from io import BytesIO
from typing import Callable
from flask import Blueprint, render_template
from flask import  render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user

# LOCAL IMPORTS
from .config import Config
from .models import User, db

auth = Blueprint("auth", __name__)
config = Config()

AUTH = config.read("auth", "AUTH")
STREAM_AUTH = AUTH
STREAM_AUTH.update(config.read("auth", "STREAM"))

# DECORATORS
def auth_restricted_route_decorator(func: Callable):
    """Restricted Route Decorator 
    Check if the user session is valid, if not,
    it redirected to 404.
    In addition, the decorator check if the user exists,
    if not, will be redirected to index page.   
    
    Must define endpoint for each route using this decorator.
    The decorator should be right above the function in 
    order to run properly.

    Parameters
    ----------
    func : Callable
        The function to wrap with authentication checking.
    """
    def wrapped(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("views.index"))
        user = User.query.filter_by(username=session["username"]).first()
        if user is None:
            return redirect(url_for("views.index"))
        
        res = func(*args, **kwargs)
        return res
    return wrapped

# ROUTES    
@auth.route("/register", methods=["GET", "POST"])
def register():
    """User registration route."""
    from .forms import RegisterForm
    
    if current_user.is_authenticated:
        # if user is logged in we get out of here
        return redirect(url_for("views.index"))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            flash("Username already exists.")
            return redirect(url_for("auth.register"))
        
        # add image
        # Read the binary data of the image
        if form.image.data is not None:
            image = form.image.data
            image_data = image.read()
            image_filename = image.filename
        else:
            image_data = None
            image_filename = "default.png"
        
        # add new user to the database
        user_data = {
            "username": form.username.data,
            "password": form.password.data,
            "name": form.name.data,
            "lastname": form.lastname.data,
            "image_data": image_data,
            "image_filename": image_filename,
        }
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()

        # redirect to the two-factor auth page, passing username in session
        session["username"] = user.username
        return redirect(url_for("auth.two_factor_setup"))
    return render_template("register.html", form=form)


@auth.route("/twofactor", endpoint="twofactor")
@auth_restricted_route_decorator
def two_factor_setup():
    return render_template("two-factor-setup.html"), 200, AUTH


@auth.route("/qrcode", endpoint="qrcode")
@auth_restricted_route_decorator
def qrcode():
    user = User.query.filter_by(username=session["username"]).first()

    # for added security, remove username from session
    del session["username"]

    # render qrcode for FreeTOTP
    url = pyqrcode.create(user.get_totp_uri())
    stream = BytesIO()
    url.svg(stream, scale=3)
    return stream.getvalue(), 200, STREAM_AUTH


@auth.route("/login", methods=["GET", "POST"])
def login():
    """User login route."""
    from .forms import LoginForm
    
    if current_user.is_authenticated:
        # if user is logged in we get out of here
        return redirect(url_for("views.index"))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data) or \
                not user.verify_totp(form.token.data):
            flash("Invalid username, password or token.")
            return redirect(url_for("auth.login"))

        # log user in
        login_user(user)
        flash("You are now logged in!")
        return redirect(url_for("views.index"))
    return render_template("login.html", form=form)


@auth.route("/logout")
def logout():
    """User logout route."""
    logout_user()
    return redirect(url_for("views.index"))