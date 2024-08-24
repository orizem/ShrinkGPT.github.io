# auth.py

import pyqrcode

from io import BytesIO
from flask import Blueprint, render_template
from flask import render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user

# LOCAL IMPORTS
from .models import User, db
from .config.config import config
from .utils.utils import restricted_route_decorator

auth = Blueprint("auth", __name__)

AUTH: dict = config.read("auth", "AUTH")
STREAM_AUTH: dict = AUTH
STREAM_AUTH.update(config.read("auth", "STREAM"))


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
            if user.status == -1:
                flash("Deactivated user.")
                return redirect(url_for("auth.register"))
            
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


@auth.route("/two_factor_setup", endpoint="two_factor_setup")
@restricted_route_decorator(check_session=True)
def two_factor_setup():
    print(AUTH)
    return (
        render_template("two-factor-setup.html"),
        200,
        {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@auth.route("/qrcode", endpoint="qrcode")
@restricted_route_decorator(check_session=True)
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
    import sys

    if current_user.is_authenticated:
        # if user is logged in we get out of here
        return redirect(url_for("views.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if (
            user is None
            or not user.verify_password(form.password.data)
            or not user.verify_totp(form.token.data)
        ):
            flash("Invalid username, password or token.")
            return redirect(url_for("auth.login"))

        if user.status == -1:
            flash("Deactivated user.")
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
