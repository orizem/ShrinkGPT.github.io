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
    """Get all images from a directory that match a prefix

    This function searches the `website/static/image` directory for image
    files that start with a specified prefix or a list of prefixes. It only
    considers files with `.jpg`, `.jpeg`, or `.png` extensions and returns
    the matching image filenames.

    The function can accept a single prefix as a string or multiple prefixes
    as a list of strings. If a list is not provided, the function treats the
    prefix as a list with one element.

    Parameters
    ----------
    start_with : Union[str, List]
        A single prefix (str) or a list of prefixes (List[str]) to search for in the filenames.

    Returns
    -------
    List[str]
        A list of image filenames (with `.jpg`, `.jpeg`, or `.png` extensions)
        that start with the provided prefix or prefixes.

    Examples
    --------
    >>> __get_all_images("logo")
    ['logo1.jpg', 'logo2.png', 'logo3.jpeg']

    >>> __get_all_images(["thumb", "banner"])
    ['thumb1.jpg', 'thumb2.png', 'banner1.jpeg']
    """
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
            if check_session:
                if "username" not in session:
                    return redirect(url_for("views.index"))
                user = User.query.filter_by(username=session["username"]).first()

                if user is None:
                    return redirect(url_for("views.index"))
            else:
                if (current_user is None) or (not current_user.is_authenticated):
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
            except Exception:
                return redirect(url_for("views.index"))

            admin_id = Admin.query.filter_by(user_id=user.id).first()

            if admin_id is None:
                return redirect(url_for("views.index"))

            res = func(*args, **kwargs)
            return res

        return wrapper

    return decorator


def html_encode(text):
    """Encode HTML special characters

    This function takes a string and converts all special HTML characters
    (e.g., `<`, `>`, `&`, etc.) into their corresponding HTML escape codes.
    It uses Python's `html.escape` to ensure that the input text is safely
    represented in HTML format.

    Parameters
    ----------
    text : str
        The input string that contains special HTML characters to be encoded.

    Returns
    -------
    str
        The encoded string with HTML special characters replaced by their escape codes.

    Examples
    --------
    >>> html_encode("<div>Hello & Welcome</div>")
    '&lt;div&gt;Hello &amp; Welcome&lt;/div&gt;'
    """
    return html.escape(text)


def html_decode(text):
    """Decode HTML escape codes into characters

    This function takes a string containing HTML escape codes and converts
    them back into their corresponding characters. It uses Python's `html.unescape`
    to decode the HTML entities into their original form.

    Parameters
    ----------
    text : str
        The input string containing HTML escape codes to be decoded.

    Returns
    -------
    str
        The decoded string with HTML escape codes replaced by their corresponding characters.

    Examples
    --------
    >>> html_decode('&lt;div&gt;Hello &amp; Welcome&lt;/div&gt;')
    '<div>Hello & Welcome</div>'
    """
    return html.unescape(text)


def get_avatar_video(text, emotion):
    """Generate an avatar video with a given emotion and text

    This function interacts with the D-ID API to generate a video where
    a given avatar speaks the provided text with the specified emotion.
    It returns the URL of the generated video.

    Parameters
    ----------
    text : str
        The text that the avatar will speak.
    emotion : str
        The emotion (e.g., "happy", "sad") to apply to the avatar's expression.

    Returns
    -------
    str
        The URL of the generated avatar video.

    Examples
    --------
    >>> get_avatar_video("Hello, how are you?", "happy")
    'https://api.d-id.com/talks/xyz/result.mp4'
    """
    load_dotenv()
    D_ID_API_KEY = os.environ.get("D_ID_API_KEY")

    payload = {
        "source_url": "https://create-images-results.d-id.com/DefaultPresenters/Emma_f/thumbnail.jpeg",  #! Make this with other frameworks
        "script": {
            "type": "text",
            "input": text,
            "provider": {
                "type": "microsoft",
                "voice_id": "en-US-JennyNeural",
            },
        },
        "config": {
            "driver_expressions": {
                "expressions": [
                    {"start_frame": 0, "expression": f"{emotion}", "intensity": 1}
                ]
            }
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
    sleep(7)

    response = requests.get(url, headers=headers)
    response_json = response.json()

    return response_json.get("result_url")


def allowed_file(filename):
    """Check if the file has an allowed extension

    This function checks whether the given filename has an extension that
    is allowed for uploading (e.g., audio or video files).

    Parameters
    ----------
    filename : str
        The filename to check.

    Returns
    -------
    bool
        True if the file has an allowed extension, False otherwise.

    Examples
    --------
    >>> allowed_file("song.mp3")
    True

    >>> allowed_file("image.jpg")
    False
    """
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
    """Get the initial chat state response based on user status

    This function generates the next response for the user based on their
    current status. It returns a question or statement according to the user's
    progress in the chat.

    Parameters
    ----------
    user : User
        The user object that contains the user's current status.

    Returns
    -------
    str
        The response that corresponds to the user's current chat status.

    Examples
    --------
    >>> get_initial_chat_state_response(user)
    "Hello John, how can I assist you today?"
    """
    status = user.status
    response = QUESTIONS[status]
    if user.status == 1:
        response = QUESTIONS[0].format(user.full_name) + "\n" + response
    user.status += 1

    if user.status >= len(QUESTIONS):
        user.status = 0

    return response


def get_previous_chats(user):
    """Retrieve and format the previous chat history for a given user.

    This function extracts all previous chats associated with the user, 
    formats them into a standardized structure, and returns the chat history.

    Parameters
    ----------
    user : User
        The user object containing chat-related data.

    Returns
    -------
    list of dict
        A list of dictionaries representing the chat history, where each 
        dictionary contains the role ('assistant' or 'user') and the content 
        of the chat.

    Examples
    --------
    >>> get_previous_chats(user)
    [
        {'role': 'user', 'content': 'Hello!'},
        {'role': 'assistant', 'content': 'Hi there! How can I help?'}
    ]
    """
    db_chats_history = []
    for chat in user.chats:
        db_chats_history += chat.chat

    chats_history = []
    for db_data in db_chats_history:
        formatted_data = {
            "role": (
                "assistant" if db_data["identifier"] in ["bot", "assistant"] else "user"
            ),
            "content": db_data["text"],
        }
        chats_history.append(formatted_data)
    return chats_history


# Admin Utils
# import os
from flask import session
from datetime import datetime, timedelta
from random import randint, choice, choices, sample
from faker import Faker
from json import dumps
from bson import json_util

# LOCAL IMPORTS
from ..models import Admin, User, Status, Reviews, Chat, db

# Initialize the Faker object
fake = Faker()


def random_date() -> datetime:
    """Generates a random date between May 1, 2024, and the current date.

    Returns a random date calculated by generating a random number of days between the start and today.

    Returns
    -------
    datetime
        A random date between May 1, 2024, and the current date.
    """
    start = datetime(2024, 5, 1)
    end = datetime.today()
    delta = end - start
    random_days = randint(0, delta.days)
    return start + timedelta(days=random_days)


def create_test_users():
    """Generates and adds 383 test users to the database with random usernames, names, and statuses.

    This function uses the Faker library to generate random names and usernames, then adds them to the
    database. A random status is also assigned to each user along with a registration date.

    Returns
    -------
    None
        The function does not return anything. It commits each user and their associated status to the database.
    """
    for i in range(383):
        Faker.seed(randint(0, 100000))
        fake = Faker("en")

        name = fake.first_name()
        lastname = fake.last_name()
        username = f"{name}_{lastname}_{randint(0, 999)}"
        password = "123456"

        # add new user to the database
        user_data = {
            "username": username,
            "password": password,
            "name": name,
            "lastname": lastname,
            "image_data": None,
            "image_filename": "default.png",
        }
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()

        user = User.query.filter_by(username=user.username).first()

        status_data = {
            "user_id": user.id,
            "status": randint(0, 1),
            "register_date": random_date(),
            "last_deactivate_date": None,
        }
        status = Status(**status_data)
        db.session.add(status)
        db.session.commit()


def generate_random_review():
    """Generates a random review with a title, content, and star rating.

    Based on the randomly chosen star rating, the function generates a review title and content from
    pre-defined categories: 'bad', 'good', or 'excellent'. A random star rating is chosen, and
    corresponding text for the review is generated.

    Returns
    -------
    tuple
        A tuple containing the title (str), content (str), and star rating (int) of the review.
    """
    # Titles categorized by star rating groups
    titles = {
        "bad": [
            "Not worth the money",
            "Very disappointing",
            "Regret buying",
            "Waste of money",
            "Poor quality",
            "Terrible experience",
            "Product broke quickly",
            "False advertising",
            "Not as described",
            "Horrible service",
            "Disappointing results",
            "Wouldn't recommend",
            "Very low quality",
            "Frustrating purchase",
            "Not worth the hype",
            "Overpriced garbage",
            "Worst purchase ever",
            "Complete letdown",
            "Not durable at all",
            "Avoid this product",
        ],
        "good": [
            "Quite satisfied",
            "Better than expected",
            "Good, but could improve",
            "Decent product",
            "Worth the price",
            "Happy with the purchase",
            "Meets expectations",
            "Solid quality",
            "Good value for money",
            "Pleasant surprise",
            "Performs well",
            "Would buy again",
            "Useful and practical",
            "Does the job",
            "Satisfactory performance",
            "Reasonable quality",
            "Good, but some issues",
            "Works as expected",
            "Happy overall",
            "Pretty good purchase",
        ],
        "excellent": [
            "Fantastic product!",
            "Exceeded expectations",
            "Best purchase ever!",
            "Perfect in every way",
            "Incredible quality",
            "Highly recommend",
            "Top-notch product",
            "Absolutely love it",
            "Impressive results",
            "Amazing experience",
            "Worth every penny",
            "Best decision ever",
            "Can't live without it",
            "Superior quality",
            "Outstanding performance",
            "Perfect choice",
            "Thrilled with this product",
            "Couldn't be happier",
            "Five stars all the way",
            "Must-have item",
        ],
    }

    # Contents categorized by star rating groups
    contents = {
        "bad": [
            "This product really let me down. Wouldn't recommend.",
            "The quality was poor and didn't meet expectations.",
            "A complete waste of money. I regret buying this.",
            "It broke after just a week. Very disappointed.",
            "Terrible experience overall. Not what I expected.",
            "False advertising, the product doesn't work as described.",
            "I had high hopes but was sorely disappointed.",
            "The material is cheap and flimsy.",
            "Not worth even half the price.",
            "Bad customer service and bad product.",
            "It stopped working after a few uses.",
            "Definitely wouldn't buy this again.",
            "Overhyped and under-delivered.",
            "Extremely dissatisfied with this purchase.",
            "The product arrived damaged and wasn't usable.",
            "Poor quality control. It's full of defects.",
            "Feels cheaply made and didn't last.",
            "It's unusable. Complete failure.",
            "Very frustrating to use. A total waste.",
            "Avoid this product at all costs!",
        ],
        "good": [
            "The product is decent for its price. Satisfied with the performance.",
            "Pretty good overall. Some minor issues.",
            "Better than expected. I'm quite happy with it.",
            "Does what it promises, though there's room for improvement.",
            "Worth the money for what it offers.",
            "Solid performance and generally happy with it.",
            "I had a good experience, though it could be improved in some areas.",
            "Performs well for the price.",
            "Happy with the purchase, though not perfect.",
            "The product does its job without any major problems.",
            "Good value for money, does what it's supposed to.",
            "I am content with the results.",
            "Works well for most tasks, but could be better.",
            "It’s solid overall with a few minor issues.",
            "Good product but I’ve seen better.",
            "Overall, a decent buy. Would consider buying again.",
            "For the price, this is pretty good.",
            "Performs adequately for its cost.",
            "Quite happy with how it turned out.",
            "Good quality, though there are some improvements that could be made.",
        ],
        "excellent": [
            "Absolutely fantastic! Best purchase I've made.",
            "Exceeded all expectations. Very pleased with this.",
            "This is the best product I've used in a long time.",
            "It performs incredibly well. Highly recommend it.",
            "Perfect! Couldn't ask for more.",
            "Amazing quality and great value.",
            "I'm extremely happy with this product. It works flawlessly.",
            "Superb build and functionality.",
            "Impressed by the attention to detail and performance.",
            "Five stars for sure. Worth every penny.",
            "One of the best purchases I've ever made.",
            "Can't imagine living without this now.",
            "Superb experience from start to finish.",
            "Couldn't be happier with how this turned out.",
            "Highly recommend to everyone! It's perfect.",
            "Outstanding quality and great design.",
            "Completely satisfied with this purchase.",
            "Top-tier performance and quality.",
            "This product is a game changer.",
            "Best decision I've ever made. Highly recommend!",
        ],
    }

    # Generate a random star rating (1 to 5)
    stars = choices(
        [1, 2, 3, 4, 5],  # Star ratings
        weights=[1, 1, 2, 3, 8],  # Corresponding odds (more weight = more likely)
        k=1,  # Number of items to choose
    )[0]

    # Decide which type of review to generate based on the stars
    if stars in [1, 2]:
        review_type = "bad"
    elif stars in [3, 4]:
        review_type = "good"
    else:  # stars == 5
        review_type = "excellent"

    # Pick a random title and content from the appropriate group
    title = choice(titles[review_type])
    content = choice(contents[review_type])

    return title, content, stars


def create_test_reviews():
    """Generates random reviews for users and adds them to the database.

    This function fetches all user IDs from the database, then selects a random subset of users.
    For each selected user, a review is generated using `generate_random_review()` and added to the database.

    Returns
    -------
    None
        The function does not return anything. It commits each generated review to the database.
    """
    # Fetch all user IDs from the User model
    user_ids = db.session.query(User.id).all()

    # Flatten the list of tuples into a list of IDs
    user_ids = [user_id[0] for user_id in user_ids]

    # Return the specified number of random user IDs
    amount = randint(len(user_ids) * 20 // 100, len(user_ids) * 60 // 100)
    user_ids_sample = sample(user_ids, amount)

    for i in range(amount):
        current_user = User.query.get(int(user_ids_sample[i]))

        status = Status.query.get(int(user_ids_sample[i]))
        delta = datetime.today() - status.register_date
        random_days = randint(0, delta.days)

        title, content, stars = generate_random_review()

        review = Reviews(
            title=title,
            content=content,
            stars=stars,
            user_id=None if randint(0, 1) == 0 else current_user.id,
            submitted_at=status.register_date + timedelta(days=random_days),
        )
        db.session.add(review)
        db.session.commit()


def create_test_chats():
    """Generates random chat entries for users and adds them to the database.

    This function selects a random subset of users and generates a welcome message for each user
    in a chat. The message and user data are then stored in the database as a new chat entry.

    Returns
    -------
    None
        The function does not return anything. It commits each generated chat to the database.
    """
    # Fetch all user IDs from the User model
    user_ids = db.session.query(User.id).all()

    # Flatten the list of tuples into a list of IDs
    user_ids = [user_id[0] for user_id in user_ids]

    # Return the specified number of random user IDs
    amount = randint(len(user_ids) * 30 // 100, len(user_ids) * 80 // 100)
    user_ids_sample = sample(user_ids, amount)

    for i in range(amount):
        current_user = User.query.get(int(user_ids_sample[i]))

        welcome_text = f"Hi { current_user.name.title() }, welcome to Shrink.io! Go ahead and send me a message."

        status = Status.query.get(int(user_ids_sample[i]))
        delta = datetime.today() - status.register_date
        random_days = randint(0, delta.days)

        new_chat = Chat(
            name=f"Chat_{len(current_user.chats)}",
            chat_json=dumps(
                [
                    {
                        "identifier": "assistant",
                        "text": welcome_text,
                        "date_time": status.register_date + timedelta(days=random_days),
                    }
                ],
                default=json_util.default,
            ),
            user_id=current_user.id,
        )
        db.session.add(new_chat)
        db.session.commit()
