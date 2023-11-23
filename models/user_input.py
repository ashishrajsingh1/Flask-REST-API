from db import db


class DocumentModel(db.Model):
    __tablename__ = "Documents"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    content = db.Column(db.LargeBinary)
