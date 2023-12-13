import uuid
from db import db


def generate_uuid():
    return str(uuid.uuid4().hex)


class ItemModel(db.Model):
    __tablename__ = "items"

    id = db.Column(db.String(40), primary_key=True, default=generate_uuid(), unique=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    price = db.Column(db.Float(precision=2), unique=False, nullable=False)
    store_id = db.Column(db.String, db.ForeignKey("stores.id"), unique=False, nullable=False)
    store = db.relationship("StoreModel", back_populates="items")
    tags = db.relationship("TagModel", back_populates="items", secondary="items_tags")
