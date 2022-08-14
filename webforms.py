from flask_wtf import FlaskForm
from wtforms import (
    TextAreaField,
    StringField,
    SubmitField,
    EmailField,
    PasswordField,
    # RadioField,
    SelectField,
    # BooleanField,
    # ValidationError,
)
from wtforms.validators import DataRequired, Email, EqualTo
from flask_ckeditor import CKEditorField

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


class EditUserForm(FlaskForm):

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

    user_access = SelectField(
        label="Accsess Level",
        choices=[
            "user",
            "admin",
        ],
        validators=[
            DataRequired("Choose One"),
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

    content = CKEditorField(
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


# Create a Form class For Search
class SearchForm(FlaskForm):

    searched = StringField(
        "Search",
        validators=[
            DataRequired(),
        ],
    )

    submit = SubmitField("Submit")
