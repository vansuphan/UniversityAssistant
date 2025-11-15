"""
File processing utilities for extracting text from various file formats
"""
import io
import logging

logger = logging.getLogger(__name__)

# File processing imports
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

def allowed_file(filename, allowed_extensions=None):
    """Check if file extension is allowed"""
    if allowed_extensions is None:
        from config import ALLOWED_EXTENSIONS
        allowed_extensions = ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def extract_text_from_pdf(file_content):
    """Extract text from PDF file"""
    if not PDF_AVAILABLE:
        raise ImportError("PyPDF2 is not installed. Please install it to process PDF files.")
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting PDF: {e}")
        raise

def extract_text_from_docx(file_content):
    """Extract text from DOCX file"""
    if not DOCX_AVAILABLE:
        raise ImportError("python-docx is not installed. Please install it to process DOCX files.")
    try:
        docx_file = io.BytesIO(file_content)
        doc = Document(docx_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        logger.error(f"Error extracting DOCX: {e}")
        raise

def extract_text_from_txt(file_content):
    """Extract text from TXT file"""
    try:
        # Try UTF-8 first, then fallback to other encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                return file_content.decode(encoding)
            except UnicodeDecodeError:
                continue
        raise ValueError("Could not decode text file")
    except Exception as e:
        logger.error(f"Error extracting TXT: {e}")
        raise

def extract_text_from_file(file_content, file_extension):
    """
    Extract text from file based on extension
    
    Args:
        file_content: Binary file content
        file_extension: File extension (pdf, docx, txt, etc.)
        
    Returns:
        str: Extracted text
    """
    ext = file_extension.lower()
    
    if ext == 'pdf':
        return extract_text_from_pdf(file_content)
    elif ext in ['docx', 'doc']:
        return extract_text_from_docx(file_content)
    elif ext == 'txt':
        return extract_text_from_txt(file_content)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

