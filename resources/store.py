import logging
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db import db
from models import StoreModel
from schemas import StoreSchema

stores_logger = logging.getLogger(__name__ + '.stores')
stores_logger.setLevel(logging.INFO)

handler = logging.FileHandler("stores.log")
handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

stores_logger.addHandler(handler)

blp = Blueprint("Stores", __name__, description="Operations on stores")


@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        try:
            store = StoreModel.query.get_or_404(store_id)
            return store

        except Exception as e:
            stores_logger.error(f"Error during store retrieval: {str(e)}")
            abort(500, message="Internal Server Error")

    def delete(self, store_id):
        try:
            store = StoreModel.query.get_or_404(store_id)
            db.session.delete(store)
            db.session.commit()

            stores_logger.info(f"Store deleted successfully: Store ID - {store_id}")

            return {"message": "Store deleted"}, 200

        except SQLAlchemyError as e:
            stores_logger.error(f"Error during store deletion: {str(e)}")
            abort(500, message="Internal Server Error")


@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        try:
            return StoreModel.query.all()

        except Exception as e:
            stores_logger.error(f"Error during stores retrieval: {str(e)}")
            abort(500, message="Internal Server Error")

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        try:
            if "name" not in store_data:
                abort(400, message="Name is a required field for a store.")

            store = StoreModel(**store_data)
            db.session.add(store)
            db.session.commit()

            stores_logger.info(f"Store created successfully: Store ID - {store.id}, Name - {store.name}")

            return store

        except IntegrityError:
            stores_logger.error(f"Error during store creation: Store with the same name already exists.")
            abort(400, message="A store with that name already exists.")
        except SQLAlchemyError as e:
            stores_logger.error(f"Error during store creation: {str(e)}")
            abort(500, message="Internal Server Error")
