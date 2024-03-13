from flask import render_template
from flask_smorest import Blueprint

blp = Blueprint("Home", __name__)


@blp.route("/")
@blp.route("/home")
def home_page():
    return render_template("Home.html")
