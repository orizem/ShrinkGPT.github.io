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
from flask import render_template, redirect, url_for, send_file, session
from dotenv import load_dotenv

load_dotenv()
D_ID_API_KEY = os.environ.get("D_ID_API_KEY")

# LOCAL IMPORTS
from ..models import User

# PROJECT IMPORTS
from config import WEBSITE_PATH


# PRIVATE
def __get_all_images(start_with: Union[str, List]):
    IMAGE_PATH = rf"{WEBSITE_PATH}\static\image"

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
    with open(rf"{WEBSITE_PATH}\static\image\{images[-1]}", "rb") as img_file:
        yield (
            b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + img_file.read() + b"\r\n"
        )

    while True:
        for image_name in images:
            try:
                with open(
                    rf"{WEBSITE_PATH}\static\image\{image_name}", "rb"
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
    base = rf"{WEBSITE_PATH}\static\image"
    safepath = realpath(rf"{WEBSITE_PATH}\static\image\default.png")
    prefix = commonpath((base, safepath))
    if prefix == base:
        return send_file(rf"{base}\default.png", mimetype="image/jpeg")
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


def html_encode(text):
    return html.escape(text)


def html_decode(text):
    return html.unescape(text)


def get_avatar_video(text):
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
    print(f"\n{'='*35}\n", talks_response_json, f"\n{'='*35}\n")  #! Remove, Test Tag
    url = url + "/" + talks_response_json.get("id")
    print(f"\n{'='*35}\nTalks ID URL = {url}\n{'='*35}\n")  #! Remove, Test Tag
    sleep(5)

    response = requests.get(url, headers=headers)
    response_json = response.json()

    # while not talks_response_json.get("id"): #! Fix the not return correct response
    #     talks_response = requests.post(url, json=payload, headers=headers)

    #     try:
    #         talks_response_json = talks_response.json()
    #     except:
    #         pass

    #     if talks_response_json.get("id"):
    #         print(f"\n{'='*35}\n", talks_response_json, f"\n{'='*35}\n") #! Remove, Test Tag

    #         url = url + '/' + talks_response_json.get("id")
    #         print(f"\n{'='*35}\nTalks ID URL = {url}\n{'='*35}\n") #! Remove, Test Tag

    #         response_json = dict()
    #         i = 0
    #         while not response_json.get("result_url"): # ! Fix the not return correct response
    #             response = requests.get(url, headers=headers)
    #             print(f"try - {i}: |{response_json.get("result_url")}|") #! Remove, Test Tag
    #             i += 1
    #             sleep(0.5)
    #             try:
    #                 response_json = response.json()
    #             except:
    #                 pass

    #             if i > 5:
    #                 break

    return response_json.get("result_url")

ALLOWED_EXTENSIONS = {'mp3', 'wav'}

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
