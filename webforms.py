from flask_wtf import FlaskForm
from wtforms import (
    TextAreaField,
    StringField,
    SubmitField,
    EmailField,
    PasswordField,
    # BooleanField,
    # ValidationError,
)
from wtforms.validators import DataRequired, Email, EqualTo


# Create a Form class for Database
class UserForm(FlaskForm):

    name = StringField(
        "Name",
        validators=[
            DataRequired("enter your name"),
        ],
    )

    username = StringField(
        "User Name",
        validators=[
            DataRequired("enter your name"),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            EqualTo("password2", message="Passwords Must Match"),
        ],
    )
    password2 = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
        ],
    )

    email = EmailField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
        ],
    )
    submit = SubmitField("Submit")


# Create a Form class for PostForm Page
class PostForm(FlaskForm):
    """
    PostForm a model for post form
    """

    title = StringField(
        "Title",
        validators=[
            DataRequired("enter your name"),
        ],
    )

    author = StringField(
        "Author",
        validators=[
            DataRequired(),
        ],
    )

    content = TextAreaField(
        "Content",
        validators=[
            DataRequired(),
        ],
    )

    slug = StringField(
        "Slug",
        validators=[
            DataRequired(),
        ],
    )

    submit = SubmitField("Submit")


# Create a Form class For Login
class LoginForm(FlaskForm):

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
        ],
    )

    username = StringField(
        "Username",
        validators=[
            DataRequired("enter your name"),
        ],
    )

    submit = SubmitField("Submit")


# NOTE: Create a Form class
class NamerForm(FlaskForm):
    name = StringField(
        "What's your name",
        validators=[
            DataRequired(),
        ],
    )
    submit = SubmitField("Submit")
