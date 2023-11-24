from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import db
from models.user_input import DocumentModel
from schemas import DocumentSchema

blp = Blueprint('document', 'document', url_prefix='/documents', description='Document operations')

document_schema_instance = DocumentSchema()


@blp.route('', methods=['POST'])
class DocumentCreate(MethodView):
    @blp.response(201, DocumentSchema)
    def post(self):
        if 'file' not in request.files:
            abort(422, message='Missing file field in the request.')

        file = request.files['file']

        if 'name' not in request.form:
            abort(422, message='Missing name field in the request.')

        name = request.form['name']

        if DocumentModel.query.filter_by(name=name).first():
            abort(409, message='A document with that name already exists.')

        document = DocumentModel(name=name, content=file.read())
        db.session.add(document)
        db.session.commit()
        return {"message": "Document created successfully."}, 201


@blp.route('/<int:document_id>', methods=['GET'])
class DocumentRetrieve(MethodView):

    @blp.response(200, DocumentSchema)
    @blp.response(404, 'Document not found')
    def get(self, document_id):
        document = DocumentModel.query.get(document_id)
        if not document:
            abort(404, message='Document not found')

        return {"message": "User retrieved successfully."}, 201
