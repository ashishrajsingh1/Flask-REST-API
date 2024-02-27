import plotly.express as px
import pandas as pd
from flask import render_template
from flask_smorest import Blueprint
from models import StoreModel

blp = Blueprint("Graph", "graph", description="Operations on graph")


@blp.route("/generate_graph")
def generate_graph():
    try:
        stores = StoreModel.query.all()

        stores_data = [{'name': store.name, 'num_items': store.items.count()} for store in stores]

        store_names = [store['name'] for store in stores_data]
        num_items = [store['num_items'] for store in stores_data]

        fig = px.bar(x=store_names, y=num_items, labels={'x': 'Store Name', 'y': 'Number of Items'},
                     title='Number of Items in Each Store')

        graph_html = fig.to_html(full_html=False)

        return render_template("graph.html", graph_html=graph_html)

    except Exception as e:
        return str(e), 500
