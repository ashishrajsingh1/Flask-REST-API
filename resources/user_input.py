import io
import logging
from flask import request, send_file, render_template
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import db
from models.user_input import DocumentModel
from schemas import DocumentSchema
from werkzeug.utils import secure_filename

document_logger = logging.getLogger(__name__ + '.document')
document_logger.setLevel(logging.INFO)

handler = logging.FileHandler("document.log")
handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

document_logger.addHandler(handler)

blp = Blueprint('document', 'document', description='Document operations')


@blp.route("/document")
def Document():
    return render_template("Document.html")


@blp.route('/documents', methods=['POST'])
class DocumentCreate(MethodView):

    @blp.arguments(DocumentSchema, location='form')
    @blp.response(201, DocumentSchema)
    def post(self, document_data):
        try:
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

            document_logger.info(f"Document created successfully: {name}")

            return {"message": "Document created successfully."}, 201

        except Exception as e:
            document_logger.error(f"Error during document creation: {str(e)}")
            return {"message": "Internal Server Error"}, 500


@blp.route('/documents/<int:document_id>', methods=['GET'])
class DocumentRetrieve(MethodView):

    @blp.response(200, DocumentSchema)
    @blp.response(404, 'Document not found')
    def get(self, document_id):
        try:
            document = DocumentModel.query.get(document_id)
            if not document:
                abort(404, message='Document not found')

            document_logger.info(f"Document retrieved successfully: {document.name}")

            return send_file(io.BytesIO(document.content), as_attachment=True, download_name=document.name)

        except Exception as e:
            document_logger.error(f"Error during document retrieval: {str(e)}")
            return {"message": "Internal Server Error"}, 500

    def delete(self, document_id):
        try:
            document = DocumentModel.query.get(document_id)
            db.session.delete(document)
            db.session.commit()

            document_logger.info(f"Document deleted successfully: {document_id}")

            return {"message": "Document deleted successfully"}, 200

        except Exception as e:
            document_logger.error(f"Error during document deletion: {str(e)}")
            return {"message": "Internal Server Error"}, 500
