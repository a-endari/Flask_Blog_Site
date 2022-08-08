import os
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.exc import PendingRollbackError

load_dotenv()


# Create a Flask instance
app = Flask(__name__)

# Adding Database location to app.config

# old SQlite DataBase - used at first
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

# New mysql Database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("MYSQL_URI")

# to shut depracation warnnig off!
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = "False"

# Secret Key - needed for WTF or SQLALCHEMY
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# Initialize The Database from app! whitg the provided config files!
db = SQLAlchemy(app)


# Create database Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow())

    # Create representing string repr!
    def __repr__(self) -> str:
        return f"<Name: {self.name!r}>"


# Create a Form class for Database
class UserForm(FlaskForm):

    name = StringField(
        "Name",
        validators=[
            DataRequired("enter your name"),
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


# Create a Form class
class NamerForm(FlaskForm):
    name = StringField(
        "What's your name",
        validators=[
            DataRequired(),
        ],
    )
    submit = SubmitField("Submit")


# Create a route decorator for index
@app.route("/")
def index():
    favorite_pizzas = ["cheese", "pepperoni", "beef & garlic"]
    name = "abbas endari"
    stuff = "this is <strong> Bold text </strong>"
    return render_template("index.html", name=name, stuff=stuff, pizzas=favorite_pizzas)


# a page to view sers list and add new users
@app.route("/users/", methods=["GET", "POST"])
def add_user():
    form = UserForm()
    name = None
    our_users = Users.query.order_by(Users.date_added)
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
            flash("2")
            name = form.name.data
            form.name.data = ""
            form.email.data = ""
            our_users = Users.query.order_by(Users.date_added)
            return render_template(
                "users.html", name=name, form=form, our_users=our_users
            )
        else:
            flash("1")
    return render_template("users.html", name=name, form=form, our_users=our_users)


# Update User Records in Database
@app.route("/user-update/<int:id>", methods=["GET", "POST"])
def update_user(id):
    form = UserForm()
    user_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        previous_user = Users.query.filter_by(email=request.form.get("email")).first()
        if previous_user and id != previous_user.id:
            flash("1")
            return render_template("update.html", user=user_to_update, form=form)
        else:
            user_to_update.name = request.form.get("name")
            user_to_update.email = request.form.get("email")
            try:
                db.session.commit()
                flash("3")  # User info updated successfully!
                return redirect(url_for("add_user"))
            except:
                flash("4")  # Sorry! Something Went Wrong!
                return render_template("update.html", user=user_to_update, form=form)
    else:
        return render_template("update.html", user=user_to_update, form=form)


@app.route("/user/<name>")
def user(name):
    return render_template("user.html", name=name)


# create Custom Erroe Pages
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


# create name form page using flask-wtf and wtforms!
@app.route("/name-form", methods=["GET", "POST"])
def name():
    name = None
    form = NamerForm()
    # Validate Form:
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ""
        flash("Form submitted successfully!")
    return render_template(
        "nameform.html",
        name=name,
        form=form,
    )


# the code bellow is to run the file directly from IDE
if __name__ == "__main__":
    app.run(debug=True)
