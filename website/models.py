# models.py

from json import loads, dumps
from os import urandom
from base64 import b32encode
from onetimepass import valid_totp
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model

    Represents a user in the application. This model stores personal information
    such as username, name, password hash, and OTP secret. It also manages user status
    and provides methods for handling authentication and two-factor authentication (TFA).

    Attributes
    ----------
    id : int
        Primary key for the user.
    username : str
        Username for the user (unique).
    name : str
        First name of the user.
    lastname : str
        Last name of the user.
    image_data : bytes, optional
        Profile image data for the user.
    image_filename : str, optional
        Filename for the user's profile image.
    password_hash : str
        Hashed password for authentication.
    otp_secret : str
        Secret key for generating time-based one-time passwords (TOTP).
    chats : list of Chat
        Relationship for storing the user's chats.
    reviews : list of Reviews
        Relationship for storing the user's reviews.
    is_admin : Admin
        Relationship for determining if the user is an admin.
    status : Status
        Relationship for storing the user's status.
    """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    name = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    image_data = db.Column(db.LargeBinary, nullable=True)
    image_filename = db.Column(
        db.String(20), nullable=True, default="/static/image/default.png"
    )
    password_hash = db.Column(db.String(128))
    otp_secret = db.Column(db.String(16))
    chats = db.relationship(
        "Chat", backref=db.backref("chats", lazy=True)
    )  # Creating a relationship with the User model
    reviews = db.relationship("Reviews", backref="user", lazy=True)
    is_admin = db.relationship("Admin", backref="user", lazy=True)
    _status = db.relationship("Status", backref="user", lazy=True)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.otp_secret is None:
            # generate a random secret
            self.otp_secret = b32encode(urandom(10)).decode("utf-8")

    @property
    def password(self):
        """Password property setter, prevents direct access to the password.

        Raises
        ------
        AttributeError
            When trying to access the password attribute directly.
        """
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        """Set password hash for the user.

        Parameters
        ----------
        password : str
            The password to be hashed and set.
        """
        self.password_hash = generate_password_hash(password)

    @property
    def is_admin(self):
        """Check if the user is an admin.

        Returns
        -------
        bool
            `True` if the user is an admin, `False` otherwise.
        """
        return bool(Admin.query.filter_by(user_id=self.id).first())

    @property
    def full_name(self):
        """Get the full name of the user.

        Returns
        -------
        str
            The full name of the user, combining `name` and `lastname`.
        """
        return f"{self.name} {self.lastname}".title()

    @property
    def status(self):
        """Get the status of the user.

        Returns
        -------
        int or None
            The status code of the user if found, `None` otherwise.
        """
        # Get user status
        user_status = Status.query.filter_by(user_id=self.id).first()
        return user_status.status if user_status else None

    @status.setter
    def status(self, status):
        """Set the status of the user.

        Parameters
        ----------
        status : int
            The status code to be set for the user.
        """
        user_status = Status.query.filter_by(user_id=self.id).first()
        user_status.status = status

    def verify_password(self, password):
        """Verify the user's password.

        Parameters
        ----------
        password : str
            The password to be verified.

        Returns
        -------
        bool
            `True` if the password matches the stored hash, `False` otherwise.
        """
        return check_password_hash(self.password_hash, password)

    def get_totp_uri(self):
        """Get the URI for the user's OTP secret.

        Returns
        -------
        str
            The URI used for setting up the OTP app.
        """
        return f"otpauth://totp/Shrink.io:{self.username}?secret={self.otp_secret}&issuer=Shrink.io"

    def verify_totp(self, token):
        """Verify the OTP token provided by the user.

        Parameters
        ----------
        token : str
            The OTP token to be verified.

        Returns
        -------
        bool
            `True` if the token is valid, `False` otherwise.
        """
        return valid_totp(token, self.otp_secret)


class Admin(UserMixin, db.Model):
    """Admin model

    Represents an admin in the system. An admin is essentially a user with special
    privileges, and this model links a user to their admin status.

    Attributes
    ----------
    id : int
        Primary key for the admin.
    user_id : int
        Foreign key referencing the `users` table to link the admin to a user.
    """

    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(self, **kwargs):
        super(Admin, self).__init__(**kwargs)


class Status(UserMixin, db.Model):
    """Status model

    Represents the status of a user. This model is used to track whether a user is active,
    deactivated, or in registration steps. It also stores the registration and deactivation dates.

    Attributes
    ----------
    id : int
        Primary key for the status.
    user_id : int
        Foreign key referencing the `users` table.
    status : int
        Status code for the user: `-1` for deactivated, `0` for active, and other values
        represent different registration steps.
    register_date : datetime
        The date and time when the user registered.
    last_deactivate_date : datetime, optional
        The date and time when the user was last deactivated.
    """

    __tablename__ = "status"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(
        db.Integer, nullable=False
    )  # Deactivated:-1 | Active:0 | Registration Steps:n
    register_date = db.Column(db.DateTime, nullable=False)
    last_deactivate_date = db.Column(db.DateTime, nullable=True)

    def __init__(self, **kwargs):
        super(Status, self).__init__(**kwargs)


class Chat(UserMixin, db.Model):
    """Chat model

    Represents a chat conversation in the application. This model stores the chat data
    in JSON format and associates each chat with a user.

    Attributes
    ----------
    id : int
        Primary key for the chat.
    __name : str
        The name of the chat.
    chat_json : str
        The chat data stored as a JSON string.
    user_id : int
        Foreign key referencing the `users` table to associate the chat with a user.
    """

    __tablename__ = "chats"
    id = db.Column(db.Integer, primary_key=True)
    __name = db.Column(db.String(20), nullable=False)
    chat_json = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(self, **kwargs):
        super(Chat, self).__init__(**kwargs)

    @property
    def chat(self):
        """Get the chat data as a Python object.

        Returns
        -------
        list
            The chat data, parsed from the stored JSON.
        """
        return loads(self.chat_json) if self.chat_json else []

    @chat.setter
    def chat(self, value):
        """Set the chat data from a Python object.

        Parameters
        ----------
        value : list
            The chat data to be stored, will be serialized to JSON.
        """
        self.chat_json = dumps(value)

    @property
    def name(self):
        """Get the name of the chat.

        Returns
        -------
        str
            The name of the chat.
        """
        return self.__name

    @name.setter
    def name(self, name):
        """Set the name of the chat.

        Parameters
        ----------
        name : str
            The name of the chat.
        """
        self.__name = name


class Reviews(db.Model):
    """Reviews model

    Represents a review submitted by a user. This model stores review details such as
    the title, content, stars, and submission date. It also associates each review with
    a specific user.

    Attributes
    ----------
    id : int
        Primary key for the review.
    title : str
        The title of the review.
    content : str
        The content of the review.
    stars : int
        The star rating for the review (1 to 5).
    submitted_at : datetime
        The date and time when the review was submitted.
    user_id : int
        Foreign key referencing the `users` table to associate the review with a user.
    """

    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )  # nullable=True - Assuming anonymity is allowed
    title = db.Column(db.String(127), nullable=False)
    content = db.Column(db.String(255), nullable=False)
    stars = db.Column(db.Integer, nullable=False)
