import logging
from flask import render_template
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import CORS
from db import db
from models import ItemModel
from schemas import ItemSchema, ItemUpdateSchema

items_logger = logging.getLogger(__name__ + '.items')
items_logger.setLevel(logging.INFO)

handler = logging.FileHandler("items.log")
handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

items_logger.addHandler(handler)

blp = Blueprint("Items", "items", description="Operations on items")

CORS(blp)


@blp.route("/item")
def Items_page():
    return render_template("items.html")


@blp.route("/items/<string:item_id>")
class Item(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        try:
            item = ItemModel.query.get_or_404(item_id)
            return item

        except Exception as e:
            items_logger.error(f"Error during item retrieval: {str(e)}")
            abort(500, message="Internal Server Error")

    @jwt_required()
    def delete(self, item_id):
        try:
            item = ItemModel.query.get_or_404(item_id)
            db.session.delete(item)
            db.session.commit()

            items_logger.info(f"Item deleted successfully: Item ID - {item_id}")

            return {"message": "Item deleted."}

        except SQLAlchemyError as e:
            items_logger.error(f"Error during item deletion: {str(e)}")
            abort(500, message="Internal Server Error")

    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        try:
            item = ItemModel.query.get(item_id)

            if item:
                item.price = item_data["price"]
                item.name = item_data["name"]
            else:
                item = ItemModel(id=item_id, **item_data)

            db.session.add(item)
            db.session.commit()

            items_logger.info(f"Item updated successfully: Item ID - {item_id}")

            return item

        except SQLAlchemyError as e:
            items_logger.error(f"Error during item update: {str(e)}")
            abort(500, message="Internal Server Error")


@blp.route("/items")
class ItemList(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        try:
            return ItemModel.query.all()

        except Exception as e:
            items_logger.error(f"Error during items retrieval: {str(e)}")
            abort(500, message="Internal Server Error")

    @jwt_required(fresh=True)
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        try:
            if "price" not in item_data or "name" not in item_data:
                abort(400, message="Price and name are required fields.")

            item = ItemModel(**item_data)
            db.session.add(item)
            db.session.commit()

            items_logger.info(f"Item created successfully: Item ID - {item.id}, Name - {item.name}")

            return item

        except SQLAlchemyError as e:
            items_logger.error(f"Error during item creation: {str(e)}")
            abort(500, message="Internal Server Error")
