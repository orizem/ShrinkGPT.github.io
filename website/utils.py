# utils.py

from os import listdir
from time import sleep
from flask import send_file
from typing import List, Union
from os.path import realpath, commonpath

# LOCAL IMPORTS
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