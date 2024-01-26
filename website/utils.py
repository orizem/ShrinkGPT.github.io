# utils.py

from os import listdir
from time import sleep
from typing import Callable
from typing import List, Union
from flask_login import current_user
from os.path import realpath, commonpath
from flask import render_template, redirect, url_for, send_file

# LOCAL IMPORTS
from .models import User

# PROJECT IMPORTS
from config import PROJECT_PATH

# PRIVATE
def __get_all_images(start_with: Union[str, List]):
    IMAGE_PATH = rf"{PROJECT_PATH}\static\image"
    
    if not isinstance(start_with, list):
       start_with = [start_with]
    
    images = []
    for sw in start_with:
        images = images + [img for img in listdir(IMAGE_PATH)
                if img.lower().startswith(sw) and
                (img.endswith(".jpg") or
                img.endswith(".jpeg") or
                img.endswith(".png"))]
    return images

# PUBLIC
def generate_slide_show(start_with: Union[str, List]): 
    images = __get_all_images(start_with=start_with)
    
    # Instantly load image without sleep
    with open(rf"{PROJECT_PATH}\static\image\{images[-1]}", "rb") as img_file:
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + img_file.read() + b"\r\n") 
        
    while True:
        for image_name in images:
            try:
                with open(rf"{PROJECT_PATH}\static\image\{image_name}", "rb") as img_file:
                    yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + img_file.read() + b"\r\n") 
                sleep(5)
            except IndexError:
                # Removes deprecated image names.
                images = list(set(images) - {image_name})

def safe_send_default_image():
    base = rf"{PROJECT_PATH}\static\image"
    safepath = realpath(rf"{PROJECT_PATH}\static\image\default.png")
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

def restricted_route_decorator(func: Callable):
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
    def wrapped(*args, **kwargs):
        if (current_user == None) or (current_user.is_authenticated == False):
            return render_template("404.html", err_msg="The page you where looking for could not be found."), 404  
        
        user = get_current_user()
        if user is None:
            return redirect(url_for("views.index"))
        
        res = func(*args, **kwargs)
        return res
    return wrapped