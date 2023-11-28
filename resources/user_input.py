import io
from flask import request, send_file
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import db
from models.user_input import DocumentModel
from schemas import DocumentSchema
from werkzeug.utils import secure_filename


blp = Blueprint('document', 'document', url_prefix='/documents', description='Document operations')


@blp.route('', methods=['POST'])
class DocumentCreate(MethodView):

    @blp.arguments(DocumentSchema, location='form')
    @blp.response(201, DocumentSchema)
    def post(self, document_data):
        name = document_data['name']
        file = request.files['file']

        if not file:
            abort(400, message='No file provided')

        allowed_extensions = {'pdf', 'doc', 'docx'}
        if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            abort(400, message='Invalid file type. Only PDF, DOC, and DOCX files are allowed.')

        if DocumentModel.query.filter_by(name=name).first():
            abort(409, message='A document with that name already exists.')

        filename = secure_filename(file.filename)
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

        return send_file(io.BytesIO(document.content), as_attachment=True, download_name=document.name)

    def delete(self, document_id):
        document = DocumentModel.query.get(document_id)
        db.session.delete(document)
        db.session.commit()

        return {"message : Document deleted successfully"}, 200
