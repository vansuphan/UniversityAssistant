"""
Chat API routes
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import json
import logging

from utils.rag_utils import SYSTEM_PROMPT_BASE, retrieve_context_from_knowledge_base, augment_system_prompt
from utils.openai_functions import FUNCTIONS, FUNCTION_MAP
from config import (
    OPENAI_MODEL, RAG_TOP_K, RAG_RELEVANCE_THRESHOLD,
    FAQ_TOP_K, FAQ_SIMILARITY_THRESHOLD, FAQ_CONFIDENCE_THRESHOLD
)

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)

# Store conversation history (in production, use a proper database)
conversation_history = {}

def init_chat_routes(app, chroma_db, conversation_logger, openai_client):
    """
    Initialize chat routes with dependencies
    
    Args:
        app: Flask app instance
        chroma_db: ChromaDB manager instance
        conversation_logger: Conversation logger instance
        openai_client: OpenAI client instance
    """
    chat_bp.chroma_db = chroma_db
    chat_bp.conversation_logger = conversation_logger
    chat_bp.openai_client = openai_client
    
    app.register_blueprint(chat_bp, url_prefix='/api')

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        logger.info(f"Processing chat request - Session: {session_id}")
        
        # Get dependencies from blueprint
        chroma_db = chat_bp.chroma_db
        conversation_logger = chat_bp.conversation_logger
        client = chat_bp.openai_client
        
        # Initialize response variables
        assistant_message = ""
        response_source = "openai"
        rag_used = False
        
        # Step 1: Check ChromaDB for similar FAQs first
        if chroma_db:
            try:
                similar_faqs = chroma_db.search_similar_faqs(
                    user_message, 
                    top_k=FAQ_TOP_K, 
                    similarity_threshold=FAQ_SIMILARITY_THRESHOLD
                )
                
                if similar_faqs["found_matches"] and len(similar_faqs["faqs"]) > 0:
                    best_faq = similar_faqs["faqs"][0]
                    confidence = best_faq["similarity"]
                    
                    logger.info(f"Found FAQ match with confidence: {confidence:.3f}")
                    
                    if confidence >= FAQ_CONFIDENCE_THRESHOLD:
                        assistant_message = best_faq["answer"]
                        response_source = "faq"
                        
                        # Log the message exchange
                        if conversation_logger:
                            conversation_logger.log_message(session_id, {
                                "role": "user",
                                "content": user_message
                            })
                            conversation_logger.log_message(session_id, {
                                "role": "assistant", 
                                "content": assistant_message,
                                "source": response_source,
                                "faq_confidence": confidence
                            })
                        
                        # Log to ChromaDB
                        chroma_db.log_user_query(user_message, assistant_message, session_id, "faq")
                        
                        return jsonify({
                            'response': assistant_message,
                            'source': response_source,
                            'confidence': confidence,
                            'session_id': session_id,
                            'timestamp': datetime.now().isoformat()
                        })
            
            except Exception as faq_error:
                logger.warning(f"FAQ search failed: {faq_error}")
        
        # Step 2: RAG - Retrieve context from knowledge base
        retrieved_context = ""
        if chroma_db:
            try:
                retrieved_context = retrieve_context_from_knowledge_base(
                    chroma_db,
                    user_message, 
                    top_k=RAG_TOP_K, 
                    relevance_threshold=RAG_RELEVANCE_THRESHOLD
                )
                if retrieved_context:
                    rag_used = True
                    response_source = "rag"
                    logger.info("Retrieved context from knowledge base for RAG")
            except Exception as rag_error:
                logger.warning(f"RAG retrieval failed: {rag_error}")
        
        # Step 3: Proceed with OpenAI workflow
        # Get or create conversation history with augmented prompt
        if session_id not in conversation_history:
            augmented_prompt = augment_system_prompt(SYSTEM_PROMPT_BASE, retrieved_context)
            conversation_history[session_id] = [
                {"role": "system", "content": augmented_prompt}
            ]
        else:
            # Update system prompt with new context if available
            if retrieved_context:
                augmented_prompt = augment_system_prompt(SYSTEM_PROMPT_BASE, retrieved_context)
                conversation_history[session_id][0] = {"role": "system", "content": augmented_prompt}
        
        # Add user message to history
        conversation_history[session_id].append({
            "role": "user", 
            "content": user_message
        })
        
        # Call OpenAI API
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=conversation_history[session_id],
                functions=FUNCTIONS,
                function_call="auto"
            )
        except Exception as api_error:
            logger.error(f"OpenAI API error: {str(api_error)}")
            fallback_message = f'Xin chào! Tôi là trợ lý ảo của trường đại học. Bạn đã gửi: "{user_message}". Hiện tại tôi đang trong chế độ demo. Vui lòng cấu hình API key để sử dụng đầy đủ tính năng.'
            
            if conversation_logger:
                conversation_logger.log_message(session_id, {
                    "role": "user",
                    "content": user_message
                })
                conversation_logger.log_message(session_id, {
                    "role": "assistant",
                    "content": fallback_message,
                    "source": "demo"
                })
            
            return jsonify({
                'response': fallback_message,
                'source': 'demo',
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })
        
        response_message = response.choices[0].message
        
        # Handle function calls
        if hasattr(response_message, 'function_call') and response_message.function_call:
            function_name = response_message.function_call.name
            function_args = json.loads(response_message.function_call.arguments)
            
            logger.info(f"Executing function: {function_name} with args: {function_args}")
            
            # Call the appropriate function
            if function_name in FUNCTION_MAP:
                result = FUNCTION_MAP[function_name](**function_args)
            else:
                result = "Xin lỗi, tôi không thể xử lý yêu cầu này."
            
            response_source = "function"
            
            # Add function result to conversation
            conversation_history[session_id].append({
                "role": "function",
                "name": function_name,
                "content": str(result)
            })
            
            # Get final response from OpenAI
            final_response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=conversation_history[session_id]
            )
            
            assistant_message = final_response.choices[0].message.content
        else:
            assistant_message = response_message.content
            if not rag_used:
                response_source = "openai"
        
        # Add assistant response to history
        conversation_history[session_id].append({
            "role": "assistant",
            "content": assistant_message
        })
        
        # Log conversation
        if conversation_logger:
            try:
                conversation_logger.log_message(session_id, {
                    "role": "user",
                    "content": user_message
                })
                log_data = {
                    "role": "assistant",
                    "content": assistant_message,
                    "source": response_source
                }
                if rag_used:
                    log_data["rag_used"] = True
                conversation_logger.log_message(session_id, log_data)
            except Exception as log_error:
                logger.warning(f"Conversation logging failed: {log_error}")
        
        # Log to ChromaDB for future FAQ matching
        if chroma_db:
            try:
                chroma_db.log_user_query(user_message, assistant_message, session_id, response_source)
            except Exception as chroma_error:
                logger.warning(f"ChromaDB logging failed: {chroma_error}")
        
        return jsonify({
            'response': assistant_message,
            'source': response_source,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': 'Có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại.',
            'session_id': data.get('session_id', 'default') if 'data' in locals() else 'default'
        }), 500

