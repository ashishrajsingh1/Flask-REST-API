from flask import request
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from db import db
from models.user_input import DocumentModel
from schemas import DocumentSchema

blp = Blueprint("Documents", "Documents", description="Operations on Documents")


@blp.route('/document', methods=['POST'])
class DocumentCreate(MethodView):

    @blp.response(201, DocumentSchema)
    def post(self):
        if 'file' not in request.files:
            abort(422, message='Missing file field in the request.')

        file = request.files['file']

        # Check if the 'name' field is present in the JSON data
        if 'name' not in request.form:
            abort(422, message='Missing name field in the request.')

        name = request.form['name']

        document = DocumentModel(name=name, content=file.read())
        db.session.add(document)
        db.session.commit()
        return "File inserted successfully"


@blp.route('/document/<int:document_id>', methods=['GET'])
class DocumentRetrieve(MethodView):

    @blp.response(200, DocumentSchema)
    @blp.response(404, 'Document not found')
    def get(self, document_id):
        document = DocumentModel.query.get(document_id)
        if not document:
            abort(404, message='Document not found')

        return document
