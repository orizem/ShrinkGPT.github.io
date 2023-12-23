# views.py

from time import sleep
from os import listdir
from io import BytesIO
from flask import Blueprint, render_template
from flask import render_template, redirect, url_for, request, send_file, Response
from flask_login import current_user

# LOCAL IMPORTS
from .models import User
from .chatbot import ChatBot

PROJECT_PATH = r"C:\Users\User\Documents\MEGA\MEGAsync\Study\Python\ShrinkGPT.github.io\website"

views = Blueprint('views', __name__)
chat_bot = ChatBot()


@views.route('/')
def index():
    return render_template('index.html', user=current_user)

@views.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', err_msg=e), 404

@views.route("/profile", methods=['GET', 'POST'])
def profile():
    from .models import db
    from .forms import ProfileForm
    
    if current_user.is_authenticated == False:
        # if user is logged in we get out of here
        return render_template('404.html', err_msg="Access Denied, Please Login First."), 404
    
    user = User.query.filter_by(username=current_user.username).first()
    if user is None:
        return redirect(url_for('views.index'))
    
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

@views.route("/chat")
def chat():
    if current_user.is_authenticated == False:
        # if user is logged in we get out of here
        return render_template('404.html', err_msg="Access Denied, Please Login First."), 404    
    
    user = User.query.filter_by(username=current_user.username).first()
    if user is None:
        return redirect(url_for('views.index'))
    
    previous_chats = [
        {"id": 1, "name": "Chat 1", "content": "Chat 1 Content..."},
        {"id": 2, "name": "Chat 2", "content": "Chat 2 Content..."},
        # Add more chat entries as needed
    ]
    return render_template("chat.html", user=user, previous_chats=previous_chats)


@views.route('/get_chat/<int:chat_id>')
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

@views.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return chat_bot.chatbot_response(userText)


@views.route('/get_image/<string:username>')
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
        sleep(5)

def get_all_images():
    image_folder = rf'{PROJECT_PATH}\static\image'
    images = [img for img in listdir(image_folder)
              if img.startswith("WhatsApp") and
              (img.endswith(".jpg") or
              img.endswith(".jpeg") or
              img.endswith("png"))]
    return images

@views.route('/slideshow')
def slideshow():
    return Response(generate_slide_show(), mimetype='multipart/x-mixed-replace; boundary=frame')
