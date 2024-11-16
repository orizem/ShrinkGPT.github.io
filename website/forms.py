# forms.py

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    HiddenField,
    PasswordField,
    SubmitField,
    TextAreaField,
    SelectField,
    BooleanField,
    RadioField,
)
from wtforms.validators import Length, EqualTo, InputRequired, DataRequired


class RegisterForm(FlaskForm):
    """Form for user registration.

    This form collects the user's personal details (username, name, lastname), profile photo,
    password, and password confirmation. It is used for creating a new user account.

    Attributes
    ----------
    username : StringField
        The username of the user.
    name : StringField
        The first name of the user.
    lastname : StringField
        The last name of the user.
    image : FileField
        The profile photo of the user.
    password : PasswordField
        The password for the user account.
    password_again : PasswordField
        A field to confirm the password.
    submit : SubmitField
        A button to submit the registration form.
    """

    username = StringField("Username", validators=[InputRequired(), Length(1, 64)])
    name = StringField("Name", validators=[InputRequired(), Length(1, 64)])
    lastname = StringField("Lastname", validators=[InputRequired(), Length(1, 64)])
    image = FileField(
        "Photo", validators=[FileAllowed(["jpg", "jpeg", "png"], "Images only!")]
    )
    password = PasswordField("Password", validators=[InputRequired()])
    password_again = PasswordField(
        "Password again", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    """Form for user login.

    This form is used by users to log into their account by entering their username, password, 
    and a time-based one-time password (TOTP) for two-factor authentication.

    Attributes
    ----------
    username : StringField
        The username of the user.
    password : PasswordField
        The password for the user account.
    token : StringField
        The TOTP token for two-factor authentication.
    submit : SubmitField
        A button to submit the login form.
    """

    username = StringField("Username", validators=[InputRequired(), Length(1, 64)])
    password = PasswordField("Password", validators=[InputRequired()])
    token = StringField(
        "Token",
        validators=[InputRequired(), Length(6, 6)],
        render_kw={"autocomplete": "off"},
    )
    submit = SubmitField("Login")


class ProfileForm(FlaskForm):
    """Form for editing user profile.

    This form allows users to update their name, lastname, and profile photo.

    Attributes
    ----------
    name : StringField
        The first name of the user.
    lastname : StringField
        The last name of the user.
    image : FileField
        The profile photo of the user.
    submit : SubmitField
        A button to submit the profile form.
    """

    name = StringField("Name", validators=[Length(1, 64)])
    lastname = StringField("Lastname", validators=[Length(1, 64)])
    image = FileField(
        "Photo", validators=[FileAllowed(["jpg", "jpeg", "png"], "Images only!")]
    )
    submit = SubmitField("Save")


class ChatEdit(FlaskForm):
    """Form for editing a chat name.

    This form allows the user to update the name of a specific chat.

    Attributes
    ----------
    name : StringField
        The name of the chat to be updated.
    """

    name = StringField("Name", validators=[Length(1, 20)])


class ReviewForm(FlaskForm):
    """Form for submitting a review.

    This form is used to create a review for a product, service, or entity. It allows users to
    input a title, content, rating (stars), and whether they want to publish it anonymously.

    Attributes
    ----------
    title : StringField
        The title of the review.
    content : TextAreaField
        The content or description of the review.
    stars : RadioField
        The star rating of the review (from 1 to 5).
    anonymous : BooleanField
        Whether the review should be published anonymously.
    submit : SubmitField
        A button to submit the review form.
    """
    
    title = StringField("Title", validators=[DataRequired(), Length(min=2, max=100)])
    content = TextAreaField(
        "Review", validators=[DataRequired(), Length(min=2, max=255)]
    )
    stars = RadioField(
        "Rating",
        choices=[
            (1, "1 Star"),
            (2, "2 Stars"),
            (3, "3 Stars"),
            (4, "4 Stars"),
            (5, "5 Stars"),
        ],
        coerce=int,
    )
    anonymous = BooleanField("Publish Anonymously")
    submit = SubmitField("Submit Review")
