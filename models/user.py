import uuid
from db import db
from datetime import datetime


def generate_uuid():
    return str(uuid.uuid4().hex)


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(40), primary_key=True, default=generate_uuid(), unique=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def delete(self):
        self.deleted = True
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()
