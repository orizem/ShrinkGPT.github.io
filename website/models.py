# models.py

from json import loads, dumps
from os import urandom
from base64 import b32encode
from onetimepass import valid_totp
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model."""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    name = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    image_data = db.Column(db.LargeBinary, nullable=True)
    image_filename = db.Column(db.String(20), nullable=True, default="/static/image/default.png")
    password_hash = db.Column(db.String(128))
    otp_secret = db.Column(db.String(16))
    chats = db.relationship("Chat", backref=db.backref("chats", lazy=True)) # Creating a relationship with the User model

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.otp_secret is None:
            # generate a random secret
            self.otp_secret = b32encode(urandom(10)).decode("utf-8")

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_totp_uri(self):
        return f"otpauth://totp/Shrink.io:{self.username}?secret={self.otp_secret}&issuer=Shrink.io"

    def verify_totp(self, token):
        return valid_totp(token, self.otp_secret)
    
class Chat(UserMixin, db.Model):
    """Chat model."""
    __tablename__ = "chats"
    id = db.Column(db.Integer, primary_key=True)
    __name = db.Column(db.String(20), nullable=False)
    chat_json = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    
    def __init__(self, **kwargs):
        super(Chat, self).__init__(**kwargs)
        
    @property
    def chat(self):
        return loads(self.chat_json) if self.chat_json else []

    @chat.setter
    def chat(self, value):
        self.chat_json = dumps(value)
        
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name