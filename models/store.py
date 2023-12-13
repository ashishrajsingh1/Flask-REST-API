import uuid
from db import db


def generate_uuid():
    return str(uuid.uuid4().hex)


class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.String(40), primary_key=True, default=generate_uuid(), unique=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    tags = db.relationship("TagModel", back_populates="store", lazy="dynamic")
    items = db.relationship("ItemModel", back_populates="store", lazy="dynamic")
