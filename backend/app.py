"""
Main Flask application
"""
from flask import Flask
from flask_cors import CORS
import openai
import logging

from config import (
    OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL,
    FLASK_HOST, FLASK_PORT, FLASK_DEBUG,
    CORS_ORIGINS, CORS_METHODS, CORS_HEADERS
)
from chroma_manager import get_chroma_manager
from conversation_logger import get_conversation_logger
from routes.chat import init_chat_routes
from routes.knowledge import init_knowledge_routes
from routes.health import init_health_routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": CORS_ORIGINS,
        "methods": CORS_METHODS,
        "allow_headers": CORS_HEADERS
    }
})

# Initialize OpenAI client
if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
    print("⚠️  Warning: Using demo API key. Please set OPENAI_API_KEY in .env file for production use.")
    api_key = "sk-demo-key-for-testing"
else:
    api_key = OPENAI_API_KEY

client = openai.OpenAI(
    api_key=api_key,
    base_url=OPENAI_BASE_URL
)

# Initialize enhanced services
logger.info("Initializing enhanced services...")
try:
    chroma_db = get_chroma_manager()
    conversation_logger = get_conversation_logger()
    logger.info("✅ All enhanced services initialized successfully!")
except Exception as e:
    logger.error(f"❌ Error initializing services: {e}")
    chroma_db = None
    conversation_logger = None

# Initialize routes
init_chat_routes(app, chroma_db, conversation_logger, client)
init_knowledge_routes(app, chroma_db)
init_health_routes(app, chroma_db, conversation_logger, api_key)

if __name__ == '__main__':
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)
