"""
Configuration and constants for the application
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-demo-key-for-testing")
OPENAI_BASE_URL = "https://aiportalapi.stu-platform.live/jpe"
OPENAI_MODEL = "gpt-4o-mini"

# Flask Configuration
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5001
FLASK_DEBUG = True

# CORS Configuration
CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_HEADERS = ["Content-Type", "Authorization"]

# File Upload Configuration
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# RAG Configuration
RAG_TOP_K = 3
RAG_RELEVANCE_THRESHOLD = 0.01  # Lowered from 0.7 to 0.01 for better recall

# FAQ Configuration
FAQ_TOP_K = 2
FAQ_SIMILARITY_THRESHOLD = 0.7
FAQ_CONFIDENCE_THRESHOLD = 0.8

