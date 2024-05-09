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
    """Registration form."""

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
    """Login form."""

    username = StringField("Username", validators=[InputRequired(), Length(1, 64)])
    password = PasswordField("Password", validators=[InputRequired()])
    token = StringField(
        "Token",
        validators=[InputRequired(), Length(6, 6)],
        render_kw={"autocomplete": "off"},
    )
    submit = SubmitField("Login")


class ProfileForm(FlaskForm):
    """Profile form."""

    name = StringField("Name", validators=[Length(1, 64)])
    lastname = StringField("Lastname", validators=[Length(1, 64)])
    image = FileField(
        "Photo", validators=[FileAllowed(["jpg", "jpeg", "png"], "Images only!")]
    )
    submit = SubmitField("Save")


class ChatEdit(FlaskForm):
    """Profile form."""

    name = StringField("Name", validators=[Length(1, 20)])


class ReviewForm(FlaskForm):
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
