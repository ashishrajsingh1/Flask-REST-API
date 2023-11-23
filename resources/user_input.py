from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import db
from models.user_input import DocumentModel
from schemas import DocumentSchema

blp = Blueprint('document', 'document', url_prefix='/document', description='Document operations')


@blp.route('', methods=['POST'])
class DocumentCreate(MethodView):

    @blp.arguments(DocumentSchema, location='json')
    @blp.response(201, DocumentSchema)
    def post(self, document_data):
        if 'file' not in request.files:
            abort(422, message='Missing file field in the request.')

        file = request.files['file']

        if DocumentModel.query.filter_by(name=document_data['name']).first():
            abort(409, message='A document with that name already exists.')

        document = DocumentModel(name=document_data['name'], content=file.read())
        db.session.add(document)
        db.session.commit()

        return DocumentSchema.dump(document), 201


@blp.route('/<int:document_id>', methods=['GET'])
class DocumentRetrieve(MethodView):

    @blp.response(200, DocumentSchema)
    @blp.response(404, 'Document not found')
    def get(self, document_id):
        document = DocumentModel.query.get(document_id)
        if not document:
            abort(404, message='Document not found')

        return DocumentSchema.dump(document), 200
