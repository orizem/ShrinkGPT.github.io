import os
import base64
from io import BytesIO
from flask import Flask, render_template, redirect, url_for, flash, session, abort, request, send_file, Response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField
from werkzeug.utils import secure_filename
from wtforms.validators import Length, EqualTo, InputRequired
import onetimepass
import pyqrcode

import nltk
# nltk.download('popular')
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np

from keras.models import load_model
model = load_model('model.h5')
import json
import random
from io import BytesIO
import imageio as iio
import time

PROJECT_PATH = r"C:\Users\User\Documents\MEGA\MEGAsync\Study\Python\ShrinkGPT.github.io\flask_shrink_gpt"

intents = json.loads(open("data.json").read())
words = pickle.load(open("texts.pkl",'rb'))
classes = pickle.load(open("labels.pkl",'rb'))
# intents = json.loads(open(PROJECT_PATH + r"\data.json").read())
# words = pickle.load(open(PROJECT_PATH + r"\texts.pkl",'rb'))
# classes = pickle.load(open(PROJECT_PATH + r"\labels.pkl",'rb'))

# create application instance
env = os.environ.get('FLASK_ENV', 'dev')

db = SQLAlchemy()

app = Flask(__name__)
app.static_folder = 'static'

# initialize extensions
bootstrap:Bootstrap = None
lm:LoginManager = None

app.config.from_object('config')

db.init_app(app)

class User(UserMixin, db.Model):
    """User model."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    name = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    image_data = db.Column(db.LargeBinary, nullable=True)
    image_filename = db.Column(db.String(20), nullable=True, default='/static/image/default.png')
    password_hash = db.Column(db.String(128))
    otp_secret = db.Column(db.String(16))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.otp_secret is None:
            # generate a random secret
            self.otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_totp_uri(self):
        return f'otpauth://totp/Shrink.io:{self.username}?secret={self.otp_secret}&issuer=Shrink.io'

    def verify_totp(self, token):
        return onetimepass.valid_totp(token, self.otp_secret)

with app.app_context():
    
    # initialize extensions        
    bootstrap = Bootstrap(app)
    # db = SQLAlchemy(app)
    lm = LoginManager(app)
    
    db.create_all()

def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result

def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)
    return res

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', err_msg=e), 404

@app.route("/chat")
def chat():
    if current_user.is_authenticated == False:
        # if user is logged in we get out of here
        return render_template('404.html', err_msg="Access Denied, Please Login First."), 404    
    
    user = User.query.filter_by(username=current_user.username).first()
    if user is None:
        return redirect(url_for('index'))
    
    previous_chats = [
        {"id": 1, "name": "Chat 1", "content": "Chat 1 Content..."},
        {"id": 2, "name": "Chat 2", "content": "Chat 2 Content..."},
        # Add more chat entries as needed
    ]
    return render_template("chat.html", user=user, previous_chats=previous_chats)

@app.route('/get_chat/<int:chat_id>')
def get_chat(chat_id):
    previous_chats = [
        {"id": 1, "name": "Chat 1", "content": "Chat 1 Content..."},
        {"id": 2, "name": "Chat 2", "content": "Chat 2 Content..."},
        # Add more chat entries as needed
    ]
    # Fetch chat content based on chat_id (you can modify this based on your data source)
    chat = next((chat for chat in previous_chats if chat['id'] == chat_id), None)
    if chat:
        return render_template('chat_content.html', chat=chat)
    else:
        return render_template('404.html', err_msg="Chat not found"), 404

@app.route("/profile", methods=['GET', 'POST'])
def profile():
    if current_user.is_authenticated == False:
        # if user is logged in we get out of here
        return render_template('404.html', err_msg="Access Denied, Please Login First."), 404
    
    user = User.query.filter_by(username=current_user.username).first()
    if user is None:
        return redirect(url_for('index'))
    
    form = ProfileForm(obj=user)
    if form.validate_on_submit():
        form.populate_obj(user)
        
        if form.image.data is not None:
            image = form.image.data
            # Read the binary data of the image
            image_data = image.read()
            image_filename = image.filename
            
            user.image_data = image_data
            user.image_filename = image_filename
        
        db.session.add(user)
        # Commit the changes
        db.session.commit()
        
    return render_template("profile.html", user=user, form=form)

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return chatbot_response(userText)

@lm.user_loader
def load_user(user_id):
    """User loader callback for Flask-Login."""
    return User.query.get(int(user_id))


class RegisterForm(FlaskForm):
    """Registration form."""
    username = StringField('Username', validators=[InputRequired(), Length(1, 64)])
    name = StringField('Name', validators=[InputRequired(), Length(1, 64)])
    lastname = StringField('Lastname', validators=[InputRequired(), Length(1, 64)])
    image = FileField('Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    password = PasswordField('Password', validators=[InputRequired()])
    password_again = PasswordField('Password again', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """Login form."""
    username = StringField('Username', validators=[InputRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[InputRequired()])
    token = StringField('Token', validators=[InputRequired(), Length(6, 6)], render_kw={'autocomplete': 'off'})
    submit = SubmitField('Login')

class ProfileForm(FlaskForm):
    """Profile form."""
    name = StringField('Name', validators=[Length(1, 64)])
    lastname = StringField('Lastname', validators=[Length(1, 64)])
    image = FileField('Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Save')


@app.route('/')
def index():
    return render_template('index.html', user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if current_user.is_authenticated:
        # if user is logged in we get out of here
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            flash('Username already exists.')
            return redirect(url_for('register'))
        
        # add image
        image = form.image.data
        # Read the binary data of the image
        if image is not None:
            image_data = image.read()
        else:
            image_data = iio.imread("/static/image/default.png")
        image_filename = image_data.filename
            
        
        # add new user to the database
        user = User(username=form.username.data, password=form.password.data, name=form.name.data, lastname=form.lastname.data, image_data=image_data, image_filename=image_filename)
        db.session.add(user)
        db.session.commit()

        # redirect to the two-factor auth page, passing username in session
        session['username'] = user.username
        return redirect(url_for('two_factor_setup'))
    return render_template('register.html', form=form)


@app.route('/twofactor')
def two_factor_setup():
    if 'username' not in session:
        return redirect(url_for('index'))
    user = User.query.filter_by(username=session['username']).first()
    if user is None:
        return redirect(url_for('index'))
    # since this page contains the sensitive qrcode, make sure the browser
    # does not cache it
    return render_template('two-factor-setup.html'), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@app.route('/qrcode')
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        # if user is logged in we get out of here
        return redirect(url_for('index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data) or \
                not user.verify_totp(form.token.data):
            flash('Invalid username, password or token.')
            return redirect(url_for('login'))

        # log user in
        login_user(user)
        flash('You are now logged in!')
        return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """User logout route."""
    logout_user()
    return redirect(url_for('index'))

@app.route('/get_image/<string:username>')
def get_image(username):
    user = User.query.filter_by(username=username).first()
    return send_file(BytesIO(user.image_data), mimetype='image/jpeg')

def generate_slide_show():
    i = 0
    while True:
        images = get_all_images()
        image_name = images[i]
        im = open(rf'{PROJECT_PATH}\static\image\\' + image_name, 'rb').read()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + im + b'\r\n')
        i += 1
        if i >= len(images):
            i = 0
        time.sleep(5)

def get_all_images():
    image_folder = rf'{PROJECT_PATH}\static\image'
    images = [img for img in os.listdir(image_folder)
              if img.startswith("WhatsApp") and
              (img.endswith(".jpg") or
              img.endswith(".jpeg") or
              img.endswith("png"))]
    return images

@app.route('/slideshow')
def slideshow():
    return Response(generate_slide_show(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True) # public
    # app.run(host="127.0.0.1", port=8080, debug=True)
