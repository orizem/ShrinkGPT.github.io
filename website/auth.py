# auth.py

import pyqrcode

from io import BytesIO
from datetime import datetime
from flask import Blueprint, render_template, Response
from flask import render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user
from typing import Union

# LOCAL IMPORTS
from .models import User, Status, db
from .config.config import config
from .utils.utils import restricted_route_decorator

auth = Blueprint("auth", __name__)

AUTH: dict = config.read("auth", "AUTH")
STREAM_AUTH: dict = AUTH
STREAM_AUTH.update(config.read("auth", "STREAM"))


# ROUTES
@auth.route("/register", methods=["GET", "POST"])
def register() -> Union[str, Response]:
    """User Registration Route Handler

    This route manages both GET and POST requests for user registration.
    On GET requests, it displays the registration form.
    On POST requests, it processes the form submission and creates a new user account.

    The route performs the following operations:
    1. Checks if user is already logged in
    2. Validates the registration form
    3. Checks for username conflicts
    4. Handles user profile image upload
    5. Creates new user record in database
    6. Creates user status record
    7. Initiates two-factor authentication setup

    Returns
    -------
    Union[str, Response]
        - On GET: Rendered registration form template
        - On POST (success): Redirect to two-factor setup
        - On POST (failure): Redirect back to registration with error message
        - On authenticated access: Redirect to index page

    Notes
    -----
    Form Fields:
        - username: Unique user identifier
        - password: User's password
        - name: User's first name
        - lastname: User's last name
        - image: Optional profile image (defaults to 'default.png')

    Database Operations:
        - Creates new User record
        - Creates associated Status record
        - Initial status is set to 1 (active)

    Flash Messages:
        - "Deactivated user." - When username exists but is deactivated
        - "Username already exists." - When username is taken

    Session Data:
        - Sets 'username' in session for two-factor setup

    See Also
    --------
    .forms.RegisterForm : The form class handling registration data
    User : User model class
    Status : Status model class
    """
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

        user = User.query.filter_by(username=user.username).first()

        status_data = {
            "user_id": user.id,
            "status": 1,
            "register_date": datetime.today(),
            "last_deactivate_date": None,
        }
        status = Status(**status_data)
        db.session.add(status)
        db.session.commit()

        # redirect to the two-factor auth page, passing username in session
        session["username"] = user.username
        return redirect(url_for("auth.two_factor_setup"))
    return render_template("register.html", form=form)


@auth.route("/two_factor_setup", endpoint="two_factor_setup")
@restricted_route_decorator(check_session=True)
def two_factor_setup():
    """Two Factor Authentication Setup Route Handler

    Renders the two-factor authentication setup page with specific cache control headers.
    This route is protected by the restricted_route_decorator, which verifies
    the user has an active session before allowing access.

    The route enforces a strict no-cache policy to ensure the security of the 2FA setup process
    by preventing browser caching of sensitive setup information.

    Returns
    -------
    tuple
        A tuple containing three elements:
        
        - Rendered two-factor setup template
        - HTTP status code (200)
        - Dictionary of cache control headers with values:
            - Cache-Control: "no-cache, no-store, must-revalidate"
            - Pragma: "no-cache"
            - Expires: "0"

    Notes
    -----
    - Route is decorated with restricted_route_decorator to verify session
    - Prints AUTH variable for debugging/logging purposes
    - Implements strict no-cache policy through multiple headers
    - Template: "two-factor-setup.html"

    See Also
    --------
    restricted_route_decorator : Decorator that validates session
    """
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
def qrcode() -> tuple:
    """Generate QR Code for Two-Factor Authentication Setup

    Generates and returns a QR code image for setting up TOTP-based two-factor
    authentication. The QR code encodes the user's TOTP URI which can be scanned
    by authenticator apps like Google Authenticator or FreeOTP.

    The route performs the following operations:
    1. Retrieves user from database using session username
    2. Removes username from session for security
    3. Generates QR code from user's TOTP URI
    4. Returns QR code as SVG image stream

    Returns
    -------
    tuple
        A tuple containing three elements:
        - BytesIO stream containing SVG QR code image
        - HTTP status code (200)
        - STREAM_AUTH headers for secure content delivery

    Security Notes
    --------------
    - Protected by restricted_route_decorator
    - Removes username from session after use
    - QR code is generated dynamically per request
    - Uses secure TOTP protocol for 2FA

    Technical Details
    -----------------
    - QR code is generated using pyqrcode library
    - Output format is SVG with scale factor of 3
    - TOTP URI follows standard RFC 6238 format
    - Stream is delivered with authentication headers

    See Also
    --------
    restricted_route_decorator : Session validation decorator
    User.get_totp_uri : Method generating TOTP URI
    STREAM_AUTH : Security headers for stream delivery
    """
    user = User.query.filter_by(username=session["username"]).first()

    # for added security, remove username from session
    del session["username"]

    # render qrcode for FreeTOTP
    url = pyqrcode.create(user.get_totp_uri())
    stream = BytesIO()
    url.svg(stream, scale=3)
    return stream.getvalue(), 200, STREAM_AUTH


@auth.route("/login", methods=["GET", "POST"])
def login() -> Union[str, Response]:
    """User Login Route Handler

    Manages both GET and POST requests for user authentication. Validates user credentials
    and handles the user login process. Currently supports username/password authentication
    with commented infrastructure for TOTP-based two-factor authentication.

    The route performs the following operations:
    1. Checks if user is already logged in
    2. Validates the login form submission
    3. Verifies user credentials
    4. Checks user account status
    5. Creates user session on successful login

    Returns
    -------
    Union[str, Response]
        - On GET: Rendered login form template
        - On POST (success): Redirect to index page with success message
        - On POST (failure): Redirect back to login with error message
        - On authenticated access: Redirect to index page

    Authentication Process
    ----------------------
    1. Username lookup in database
    2. Password verification using secure hash comparison
    3. (Commented) TOTP token verification
    4. User status verification (active/deactivated)

    Flash Messages
    --------------
    - "Invalid username, password or token." - When credentials are incorrect
    - "Deactivated user." - When account is deactivated
    - "You are now logged in!" - On successful authentication

    Notes
    -----
    - Uses Flask-Login for session management
    - Form validation through WTForms
    - Password verification uses secure comparison
    - TOTP verification is currently commented out
    - Redirects authenticated users to index

    See Also
    --------
    .forms.LoginForm : The form class handling login data
    User : User model with verification methods
    login_user : Flask-Login function for session creation
    """
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
            # or not user.verify_totp(form.token.data)
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
