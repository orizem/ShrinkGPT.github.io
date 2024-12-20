# views.py

import os
import io
import pytz
import requests
import threading
from io import BytesIO
from json import dumps
from typing import Any
from flask_login import current_user
from flask import (
    Blueprint,
    Response,
    render_template,
    redirect,
    url_for,
    send_file,
    request,
    flash,
    jsonify,
    abort,
)
from datetime import datetime

# LOCAL IMPORTS
from .models import User, Chat
from .utils.text2speech import speak
from .utils.utils import (
    generate_slide_show,
    safe_send_default_image,
    get_current_user,
    restricted_route_decorator,
    html_encode,
    get_avatar_video,
    allowed_file,
    get_initial_chat_state_response,
    get_previous_chats,
    QUESTIONS,
)
from .utils.gpt import (
    format_chat_history_for_gpt,
    GPT_MESSAGES,
    client,
)

# Define a thread-local storage for each request/thread
thread_local = threading.local()

views = Blueprint("views", __name__)

# Define the absolute path to your Sphinx HTML docs
DOCS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "docs/_build/html")
)
STATIC_PATH = os.path.join(DOCS_PATH, "_static")

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
    from .models import Reviews

    # Order reviews by submitted_at in descending order
    reviews = Reviews.query.order_by(Reviews.submitted_at.desc()).limit(10).all()

    jerusalem_tz = pytz.timezone("Asia/Jerusalem")
    local_timezone = datetime.now(jerusalem_tz)

    for review in reviews:
        review.submitted_at = review.submitted_at.astimezone(local_timezone.tzinfo)

    table_data = [
        {
            "submitted_at": str(review.submitted_at),
            "name": review.user.username if review.user_id is not None else "Anonymous",
            "title": review.title,
            "content": review.content,
            "stars": review.stars,
            "user_id": review.user_id,
        }
        for review in reviews
    ]

    table_data_json = dumps(table_data)

    return render_template("index.html", user=current_user, reviews=table_data_json)


# ROUTES
@views.route("/presentation")
def presentation():
    """Presentation

    Handle GET request for the presentation page.
    Display the presentation page with user information.

    Returns
    -------
    render_template
        Renders the 'presentation.html' template with user information.
    """
    return render_template("presentation.html", user=current_user)


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
@restricted_route_decorator(check_session=False)
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
@restricted_route_decorator(check_session=False)
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

    return render_template(
        "chat.html", user=user, chat_data=-1, chat_id=-1, name_form=chat_name_form
    )


@views.route("/get_chat/<int:chat_id>", endpoint="get_chat")
@restricted_route_decorator(check_session=False)
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
    return render_template(
        "chat.html",
        user=user,
        chat_data=chat_data.chat,
        chat_id=chat_id,
        name_form=chat_name_form,
    )


@views.route("/get", endpoint="get")
@restricted_route_decorator(check_session=False)
def get_bot_response():
    """Handle GET request for bot response.

    Process user input and generate a response from the AI model.

    Returns
    -------
        dict: A dictionary containing the encoded bot response and avatar video URL.

    Note
    ----
        This endpoint requires authentication and appropriate permissions.
    """
    from .models import db

    user = get_current_user()
    chat_id = int(request.args.get("chatId"))
    first_time = request.args.get("firstTime")
    user_msg = request.args.get("msg")
    date_time = request.args.get("dateTime")

    if chat_id != -1:
        current_chat = Chat.query.filter_by(user_id=current_user.id, id=chat_id).first()
    elif user.status == 1:
        welcome_text = ""
        welcome_response = {
            "identifier": "assistant",
            "text": welcome_text,
            "date_time": date_time,
        }
        new_chat = Chat(
            name=f"Chat_{len(user.chats)}",
            chat_json=dumps([welcome_response]),
            user_id=current_user.id,
        )
        db.session.add(new_chat)
        db.session.commit()
        current_chat = user.chats[-1]
    else:
        if first_time == "1":
            if user.status == 1:
                welcome_text = QUESTIONS[0].format(user.full_name) + "\n" + QUESTIONS[1]
            else:
                welcome_text = f"Hi { user.name.title() }, welcome to Shrink.io! Go ahead and send me a message."

            welcome_response = {
                "identifier": "assistant",
                "text": welcome_text,
                "date_time": date_time,
            }
            new_chat = Chat(
                name=f"Chat_{len(user.chats)}",
                chat_json=dumps([welcome_response]),
                user_id=current_user.id,
            )
            db.session.add(new_chat)
            db.session.commit()
        current_chat = user.chats[-1]

    existing_messages = current_chat.chat
    new_message = {"identifier": "user", "text": user_msg, "date_time": date_time}
    existing_messages.append(new_message)

    if user.status == 0:
        chat_history = [
            format_chat_history_for_gpt(__chat) for __chat in existing_messages
        ]

        db_chats_history = get_previous_chats(user)

        # Prepare messages for OpenAI API
        messages = GPT_MESSAGES + db_chats_history + chat_history

        # Interact with OpenAI GPT-4
        response = client.chat.completions.create(model="gpt-4o", messages=messages)
        bot_response = response.choices[0].message.content
    else:
        bot_response = get_initial_chat_state_response(user)

    new_message = {"identifier": "assistant", "text": bot_response, "date_time": date_time}
    existing_messages.append(new_message)

    current_chat.chat = existing_messages

    # Update chat history
    db.session.add(current_chat)
    db.session.commit()

    encoded_bot_response = html_encode(bot_response)

    # Generate response avatar stream
    avatar_video_url = ""
    emotion = "neutral"
    if user.status == 0:
        try:      
            API_URL = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"
            token = os.environ.get("HUGGINGFACE_API_KEY")
            headers = {"Authorization": token}
            payload = {
                "inputs": user_msg,
            }
            
            try:
                response = requests.post(API_URL, headers=headers, json=payload)
                res = response.json()[0]
                
                # Filter scores for list_labels
                emotions = ["surprise", "joy", "neutral"]
                filtered_data = [item for item in res if item['label'] in emotions]
                
                if filtered_data:
                    highest_score_label = max(filtered_data, key=lambda x: x['score'])['label']
                    emotion = highest_score_label
                    if emotion == "joy":
                        emotion = "happy"
                else:
                    emotion = "neutral"
            except Exception:    
                emotion = "neutral"
                
            avatar_video_url = get_avatar_video(bot_response, emotion)
        except Exception as e:
            print("[D-ID Video Error]:", e)
            avatar_video_url = ""
        print("[avatar_video_url]:", avatar_video_url)

    response = {
        "encoded_bot_response": encoded_bot_response,
        "avatar_video_url": avatar_video_url,
        "emotion": emotion,
    }

    return response


@views.route("/chat-edit", endpoint="chat-edit")
@restricted_route_decorator(check_session=False)
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


@views.route("/chat-delete", endpoint="chat-delete")
@restricted_route_decorator(check_session=False)
def get_chat_delete() -> Any:
    """Get Chat Delete

    Handle GET request for Chat Delete endpoint.
    Delete the chat by the chat
    id in the request arguments.

    Returns
    -------
    Any
        An empty string.

    Raises
    ------
    Redirect
        Redirects to the index page if the current
        user is not authorized to delete the chat or
        if the chat does not exist.

    Notes
    -----
    This endpoint requires the user to be authenticated
    and have the necessary permissions to delete the
    chat.
    """
    from .models import db

    user = get_current_user()

    id = request.args.get("id")

    # Prevent from other users to access
    current_chat = Chat.query.filter_by(user_id=user.id, id=id).first()
    if current_chat is None:
        return redirect(url_for("views.index"))

    db.session.delete(current_chat)
    db.session.commit()
    return ""


@views.route("/get_image/<string:username>")
def get_image(username: str) -> Any:
    """Get Image

    Returns the profile image of the user.

    Parameters
    ----------
    username : str
        The user name to search.

    Returns
    -------
    Any
        User image.
    """
    # Make sure the user sent the request correctly, or to reviews
    referrer = request.referrer

    if referrer is None or referrer.split("/")[3] not in ["review", ""]:
        if current_user.username != username:
            return redirect(url_for("views.index"))

    # Prevent from other users to access
    user = User.query.filter_by(username=username).first()

    if (user is not None) and (user.image_data is not None):
        image_path = user.image_data
        base_path = BytesIO(image_path)
        return send_file(base_path, mimetype="image/jpeg")
    return safe_send_default_image()


@views.route("/slideshow/")
@views.route("/slideshow/<string:start_with>")
def slideshow(start_with: str = "") -> Response:
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
    return Response(
        generate_slide_show(start_with=start_with),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@views.route("/text2speech/<string:text>", endpoint="text2speech")
@restricted_route_decorator(check_session=False)
def text2speech(text: str = "") -> Response:
    """Text to Speech Converter

    Convert text to speech and play it.
    This route handles text-to-speech conversion and playback.
    It uses the speak function to convert the provided text into speech.

    Parameters
    ----------
    text : str, optional
        The text to be converted to speech. If omitted, an empty string is used.

    Returns
    -------
    Response
        An empty Flask Response object.

    Notes
    -----
    This endpoint does not require user authentication (check_session=False).
    It silently fails and returns an empty response if any error occurs during the speech synthesis process.

    Examples
    --------
    >>> text2speech("Hello, world!")
    Plays the spoken version of "Hello, world!".
    >>> text2speech("")
    Does nothing, as no text is provided.
    """
    try:
        speak(text)
    except Exception:
        pass
    return Response()


@views.route("/review", methods=["GET", "POST"])
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
        review = Reviews(
            title=review_form.title.data.replace("`", "'"),
            content=review_form.content.data.replace("`", "'"),
            stars=review_form.stars.data,
            user_id=None if review_form.anonymous.data else current_user.id,
        )
        db.session.add(review)
        db.session.commit()
        flash("Your review has been posted!", "success")
        return redirect(url_for("views.reviews"))

    # Order reviews by submitted_at in descending order
    reviews = Reviews.query.order_by(Reviews.submitted_at.desc()).all()

    jerusalem_tz = pytz.timezone("Asia/Jerusalem")
    local_timezone = datetime.now(jerusalem_tz)

    for review in reviews:
        review.submitted_at = review.submitted_at.astimezone(local_timezone.tzinfo)

    return render_template(
        "review.html", title="Reviews", review_form=review_form, reviews=reviews
    )


@views.route("/user_image/<filename>")
def user_image(filename: str):
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
        # Adjust mimetype as necessary
        return Response(user.image_data, mimetype="image/png")
    else:
        # Fallback to default image
        return url_for("static", filename="image/default.png")


@views.route("/save_record", methods=["POST"])
def save_record() -> tuple:
    """Audio File Transcription Endpoint

    This endpoint accepts audio file uploads and transcribes them to text.
    The audio file should be sent as a multipart form data with key 'file'.
    Only allowed audio file formats (as determined by allowed_file()) will be processed.
    The audio data is processed in memory without saving to disk.

    Returns
    -------
    tuple
        A tuple containing two elements:
        - First element: Either a JSON response with transcribed text or an error message string
        - Second element: HTTP status code (200 for success, 400 for errors)

    Example Response
    ----------------
    Success: ({"text": "transcribed text content"}, 200)
    Error: ("No file part", 400) or ("Invalid file type", 400)
    """
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]

    if file and allowed_file(file.filename):
        file_bytes_data = file.read()
        buffer = io.BytesIO(file_bytes_data)  # Read file data into memory
        buffer.name = "file.mp3"
        transcription = transcribe_audio(buffer)  # Transcribe the audio in memory
        return jsonify({"text": transcription}), 200
    else:
        return "Invalid file type", 400


def transcribe_audio(file_bytes: io.BytesIO) -> str:
    """Transcribe Audio to Text using OpenAI's Whisper Model

    This function takes an audio file in bytes format and transcribes it to text
    using OpenAI's Whisper ASR (Automatic Speech Recognition) model.
    The file pointer is reset to the start before processing to ensure
    complete file reading.

    Parameters
    ----------
    file_bytes : io.BytesIO
        A BytesIO object containing the audio data to be transcribed.
        The audio should be in a format supported by the Whisper model
        (e.g., mp3, wav, m4a, etc.).

    Returns
    -------
    str
        The transcribed text from the audio file.
        Returns an empty string if transcription fails.

    Notes
    -----
    - Uses OpenAI's 'whisper-1' model for transcription
    - Currently set to transcribe English language content only
    - Requires valid OpenAI API credentials in the client object

    Raises
    ------
    Exception
        May raise exceptions related to API calls, invalid audio format,
        or authentication issues with the OpenAI client.
    """
    file_bytes.seek(0)  # Reset pointer to the start of the file
    transcription = client.audio.transcriptions.create(
        model="whisper-1", file=file_bytes, language="en"
    )
    return transcription.text


# Route to serve the Sphinx documentation
@views.route("/docs/")
def docs_empty() -> Response:
    """Redirect Empty Docs Route

    This route handler manages the empty '/docs/' endpoint by redirecting
    to the main documentation page. When users access the /docs/ URL
    without additional path parameters, they will be automatically
    redirected to the main documentation view.

    Returns
    -------
    Response
        A Flask redirect response that sends the user
        to the main documentation page (views.docs_main).

    Notes
    -----
    - The trailing slash in '/docs/' is important for route matching
    - Uses Flask's url_for() for generating the redirect URL
    - This is a convenience route to handle empty docs requests
    """
    return redirect(url_for("views.docs_main"))


# Route to serve the Sphinx documentation
@views.route("/docs/<path:filename>")
def docs(filename) -> Response:
    """Docs

    Serve static files from the documentation directory.
    This route handles requests for documentation files stored in the DOCS_PATH directory.
    It allows serving individual files or directories within the documentation structure.

    Parameters
    ----------
    filename : str
        Path to the file or directory within the DOCS_PATH.

    Returns
    -------
    Response
        File contents if found, otherwise raises a 404 error.

    Notes
    -----
    This endpoint serves static files directly without processing them through the Flask application.
    It's designed to handle documentation-related file requests efficiently.

    Examples
    --------
    >>> docs('readme.md')
    Serves the readme.md file from the DOCS_PATH.
    >>> docs('images/logo.png')
    Serves the logo.png image from the images subdirectory in DOCS_PATH.
    >>> docs('api/docs.pdf')
    Serves the api/docs.pdf file from the DOCS_PATH.
    """
    file_path = os.path.join(DOCS_PATH, filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        abort(404)


# Route for the index page of the documentation
@views.route("/docs")
def docs_index():
    """Docs Index

    Redirect to the main documentation page.
    This route serves as the entry point for accessing the documentation.
    It redirects users to the main documentation page, which likely contains an overview or index of available documentation resources.

    Returns
    -------
    redirect
        Redirects to the main documentation page.

    Notes
    -----
    This endpoint is typically used to provide a centralized access point for documentation within the application.
    It's part of a larger documentation system, possibly involving multiple pages or sections.

    Examples
    --------
    >>> docs_index()
    Redirects to the main documentation page.
    """
    return redirect(url_for("views.docs_main"))


# Route for the index page of the documentation
@views.route("/docs/index.html")
def docs_main():
    """Docs Main

    Serve the main documentation page.
    This route handles requests for the main HTML file in the documentation directory.
    It serves the main.html file, which likely contains an overview or index of available documentation resources.

    Returns
    -------
    Response
        File contents of the main.html file if found, otherwise raises a 404 error.

    Notes
    -----
    This endpoint serves the main documentation page directly without additional processing.
    It's part of a larger documentation system, possibly involving multiple pages or sections.

    Examples
    --------
    >>> docs_main()
    Serves the main.html file from the DOCS_PATH.
    """
    index_path = os.path.join(DOCS_PATH, "index.html")
    if os.path.exists(index_path):
        return send_file(index_path)
    else:
        abort(404)


# Redirect root static path requests to the correct /docs/_static path
@views.route("/_static/<path:filename>")
def root_static(filename):
    """Root Static

    Redirect static files to the documentation directory.
    This route handles requests for static files outside the documentation directory.
    It redirects these requests to the corresponding files within the documentation structure.

    Parameters
    ----------
    filename : str
        Path to the static file relative to the root of the application.

    Returns
    -------
    redirect
        Redirects to the equivalent file path within the docs/_static directory.

    Notes
    -----
    This endpoint serves as a fallback mechanism for serving static files.
    It ensures that static resources are correctly served from the docs/_static directory.
    """
    return redirect(f"/docs/_static/{filename}", code=301)


# Serve static files (CSS, JS, images)
@views.route("/docs/_static/<path:filename>")
def docs_static(filename):
    """Docs Static

    Redirect static files to the documentation directory.
    This route handles requests for static files located outside the documentation directory.
    It redirects these requests to the corresponding files within the documentation structure.

    Parameters
    ----------
    filename : str
        Path to the static file relative to the root of the application.

    Returns
    -------
    redirect
        Redirects to the equivalent file path within the docs/_static directory.

    Notes
    -----
    This endpoint serves as a fallback mechanism for serving static files.
    It ensures consistency in serving static resources regardless of their location within the application structure.

    Examples
    --------
    >>> root_static('image.jpg')
    Redirects to '/docs/_static/image.jpg'.
    >>> root_static('styles.css')
    Redirects to '/docs/_static/styles.css'.
    """
    static_file_path = os.path.join(STATIC_PATH, filename)
    if os.path.exists(static_file_path):
        return send_file(static_file_path)
    else:
        abort(404)
