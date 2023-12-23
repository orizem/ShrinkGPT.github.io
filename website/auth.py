# auth.py

import pyqrcode

from io import BytesIO
from imageio import imread
from flask import Blueprint, render_template
from flask import Blueprint, render_template
from flask import  render_template, redirect, url_for, flash, session, abort
from flask_login import login_user, logout_user, current_user

# LOCAL IMPORTS
from .models import User, db

auth = Blueprint('auth', __name__)
    
@auth.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    from .forms import RegisterForm
    
    if current_user.is_authenticated:
        # if user is logged in we get out of here
        return redirect(url_for('views.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            flash('Username already exists.')
            return redirect(url_for('auth.register'))
        
        # add image
        image = form.image.data
        # Read the binary data of the image
        if image is not None:
            image_data = image.read()
        else:
            image_data = imread("/static/image/default.png")
        image_filename = image_data.filename
            
        
        # add new user to the database
        user = User(username=form.username.data, password=form.password.data, name=form.name.data, lastname=form.lastname.data, image_data=image_data, image_filename=image_filename)
        db.session.add(user)
        db.session.commit()

        # redirect to the two-factor auth page, passing username in session
        session['username'] = user.username
        return redirect(url_for('auth.two_factor_setup'))
    return render_template('register.html', form=form)


@auth.route('/twofactor')
def two_factor_setup():
    if 'username' not in session:
        return redirect(url_for('views.index'))
    user = User.query.filter_by(username=session['username']).first()
    if user is None:
        return redirect(url_for('views.index'))
    # since this page contains the sensitive qrcode, make sure the browser
    # does not cache it
    return render_template('two-factor-setup.html'), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@auth.route('/qrcode')
def qrcode():
    if 'username' not in session:
        abort(404)
    user = User.query.filter_by(username=session['username']).first()
    if user is None:
        abort(404)

    # for added security, remove username from session
    del session['username']

    # render qrcode for FreeTOTP
    url = pyqrcode.create(user.get_totp_uri())
    stream = BytesIO()
    url.svg(stream, scale=3)
    return stream.getvalue(), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    from .forms import LoginForm
    
    if current_user.is_authenticated:
        # if user is logged in we get out of here
        return redirect(url_for('views.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data) or \
                not user.verify_totp(form.token.data):
            flash('Invalid username, password or token.')
            return redirect(url_for('auth.login'))

        # log user in
        login_user(user)
        flash('You are now logged in!')
        return redirect(url_for('views.index'))
    return render_template('login.html', form=form)


@auth.route('/logout')
def logout():
    """User logout route."""
    logout_user()
    return redirect(url_for('views.index'))