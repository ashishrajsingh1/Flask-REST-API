from flask import render_template
from flask_smorest import Blueprint

blp = Blueprint("Chartjsraph", "chartjsgraph", description="Operations on graph")


@blp.route("/bar")
def bar_js():
    return render_template("barchartjs.html")


@blp.route("/pie")
def pie_graph():
    return render_template("piechartjs.html")


@blp.route("/line")
def line_graph():
    return render_template("linechartjs.html")


@blp.route("/doughnut")
def doughnut_chart():
    return render_template("Doughnut.html")
