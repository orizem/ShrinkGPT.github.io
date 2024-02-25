# views.py

from flask import flash
from io import BytesIO
from json import dumps
from typing import Any
from flask_login import current_user
from flask import Blueprint, Response, render_template, redirect, url_for, send_file, request
from zoneinfo import ZoneInfo

# LOCAL IMPORTS
from .models import User, Chat
from .utils.chatbot import ChatBot
from .utils.text2speech import Text2Speech
from .utils.utils import generate_slide_show, safe_send_default_image, get_current_user, restricted_route_decorator, html_encode

views = Blueprint("views", __name__)
chat_bot = ChatBot()

# ROUTES
@views.route("/")
def index():
    """Index
    
    Handle GET request for the index page.
    Display the index page with user information.

    Returns
    -------
    render_template
        Renders the 'index.html' template with user information.
    """
    return render_template("index.html", user=current_user)

@views.errorhandler(404)
def page_not_found(e):
    """Page Not Found
    
    Handle 404 errors.
    Render a custom 404 page with an error message.

    Parameters
    ----------
    e : Exception
        The exception object representing the 404 error.

    Returns
    -------
    render_template
        Renders the '404.html' template with the provided error message.

    """
    return render_template("404.html", err_msg=e), 404

@views.route("/profile", methods=["GET", "POST"], endpoint="profile")
@restricted_route_decorator
def profile():
    """Profile
    
    Handle GET and POST requests for the profile page.
    Display user profile information and allow users to update their profiles.

    Returns
    -------
    render_template
        Renders the 'profile.html' template with user information and a profile form.

    Notes
    -----
    This endpoint requires the user to be authenticated.

    """
    from .models import db
    from .forms import ProfileForm
    
    user = get_current_user()
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

@views.route("/chat", endpoint="chat")
@restricted_route_decorator
def chat():
    """
    Chat
    Handle GET request for the Chat page.
    Display the Chat page with user 
    information and an empty chat form.

    Returns
    -------
    render_template
        Renders the 'chat.html' template with 
        user information, no specific chat data, 
        no chat ID, and an empty chat name form.

    Notes
    -----
    This endpoint requires the user to be authenticated.

    """
    from .forms import ChatEdit

    user = get_current_user()
    chat_name_form = ChatEdit()
    
    return render_template("chat.html", user=user, chat_data=-1, chat_id=-1, name_form=chat_name_form)


@views.route("/get_chat/<int:chat_id>", endpoint="get_chat")
@restricted_route_decorator
def get_chat(chat_id: int):
    """Get Chat
    
    Handle GET request to retrieve chat information.
    Retrieve and display information about a specific chat.

    Parameters
    ----------
    chat_id : int
        The identifier of the chat to be retrieved.

    Returns
    -------
    render_template
        Renders the 'chat.html' template with user 
        information, chat data, chat ID, and a 
        chat name form.

    Raises
    ------
    Redirect
        Redirects to the chat page if the current user 
        is not authorized to access the specified chat 
        or if the chat does not exist.

    Notes
    -----
    This endpoint requires the user to be authenticated 
    and have the necessary permissions to access 
    the specified chat.
    """
    from .forms import ChatEdit

    user = get_current_user()
    # Prevent from other users to access
    chat_data = Chat.query.filter_by(user_id=current_user.id, id=chat_id).first()
    if chat_data is None:
        return redirect(url_for("views.chat"))
    
    chat_name_form = ChatEdit()
    
    return render_template("chat.html", user=user, chat_data=chat_data.chat, chat_id=chat_id, name_form=chat_name_form)


@views.route("/get", endpoint="get")
@restricted_route_decorator
def get_bot_response():
    from .models import db
    
    user = get_current_user()
    
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
    return html_encode(bot_response)

@views.route("/chat-edit", endpoint="chat-edit")
@restricted_route_decorator
def get_chat_edit() -> Any:
    """Get Chat Edit
    
    Handle GET request for Chat Edit endpoint.
    Edit the name of a chat by the name and chat 
    id in the request arguments.

    Returns
    -------
    Any
        An empty string.

    Raises
    ------
    Redirect
        Redirects to the index page if the current 
        user is not authorized to edit the chat or 
        if the chat does not exist.

    Notes
    -----
    This endpoint requires the user to be authenticated 
    and have the necessary permissions to edit the 
    chat name.
    """
    from .models import db
    
    user = get_current_user()
    
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
def get_image(username: str) -> Any:
    """Get Image
    
    Returns the profile image of the current user.

    Parameters
    ----------
    username : str
        The user name to search.

    Returns
    -------
    Any
        User image.
    """
    # Make sure the user sent the request correctly
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

@views.route("/text2speech/<string:text>", endpoint="text2speech")
@restricted_route_decorator
def text2speech(text: str=""):
    try:
        speech = Text2Speech()
        speech.say(text)
    except:
        pass
    return Response()

@views.route('/review', methods=['GET', 'POST'])
def reviews():
    """Review
    
    Handle GET and POST requests for the review page.
    Display previous user's reviews and allow logged in users to post reviews.

    Returns
    -------
    render_template
        Renders the 'review.html' template with review form.

    Notes
    -----
    the post method requires the user to be authenticated.

    """
    from .forms import ReviewForm
    from .models import db, Reviews
    review_form = ReviewForm()
    if review_form.validate_on_submit() and current_user.is_authenticated:
        review = Reviews(title=review_form.title.data,
                        content=review_form.content.data,
                        stars=review_form.stars.data,
                        user_id=None if review_form.anonymous.data else current_user.id)
        db.session.add(review)
        db.session.commit()
        flash('Your review has been posted!', 'success')
        return redirect(url_for('views.reviews'))
    reviews = Reviews.query.all()
    local_timezone = ZoneInfo("Asia/Jerusalem")
    for review in reviews:
        review.submitted_at = review.submitted_at.astimezone(local_timezone)
    return render_template('review.html', title='Reviews', review_form=review_form, reviews=reviews)

@views.route('/user_image/<filename>')
def user_image(filename):
    """Get Image
    
    Returns the profile image of the current user.

    Parameters
    ----------
    filename : str
        The file name to search.

    Returns
    -------
    Any
        filename image.
    """
    user = User.query.filter_by(image_filename=filename).first()
    if user and user.image_data:
        return Response(user.image_data, mimetype='image/png')  # Adjust mimetype as necessary
    else:
        return url_for('static', filename='image/default.png')  # Fallback to default image