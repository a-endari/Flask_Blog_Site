import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, flash, request, redirect, url_for, abort

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid as uuid
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from webforms import UserForm, PostForm, LoginForm, EditUserForm, SearchForm
from flask_ckeditor import CKEditor


load_dotenv()


# Create a Flask instance
app = Flask(__name__)

# Adding Database location to app.config


# old SQlite DataBase - used at first
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

# New mysql Database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("MYSQL_URI")

# Make CKEditor be offline
app.config["CKEDITOR_SERVE_LOCAL"] = True

# to shut depracation warnnig off!
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = "False"

# Secret Key - needed for WTF or SQLALCHEMY
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# Initialize The Database from app! whitg the provided config files!
# which provides "SQLALCHEMY_DATABASE_URI"
db = SQLAlchemy(app)

# This below is for Flask-Migrate stuff and makes that possible!
migrate = Migrate(app, db)


# Flask Login stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = (  # type: ignore
    "login"  # This sets the view that is redirected when login required!
)

# setting up CkEditor for rich text editing
ckeditor = CKEditor(app)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


# Create database Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    profile_pic = db.Column(db.String(255), nullable=False)

    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(
        db.String(100),
        nullable=False,
    )
    about = db.Column(db.Text(600))
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
    date_added = db.Column(db.DateTime, default=datetime.utcnow())
    access_level = db.Column(db.String(20), nullable=False, default="user")

    # user's many posts
    posts = db.relationship("Posts", backref="post_author")

    # Create representing string repr!
    def __repr__(self) -> str:
        return f"<Name: {self.name!r}>"

    # this Below is for passwords
    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, "sha256")

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


# Create Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(
        db.String(255),
    )
    author = db.Column(db.Integer, db.ForeignKey("users.id"))
    slug = db.Column(
        db.String(255),
    )
    content = db.Column(
        db.Text,
    )
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)


# Create a route decorator for index
@app.route("/")
@app.route("/index/")
def index():
    return render_template("index.html")


# pass stuff to navbar (to make search bar usable!)
@app.context_processor
def base():
    form = SearchForm()
    return dict(searchform=form)


# Search Funcion for NavbarSearch
@app.route("/search/", methods=["POST"])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        searched = form.searched.data
        posts = Posts.query.filter(Posts.content.like("%" + searched + "%"))
        orderd_posts = posts.order_by(Posts.title).all()
        return render_template(
            "search.html", posts=orderd_posts, searched=f"{searched!r}"
        )
    return render_template("search.html", posts=None)


# Blog post route - for all blog posts
@app.route("/posts/")
def posts():
    posts = Posts.query.order_by(
        Posts.date_posted.desc()
    )  # .desc() at the end is just like .title() added to a string!! it only reversez the order.
    return render_template("posts.html", posts=posts)


# Add-post page route to add a new post
@app.route("/add-post/", methods=["GET", "POST"])
@login_required
def add_post():
    form = PostForm()
    form.author.data = current_user.id
    form.slug.data = f"{datetime.today().strftime('%Y%m%d%H%M')}"
    if request.method == "POST":
        post = Posts(
            title=request.form.get("title"),
            author=request.form.get("author"),
            content=request.form.get("content"),
            slug=request.form.get("slug"),
        )
        # add post data to database
        db.session.add(post)
        db.session.commit()
        form.title.data = ""
        form.content.data = ""
        flash("10")  # Blog post submitted successfully
        return render_template(
            "add_post.html",
            form=form,
        )
    return render_template(
        "add_post.html",
        form=form,
    )


# Route for a individual blog post
@app.route("/<string:author>/<string:slug>/")
def post(author, slug):
    post = Posts.query.filter_by(slug=slug, author=author).first()
    if post:
        return render_template("post.html", post=post)
    return abort(404)


# Editor for Indivijual Posts. (edit_post page)
@app.route("/edit/", methods=["POST"])
def edit_post():
    post = Posts.query.get_or_404(request.form.get("id"))
    form = PostForm()
    form.content.data = (
        post.content
    )  # Because textareas in html-forms don't take defaul value!
    if "to_edit" in request.form:
        return render_template("edit_post.html", form=form, post=post)
    else:
        post.title = request.form.get("title")  # or form.title.data
        post.author = request.form.get("author")  # or form.author.data
        post.slug = request.form.get("slug")  # or form.slug.data
        post.content = request.form.get("content")  # or form.content.data
        try:
            db.session.commit()
            flash("11")  # Blog updated Successfully.
            return redirect(url_for("post", author=post.author, slug=post.slug))
        except:
            flash("4")  # Sorry! Something Went Wrong!
            return render_template("edit_post.html", form=form, post=post)


# Delete endpoint for posts
@app.route("/delete_post/", methods=["POST"])
@login_required
def delete_post():
    post_to_delete = Posts.query.get_or_404(request.form.get("id"))
    if (
        current_user.username == "admin"
        or current_user.username == post_to_delete.post_author.username
    ):

        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash("12")  # Post successfully deleted.
            return redirect(url_for("posts"))
        except:
            flash("4")  # Sorry! Something Went Wrong!
            return redirect(url_for("posts"))
    flash("13")
    return redirect(url_for("posts"))


# Route view sers list and add new users
@app.route("/new_user/", methods=["GET", "POST"])
def add_user():
    form = UserForm()
    name = None
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hashing password
            if form.username.data == "admin":
                access_level = "admin"
            else:
                access_level = "user"
            user = Users(
                name=form.name.data,
                username=form.username.data,
                email=form.email.data,
                access_level=access_level,
                password=form.password.data,
            )
            db.session.add(user)
            db.session.commit()
            flash("2")
            name = form.name.data
            form.name.data = ""
            form.username.data = ""
            form.email.data = ""
            form.password.data = ""
            form.password2.data = ""
            our_users = Users.query.order_by(Users.date_added)
            return render_template(
                "user_register.html", name=name, form=form, our_users=our_users
            )
        else:
            flash("1")
    return render_template("user_register.html", name=name, form=form)


# Update User Records in Database
@app.route("/user-edit/<int:id>/", methods=["GET", "POST"])
@login_required
def edit_user(id):
    if current_user.access_level == "admin":
        form = EditUserForm()
        user_to_update = Users.query.get_or_404(id)
        form.about.data = user_to_update.about
        if form.validate_on_submit():
            previous_user = Users.query.filter_by(
                username=request.form.get("username")
            ).first()
            if previous_user and id != previous_user.id:
                flash("1")
                return render_template("edit_user.html", user=user_to_update, form=form)
            else:
                user_to_update.name = request.form.get("name")
                user_to_update.username = request.form.get("username")
                user_to_update.email = request.form.get("email")
                user_to_update.about = request.form.get("about")
                user_to_update.access_level = request.form.get("user_access")
                # user_to_update.password = request.form.get("password")
                # user_to_update.password2 = request.form.get("password2")
                try:
                    db.session.commit()
                    flash("3")  # User info updated successfully!
                    return redirect(url_for("user_management"))
                except:
                    flash("4")  # Sorry! Something Went Wrong!
                    return render_template(
                        "edit_user.html", user=user_to_update, form=form
                    )
        else:
            return render_template("edit_user.html", user=user_to_update, form=form)
    flash("Log in as an administrator to access this page.")
    return redirect(url_for("dashboard"))


@app.route("/users-managemment/")
@login_required
def user_management():
    if current_user.access_level == "admin":
        users = Users.query.all()
        return render_template("users_management.html", users=users)
    flash("Log in as an administrator to access this page.")
    return redirect(url_for("dashboard"))


# A route for deleting users from database
@app.route("/delete_user/<int:id>/")
@login_required
def delete_user(id):
    user_to_delete = Users.query.get_or_404(id)
    if (
        current_user.username == "admin"
        or current_user.username == user_to_delete.username
    ):
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("5")  # User successfully deleted.
            return redirect(url_for("add_user"))
        except:
            flash("4")  # Sorry! Something Went Wrong!
            return redirect(url_for("add_user"))
    flash("14")
    return redirect(url_for("dashboard"))


# Login page with validating hashed passwords
@app.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # if request.method == "POST":
        user = Users.query.filter_by(username=request.form.get("username")).first()
        if user:
            if user.verify_password(request.form.get("password")):
                login_user(user)  # This is the Flask Login thing
                flash("Login Successfull")
                return redirect(url_for("dashboard"))
            flash("6")  # Incorrect password
            return render_template("login.html", form=form)
        flash("7")  # username not in database
        return render_template("login.html", form=form)
    return render_template("login.html", form=form)


# The endpoint (view!) used to log current user out
@app.route("/logout/", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("Logged out Successfully.")
    return redirect(url_for("login"))


# Route to user-profile/dashboard
@app.route("/dashboard/", methods=["GET", "POST"])
@login_required
def dashboard():
    form = EditUserForm()
    user_to_update = current_user
    form.about.data = user_to_update.about
    if form.validate_on_submit():

        user_to_update.name = request.form.get("name")
        user_to_update.username = request.form.get("username")
        user_to_update.email = request.form.get("email")
        user_to_update.access_level = request.form.get("user_access")
        user_to_update.about = request.form.get("about")

        if request.files["profile_pic"]:
            # profile pic stuff
            user_profile_pic = request.files["profile_pic"]
            secure_profile_pic_name = secure_filename(user_profile_pic.filename)
            # Set UUID
            pic_uuid_name = str(uuid.uuid1()) + "_" + secure_profile_pic_name
            user_profile_pic.save(
                os.path.join("static/images/profile_pictures", pic_uuid_name)
            )
            user_to_update.profile_pic = pic_uuid_name
        try:
            db.session.commit()
            flash("3")  # User info updated successfully!
            return redirect(url_for("dashboard"))
        except:
            flash("4")  # Sorry! Something Went Wrong!
            return render_template("dashboard.html", user=user_to_update, form=form)

    return render_template("dashboard.html", user=user_to_update, form=form)


# Error-Handler for Page Not Found Errors.
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Error-Handler for Internal Server Errors.
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


# The code bellow is to run the file directly from IDE
if __name__ == "__main__":
    app.run(debug=True)
