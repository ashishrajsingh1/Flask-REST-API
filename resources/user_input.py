from flask import request
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from db import db
from models.user_input import DocumentModel
from schemas import DocumentSchema

blp = Blueprint("Documents", "Documents", description="Operations on Documents")


@blp.route('/document', methods=['POST'])
class DocumentCreate(MethodView):

    @blp.arguments(DocumentSchema(only=('name',)), location='json')
    @blp.response(201, DocumentSchema)
    def post(self, args):
        file = request.files['file']
        document = DocumentModel(name=args['name'], content=file.read())
        db.session.add(document)
        db.session.commit()
        return document, 201


@blp.route('/document/<int:document_id>', methods=['GET'])
class DocumentRetrieve(MethodView):

    @blp.response(200, DocumentSchema)
    @blp.response(404, 'Document not found')
    def get(self, document_id):
        document = DocumentModel.query.get(document_id)
        if not document:
            abort(404, message='Document not found')

        return document
