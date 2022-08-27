import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base config."""

    # Secret Key - needed for WTF or SQLALCHEMY.
    SECRET_KEY = os.environ.get("SECRET_KEY")

    ### Adding Database location to app.config
    # SQlite DataBase URI - used at first not in use any more!
    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

    # New mysql Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("MYSQL_URI")

    # Make CKEditor be offline.
    CKEDITOR_SERVE_LOCAL = True

    # to shut depracation warnnig off!
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Setting up upload folder for profile images.
    UPLOAD_FOLDER = "static/images/profile_pictures"
    PIC_UPLOAD_FOLDER = "static/images/profile_pictures"

    # Default folders
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"

    # Cookie Session name Config! (Not Used Yet!).
    # SESSION_COOKIE_NAME = environ.get('SESSION_COOKIE_NAME')


class DevConfig(Config):
    FLASK_ENV = "development"
    FLASK_DEBUG = True
    TESTING = True


class ProdConfig(Config):
    FLASK_ENV = "production"
    DEBUG = False
    TESTING = False
    FLASK_DEBUG = True
