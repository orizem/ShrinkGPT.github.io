# views.py

from time import sleep
from os import listdir
from io import BytesIO
from json import dumps
from flask import Blueprint, render_template
from flask import render_template, redirect, url_for, request, send_file, Response
from flask_login import current_user

# LOCAL IMPORTS
from .models import User, Chat
from .chatbot import ChatBot
from config import PROJECT_PATH

views = Blueprint("views", __name__)
chat_bot = ChatBot()

# FUNCTIONS
def generate_slide_show():
    images = get_all_images()
    
    # Instantly load image without sleep
    with open(rf"{PROJECT_PATH}\static\image\{images[-1]}", "rb") as img_file:
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + img_file.read() + b"\r\n") 
        
    while True:
        for image_name in images:
            with open(rf"{PROJECT_PATH}\static\image\{image_name}", "rb") as img_file:
                yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + img_file.read() + b"\r\n") 
            sleep(5)

def get_all_images():
    image_folder = rf"{PROJECT_PATH}\static\image"
    images = [img for img in listdir(image_folder)
              if img.startswith("WhatsApp") and
              (img.endswith(".jpg") or
              img.endswith(".jpeg") or
              img.endswith("png"))]
    return images

# ROUTES
@views.route("/")
def index():
    return render_template("index.html", user=current_user)

@views.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", err_msg=e), 404

@views.route("/profile", methods=["GET", "POST"])
def profile():
    from .models import db
    from .forms import ProfileForm
    
    if current_user.is_authenticated == False:
        # if user is logged in we get out of here
        return render_template("404.html", err_msg="Access Denied, Please Login First."), 404
    
    user = User.query.filter_by(username=current_user.username).first()
    if user is None:
        return redirect(url_for("views.index"))
    
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
    from .forms import ChatEdit

    if current_user.is_authenticated == False:
        # if user is logged in we get out of here
        return render_template("404.html", err_msg="Access Denied, Please Login First."), 404    
    
    user = User.query.filter_by(username=current_user.username).first()
    if user is None:
        return redirect(url_for("views.index"))
    
    chat_name_form = ChatEdit()
    
    return render_template("chat.html", user=user, chat_data=-1, chat_id=-1, name_form=chat_name_form)


@views.route("/get_chat/<int:chat_id>")
def get_chat(chat_id):
    from .forms import ChatEdit

    if current_user.is_authenticated == False:
        # if user is logged in we get out of here
        return redirect(url_for("views.index")) # render_template("404.html", err_msg="Access Denied, Please Login First."), 404    
    
    user = User.query.filter_by(username=current_user.username).first()
    if user is None:
        return redirect(url_for("views.index"))
    
    # Prevent from other users to access
    chat_data = Chat.query.filter_by(user_id=current_user.id, id=chat_id).first()
    if chat_data is None:
        return redirect(url_for("views.chat"))
    
    chat_name_form = ChatEdit()
    
    return render_template("chat.html", user=user, chat_data=chat_data.chat, chat_id=chat_id, name_form=chat_name_form)

@views.route("/get")
def get_bot_response():
    from .models import db
    
    user = User.query.filter_by(username=current_user.username).first()
    if user is None:
        return redirect(url_for("views.index"))
    
    chat_id = int(request.args.get("chatId"))
    fisrt_time = request.args.get("fisrtTime")
    user_msg = request.args.get("msg")
    date_time = request.args.get("dateTime")
    
    if chat_id != -1:
        current_chat = Chat.query.filter_by(user_id=current_user.id, id=chat_id).first()
    else:   
        if fisrt_time == "1":
            welcome_response = {
                "identifier": "bot", 
                "text": f"Hi { user.name.title() }, welcome to Shrink.io! Go ahead and send me a message.", 
                "date_time": date_time
            }
            new_chat = Chat(name=f"Chat_{len(user.chats)}", chat_json=dumps([welcome_response]), user_id=current_user.id)
            db.session.add(new_chat)
            db.session.commit()
        current_chat = user.chats[-1]

    existing_messages = current_chat.chat
    
    # TODO: Check for the real date time parameter for user (currently using the bot's time)
    new_message = {"identifier": "user", "text": user_msg, "date_time": date_time}
    existing_messages.append(new_message)
    
    bot_response = chat_bot.chatbot_response(user_msg)
    new_message = {"identifier": "bot", "text": bot_response, "date_time": date_time}
    existing_messages.append(new_message)
    
    current_chat.chat = existing_messages
    
    # Update chat history
    db.session.add(current_chat)
    db.session.commit()
    return bot_response

@views.route("/chat-edit")
def get_chat_edit():
    from .models import db
    
    user = User.query.filter_by(username=current_user.username).first()
    if user is None:
        return redirect(url_for("views.index"))
    
    name = request.args.get("name")
    id = request.args.get("id")
    
    # Prevent from other users to access
    current_chat = Chat.query.filter_by(user_id=user.id, id=id).first()
    if current_chat is None:
        return redirect(url_for("views.index"))
    
    current_chat.name = name
    db.session.add(current_chat)
    db.session.commit()
    return ""

@views.route("/get_image/<string:username>")
def get_image(username):
    if current_user.username != username:
        return redirect(url_for("views.index"))
    
    # Prevent from other users to access
    user = User.query.filter_by(username=username).first()
    if (user is not None) and (user.image_data is not None):
        return send_file(BytesIO(user.image_data), mimetype="image/jpeg")
    return send_file(rf"{PROJECT_PATH}\static\image\default.png", mimetype="image/jpeg")

@views.route("/slideshow")
def slideshow():
    return Response(generate_slide_show(), mimetype="multipart/x-mixed-replace; boundary=frame")
