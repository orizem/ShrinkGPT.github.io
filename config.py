# config.py

import os

SECRET_KEY = b"x*n\x9f\xa8\x00\x1b\xd4\xf4G\xaaO\x99\xafSC\x97\xcfC\x9a\x1f!\x1ai!3\xad\x06\xf5\xd2O2"
PROJECT_PATH = rf"{os.getcwd()}\website"
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", f"sqlite:///{PROJECT_PATH}\\db.sqlite")
SQLALCHEMY_TRACK_MODIFICATIONS = False
SESSION_TYPE = "filesystem"
