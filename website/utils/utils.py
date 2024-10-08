# utils.py

import os
import html
import requests
import functools

from os import listdir
from time import sleep
from typing import List, Union, Callable
from flask_login import current_user
from os.path import realpath, commonpath
from flask import render_template, redirect, url_for, send_file, session, request
from dotenv import load_dotenv

QUESTIONS = [
    """
    Hello {}, welcome to Shrink.io!
    Before we start the therapy sessions, I would like
    you to tell me a little bit about you self. 
    I will ask you some questions and after that we will
    begin working on the what brought you here.
    Ok, lets begin:""",
    "How old are you?",
    "What's your current living situation? Do you live alone, with family, or with roommates?",
    "What do you do for work or study? How do you feel about your job or school?",
    "What does a typical day look like for you from morning to night?",
    "Do you have any daily routines or rituals that are important to you?",
    "How do you spend your free time or weekends?",
    "How would you describe your social life? Do you spend a lot of time with friends or family?",
    "Are you currently in a relationship? If so, how would you describe it?",
    "Have you experienced any significant physical health issues?",
    "Do you have any history of mental health diagnoses or treatments?",
    "Are you currently taking any medications?",
    "Have you ever seen a psychologist or therapist before?",
    "What brings you in today?",
]

# LOCAL IMPORTS
from ..models import User, Admin


# PRIVATE
def __get_all_images(start_with: Union[str, List]):
    IMAGE_PATH = r"website/static/image"

    if not isinstance(start_with, list):
        start_with = [start_with]

    images = []
    for sw in start_with:
        images = images + [
            img
            for img in listdir(IMAGE_PATH)
            if img.lower().startswith(sw)
            and (img.endswith(".jpg") or img.endswith(".jpeg") or img.endswith(".png"))
        ]
    return images


# PUBLIC
def generate_slide_show(start_with: Union[str, List]):
    """Generate Slide Show

    Generate a slideshow of images.

    This generator function yields frames
    of images for creating a slideshow.
    It starts with the specified image or
    list of images and continues in a loop,
    adding a delay of 5 seconds
    between each image.

    Parameters
    ----------
    start_with : str | List
        The starting image or list of images
        for the slideshow.

    Yields
    ------
    bytes
        Frames of images in the form of bytes
        with appropriate HTTP headers for streaming.

    Notes
    -----
    - The images are read from the 'static/image' directory in the project path.
    - The slideshow continues indefinitely, looping through the specified images.
    - Deprecated images are removed from the list to prevent errors.

    """
    images = __get_all_images(start_with=start_with)

    # Instantly load image without sleep
    with open(os.path.join(r"website/static/image", images[-1]), "rb") as img_file:
        yield (
            b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + img_file.read() + b"\r\n"
        )

    while True:
        for image_name in images:
            try:
                with open(
                    os.path.join(r"website/static/image", image_name), "rb"
                ) as img_file:
                    yield (
                        b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                        + img_file.read()
                        + b"\r\n"
                    )
                sleep(5)
            except IndexError:
                # Removes deprecated image names.
                images = list(set(images) - {image_name})


def safe_send_default_image():
    """Safe Send Default Image

    Safely send the default image file.
    This function ensures that the
    default image file is served securely.
    It checks if the provided path is
    within the expected base path to
    prevent directory traversal.

    Returns
    -------
    send_file or tuple
        If the path is safe, the default
        image file is sent using Flask's
        `send_file` function.
        If the path is not safe, a tuple
        with an error message and HTTP
        status code 404 is returned.

    """
    base = realpath(r"website/static/image")
    safe_path = realpath(r"website/static/image/default.png")
    prefix = commonpath((base, safe_path))

    if prefix == base:
        return send_file(rf"{base}/default.png", mimetype="image/jpeg")
    return "Error", 404


def get_current_user():
    """Get Current User

    Search the flask login current user.

    Returns
    -------
    User | None
        The model of flask login current user.
        Returns None if was not found.
    """
    user = User.query.filter_by(username=current_user.username).first()
    return user


def restricted_route_decorator(check_session: bool):
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

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if check_session == True:
                if "username" not in session:
                    return redirect(url_for("views.index"))
                user = User.query.filter_by(username=session["username"]).first()

                if user is None:
                    return redirect(url_for("views.index"))
            else:
                if (current_user == None) or (current_user.is_authenticated == False):
                    msg = "The page you where looking for could not be found."
                    return render_template("404.html", err_msg=msg), 404
                user = get_current_user()

                if user is None:
                    return redirect(url_for("views.index"))

            res = func(*args, **kwargs)
            return res

        return wrapper

    return decorator


# @restricted_route_decorator(check_session=True)
def restricted_admin_route_decorator():
    """Restricted Route Decorator

    Using the restricted_route_decorator, this decorator checks
    if the user id is in the admins table, otherwise, redirected
    to index page as well.

    Must define endpoint for each route using this decorator.
    The decorator should be right above the function in
    order to run properly.

    Parameters
    ----------
    func : Callable
        The function to wrap with authentication checking.
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                user = get_current_user()
            except:
                return redirect(url_for("views.index"))

            admin_id = Admin.query.filter_by(user_id=user.id).first()

            if admin_id is None:
                return redirect(url_for("views.index"))

            res = func(*args, **kwargs)
            return res

        return wrapper

    return decorator


def html_encode(text):
    return html.escape(text)


def html_decode(text):
    return html.unescape(text)


def get_avatar_video(text):
    load_dotenv()
    D_ID_API_KEY = os.environ.get("D_ID_API_KEY")
    
    payload = {
        "source_url": "https://create-images-results.d-id.com/DefaultPresenters/Emma_f/thumbnail.jpeg",  #! Make this with other frameworks
        "script": {
            "type": "text",
            "input": text,
            "provider": {
                "type": "microsoft",  #! Make this with other frameworks
                "voice_id": "en-US-JennyNeural",  #! Make this with other voices
                "voice_config": {"style": "Cheerful"},  #! Make this with other configs
            },
        },
    }
    headers = {
        "accept": "application/json",
        "Authorization": f"Basic {D_ID_API_KEY}",
        "content-type": "application/json",
    }
    url = "https://api.d-id.com/talks"

    talks_response_json = dict()

    talks_response = requests.post(url, json=payload, headers=headers)
    talks_response_json = talks_response.json()
    url = url + "/" + talks_response_json.get("id")
    sleep(5)

    response = requests.get(url, headers=headers)
    response_json = response.json()

    return response_json.get("result_url")


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {
        "flac",
        "m4a",
        "mp3",
        "mp4",
        "mpeg",
        "mpga",
        "oga",
        "ogg",
        "wav",
        "webm",
    }
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_initial_chat_state_response(user):
    status = user.status
    response = QUESTIONS[status]
    if user.status == 1:
        response = QUESTIONS[0].format(user.full_name) + "\n" + response
    user.status += 1

    if user.status >= len(QUESTIONS):
        user.status = 0

    return response
