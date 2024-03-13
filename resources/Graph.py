from flask import render_template
from flask_smorest import Blueprint

blp = Blueprint("MainGraph", "Maingraph", description="Main Graph Page")


@blp.route("/main_graph")
def main_graph():
    return render_template("Graph.html")
