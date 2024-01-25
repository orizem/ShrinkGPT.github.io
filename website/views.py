# views.py

from io import BytesIO
from json import dumps
from flask import Blueprint, render_template
from flask import Response, render_template, redirect, url_for, send_file, request
from flask_login import current_user

# LOCAL IMPORTS
from .models import User, Chat
from .chatbot import ChatBot
from .utils import generate_slide_show, safe_send_default_image
from .text2speech import Text2Speech

views = Blueprint("views", __name__)
chat_bot = ChatBot()

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
def get_chat(chat_id: int):
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
def get_image(username: str):
    
    if current_user.username != username:
        return redirect(url_for("views.index"))
    
    # Prevent from other users to access
    user = User.query.filter_by(username=username).first()
    if (user is not None) and (user.image_data is not None):
        return send_file(BytesIO(user.image_data), mimetype="image/jpeg")
    
    return safe_send_default_image()

@views.route("/slideshow/")
@views.route("/slideshow/<string:start_with>")
def slideshow(start_with: str=""):
    """Slideshow 
    Using this route (`/slideshow`) will return a slideshow of images located in the `static/image` folder.
    If you want to choose what all file names should start with, use `/slideshow/<START_WITH>`.
    The start with parameter can also be passed as a list separated by semicolon (`;`).

    Parameters
    ----------
    start_with : str, optional
        A string or list of strings that the desired 
        images file name should start with.
        Using only /slideshow will return all images 
        located in the `static/image` folder, by default "".
    Returns
    -------
    Response
        Response of the desired images.
    """
    start_with = start_with.lower()
    if len(start_with) > 2:
        if (start_with[0] == "[") & (start_with[-1] == "]"):
            start_with = start_with[1:-1].split(";")
        else:
            start_with = start_with
    return Response(generate_slide_show(start_with=start_with), mimetype="multipart/x-mixed-replace; boundary=frame")

@views.route("/text2speech/<string:text>")
def text2speech(text: str=""):
    try:
        speech = Text2Speech()
        speech.say(text)
    except:
        pass
    return Response()
