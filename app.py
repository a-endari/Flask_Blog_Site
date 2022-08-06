from flask import Flask, render_template

# Create a Flask instance

app = Flask(__name__)

# Create a route decorator
@app.route("/")
def index():
    favorite_pizzas = ["cheese", "pepperoni", "beef & garlic"]
    name = "Abbas endari"
    stuff = "this is <strong> Bold text </strong>"
    return render_template("index.html", name=name, stuff=stuff, pizzas=favorite_pizzas)


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


# the code bellow is to run the file directly from IDE
if __name__ == "__main__":
    app.run(debug=True)
