"""
Knowledge base API routes
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from urllib.parse import unquote
import logging

from utils.file_processor import allowed_file, extract_text_from_file
from config import ALLOWED_EXTENSIONS

logger = logging.getLogger(__name__)

knowledge_bp = Blueprint('knowledge', __name__)

def init_knowledge_routes(app, chroma_db):
    """
    Initialize knowledge base routes with dependencies
    
    Args:
        app: Flask app instance
        chroma_db: ChromaDB manager instance
    """
    knowledge_bp.chroma_db = chroma_db
    app.register_blueprint(knowledge_bp, url_prefix='/api/knowledge')

@knowledge_bp.route('/upload-file', methods=['POST'])
def upload_file():
    """Upload file and add to knowledge base"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            return jsonify({'error': 'File type not allowed. Supported: PDF, DOCX, TXT'}), 400
        
        chroma_db = knowledge_bp.chroma_db
        if not chroma_db:
            return jsonify({'error': 'ChromaDB not initialized'}), 500
        
        # Get optional parameters
        category = request.form.get('category', 'general')
        title = request.form.get('title', secure_filename(file.filename))
        
        # Read file content
        file_content = file.read()
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        
        # Extract text based on file type
        try:
            text_content = extract_text_from_file(file_content, file_extension)
        except ImportError as e:
            return jsonify({'error': f'Required library not installed: {str(e)}'}), 500
        except Exception as e:
            return jsonify({'error': f'Error extracting text: {str(e)}'}), 500
        
        if not text_content or len(text_content.strip()) == 0:
            return jsonify({'error': 'File is empty or could not extract text'}), 400
        
        # Add to knowledge base
        chunk_ids = chroma_db.add_document_from_text(
            title=title,
            content=text_content,
            category=category
        )
        
        return jsonify({
            'success': True,
            'message': 'File uploaded and processed successfully',
            'title': title,
            'category': category,
            'chunks_count': len(chunk_ids),
            'chunk_ids': chunk_ids,
            'text_length': len(text_content)
        }), 200
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@knowledge_bp.route('/upload-text', methods=['POST'])
def upload_text():
    """Upload text directly to knowledge base"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        title = data.get('title', '')
        content = data.get('content', '')
        category = data.get('category', 'general')
        
        if not title or not content:
            return jsonify({'error': 'Title and content are required'}), 400
        
        chroma_db = knowledge_bp.chroma_db
        if not chroma_db:
            return jsonify({'error': 'ChromaDB not initialized'}), 500
        
        chunk_ids = chroma_db.add_document_from_text(
            title=title,
            content=content,
            category=category
        )
        
        return jsonify({
            'success': True,
            'message': 'Text added to knowledge base successfully',
            'title': title,
            'category': category,
            'chunks_count': len(chunk_ids),
            'chunk_ids': chunk_ids
        }), 200
        
    except Exception as e:
        logger.error(f"Error uploading text: {e}")
        return jsonify({'error': f'Error adding text: {str(e)}'}), 500

@knowledge_bp.route('/documents', methods=['GET'])
def list_documents():
    """Get list of all documents in knowledge base"""
    try:
        chroma_db = knowledge_bp.chroma_db
        if not chroma_db:
            return jsonify({'error': 'ChromaDB not initialized'}), 500
        
        documents = chroma_db.get_all_documents()
        
        return jsonify({
            'success': True,
            'documents': documents,
            'total': len(documents)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        return jsonify({'error': f'Error listing documents: {str(e)}'}), 500

@knowledge_bp.route('/documents/<path:title>', methods=['DELETE'])
def delete_document(title):
    """Delete document from knowledge base"""
    try:
        chroma_db = knowledge_bp.chroma_db
        if not chroma_db:
            return jsonify({'error': 'ChromaDB not initialized'}), 500
        
        # URL decode title
        title = unquote(title)
        
        success = chroma_db.delete_document(title)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Document "{title}" deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': f'Document "{title}" not found'
            }), 404
        
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        return jsonify({'error': f'Error deleting document: {str(e)}'}), 500

