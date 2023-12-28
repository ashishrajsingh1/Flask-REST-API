import logging
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from db import db
from models import TagModel, StoreModel, ItemModel
from schemas import TagSchema, TagAndItemSchema

tags_logger = logging.getLogger(__name__ + '.tags')
tags_logger.setLevel(logging.INFO)

handler = logging.FileHandler("tags.log")
handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

tags_logger.addHandler(handler)

blp = Blueprint("Tags", "tags", description="Operations on tags")


@blp.route("/store/<string:store_id>/tag")
class TagsInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        try:
            store = StoreModel.query.get_or_404(store_id)
            return store.tags.all()

        except Exception as e:
            tags_logger.error(f"Error during tags retrieval: {str(e)}")
            abort(500, message="Internal Server Error")

    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        try:
            if "name" not in tag_data:
                abort(400, message="Name is a required field for a tag.")

            if TagModel.query.filter(TagModel.store_id == store_id, TagModel.name == tag_data["name"]).first():
                abort(400, message="A tag with that name already exists in that store.")

            tag_data['store_id'] = store_id

            tag = TagModel(**tag_data)
            db.session.add(tag)
            db.session.commit()

            tags_logger.info(f"Tag created successfully: {tag_data['name']}")

            return tag

        except SQLAlchemyError as e:
            tags_logger.error(f"Error during tag creation: {str(e)}")
            abort(500, message="Internal Server Error")


@blp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagsToItem(MethodView):
    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        try:
            item = ItemModel.query.get_or_404(item_id)
            tag = TagModel.query.get_or_404(tag_id)

            item.tags.append(tag)
            db.session.add(item)
            db.session.commit()

            tags_logger.info(f"Tag linked to item successfully: Item ID - {item_id}, Tag ID - {tag_id}")

            return tag

        except SQLAlchemyError:
            tags_logger.error(f"Error during linking tag to item.")
            abort(500, message="Internal Server Error")

    @blp.response(200, TagAndItemSchema)
    def delete(self, item_id, tag_id):
        try:
            item = ItemModel.query.get_or_404(item_id)
            tag = TagModel.query.get_or_404(tag_id)

            item.tags.remove(tag)
            db.session.add(item)
            db.session.commit()

            tags_logger.info(f"Tag removed from item successfully: Item ID - {item_id}, Tag ID - {tag_id}")

            return {"message": "Item removed from tag", "item": item, "tag": tag}

        except SQLAlchemyError:
            tags_logger.error(f"Error during removing tag from item.")
            abort(500, message="Internal Server Error")


@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        try:
            tag = TagModel.query.get_or_404(tag_id)
            return tag

        except Exception as e:
            tags_logger.error(f"Error during tag retrieval: {str(e)}")
            abort(500, message="Internal Server Error")

    @blp.response(
        202,
        description="Deletes a tag if no item is tagged with it.",
        example={"message": "Tag deleted."},
    )
    @blp.alt_response(404, description="Tag not found.")
    @blp.alt_response(
        400,
        description="Returned if the tag is assigned to one or more items. In this case, the tag is not deleted.",
    )
    def delete(self, tag_id):
        try:
            tag = TagModel.query.get_or_404(tag_id)

            if not tag.items:
                db.session.delete(tag)
                db.session.commit()

                tags_logger.info(f"Tag deleted successfully: Tag ID - {tag_id}")

                return {"message": "Tag deleted."}

            abort(
                400,
                message="Could not delete tag. Make sure tag is not associated with any items, then try again."
            )

        except SQLAlchemyError as e:
            tags_logger.error(f"Error during tag deletion: {str(e)}")
            abort(500, message="Internal Server Error")
