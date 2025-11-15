"""
Health check API routes
"""
from flask import Blueprint, jsonify
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)

def init_health_routes(app, chroma_db, conversation_logger, api_key):
    """
    Initialize health check routes with dependencies
    
    Args:
        app: Flask app instance
        chroma_db: ChromaDB manager instance
        conversation_logger: Conversation logger instance
        api_key: OpenAI API key
    """
    health_bp.chroma_db = chroma_db
    health_bp.conversation_logger = conversation_logger
    health_bp.api_key = api_key
    
    app.register_blueprint(health_bp, url_prefix='/api')

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check with service status"""
    chroma_db = health_bp.chroma_db
    conversation_logger = health_bp.conversation_logger
    api_key = health_bp.api_key
    
    health_data = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Student Support Chatbot (Enhanced)',
        'services': {
            'chromadb': chroma_db is not None,
            'conversation_logger': conversation_logger is not None,
            'openai_api': api_key != "sk-demo-key-for-testing"
        }
    }
    
    # Add detailed service info if available
    if chroma_db:
        try:
            health_data['chromadb_analytics'] = chroma_db.get_analytics()
        except:
            health_data['chromadb_analytics'] = {"error": "Could not fetch analytics"}
    
    return jsonify(health_data)

