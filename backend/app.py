from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import json
import os
from datetime import datetime
import logging
from dotenv import load_dotenv
from data_loader import COURSES_DATA, EXAM_SCHEDULE, STUDENT_SERVICES, TUITION_INFO

# Import new services
from chroma_manager import get_chroma_manager
from tts_service import get_tts_service
from conversation_logger import get_conversation_logger

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY", "sk-demo-key-for-testing")
if not api_key or api_key == "your_openai_api_key_here":
    print("⚠️  Warning: Using demo API key. Please set OPENAI_API_KEY in .env file for production use.")
    api_key = "sk-demo-key-for-testing"

client = openai.OpenAI(
    api_key=api_key,
    base_url="https://aiportalapi.stu-platform.live/jpe"
)

# Initialize enhanced services
logger.info("Initializing enhanced services...")
try:
    chroma_db = get_chroma_manager()
    tts_service = get_tts_service()
    conversation_logger = get_conversation_logger()
    logger.info("✅ All enhanced services initialized successfully!")
except Exception as e:
    logger.error(f"❌ Error initializing services: {e}")
    chroma_db = None
    tts_service = None
    conversation_logger = None

# Function definitions for OpenAI
def get_course_info(course_id=None, course_name=None, instructor=None):
    """Retrieve course information based on various criteria"""
    results = []
    for course in COURSES_DATA:
        if course_id and course_id.upper() in course["course_id"]:
            results.append(course)
        elif course_name and course_name.lower() in course["course_name"].lower():
            results.append(course)
        elif instructor and instructor.lower() in course["instructor"].lower():
            results.append(course)
    
    if not results:
        return "Không tìm thấy môn học phù hợp. Vui lòng kiểm tra lại thông tin."
    
    return format_course_results(results)

def format_course_results(courses):
    formatted = "📚 Thông tin môn học:\n\n"
    for course in courses:
        formatted += f"🔹 {course['course_id']}: {course['course_name']}\n"
        formatted += f"👨‍🏫 Giảng viên: {course['instructor']}\n"
        formatted += f"📅 Lịch học: {course['schedule']}\n"
        formatted += f"🏫 Phòng: {course['room']}\n"
        formatted += f"📖 Tín chỉ: {course['credits']}\n"
        formatted += f"📝 Mô tả: {course['description']}\n"
        if course['prerequisites']:
            formatted += f"⚠️ Điều kiện tiên quyết: {', '.join(course['prerequisites'])}\n"
        formatted += "\n"
    return formatted

def get_exam_schedule(course_id=None, exam_type=None, date_range=None):
    """Get exam schedule information"""
    results = []
    for exam in EXAM_SCHEDULE:
        if course_id and course_id.upper() in exam["course_id"]:
            results.append(exam)
        elif exam_type and exam_type.lower() in exam["exam_type"].lower():
            results.append(exam)
    
    if not results:
        return "Không tìm thấy lịch thi phù hợp."
    
    return format_exam_results(results)

def format_exam_results(exams):
    formatted = "📅 Lịch thi:\n\n"
    for exam in exams:
        formatted += f"📚 Môn: {exam['course_id']}\n"
        formatted += f"📝 Loại thi: {exam['exam_type']}\n"
        formatted += f"📅 Ngày: {exam['date']}\n"
        formatted += f"⏰ Giờ: {exam['time']}\n"
        formatted += f"🏫 Phòng: {exam['room']}\n"
        formatted += f"⏱️ Thời gian: {exam['duration']} phút\n\n"
    return formatted

def calculate_tuition(credit_hours, student_type="undergraduate", additional_fees=True):
    """Calculate tuition and fees for a student"""
    if student_type.lower() == "undergraduate":
        base_tuition = credit_hours * TUITION_INFO["undergraduate_credit_hour"]
    else:
        base_tuition = credit_hours * TUITION_INFO["graduate_credit_hour"]
    
    total = base_tuition
    
    if additional_fees:
        total += TUITION_INFO["registration_fee"]
        total += TUITION_INFO["library_fee"] 
        total += TUITION_INFO["technology_fee"]
    
    return f"""💰 Tính toán học phí:
📚 Số tín chỉ: {credit_hours}
🎓 Loại sinh viên: {student_type.title()}
💵 Học phí cơ bản: {base_tuition:,} VND
💵 Phí đăng ký: {TUITION_INFO['registration_fee']:,} VND
💵 Phí thư viện: {TUITION_INFO['library_fee']:,} VND  
💵 Phí công nghệ: {TUITION_INFO['technology_fee']:,} VND
💵 TỔNG CỘNG: {total:,} VND"""

def get_student_services(service_name=None):
    """Get information about student services"""
    results = []
    for service in STUDENT_SERVICES:
        if not service_name or service_name.lower() in service["service_name"].lower():
            results.append(service)
    
    if not results:
        return "Không tìm thấy dịch vụ phù hợp."
    
    formatted = "🏢 Dịch vụ sinh viên:\n\n"
    for service in results:
        formatted += f"🔹 {service['service_name']}\n"
        formatted += f"📝 Mô tả: {service['description']}\n"
        formatted += f"📍 Địa điểm: {service['location']}\n"
        formatted += f"⏰ Giờ làm việc: {service['hours']}\n"
        formatted += f"📧 Liên hệ: {service['contact']}\n\n"
    return formatted

def get_all_courses():
    """Get all available courses information"""
    if not COURSES_DATA:
        return "Không có thông tin môn học nào."
    
    formatted = f"📚 Danh sách tất cả môn học ({len(COURSES_DATA)} môn):\n\n"
    for course in COURSES_DATA:
        formatted += f"🔹 {course['course_id']}: {course['course_name']}\n"
        formatted += f"👨‍🏫 Giảng viên: {course['instructor']}\n"
        formatted += f"📅 Lịch học: {course['schedule']}\n"
        formatted += f"🏫 Phòng: {course['room']}\n"
        formatted += f"📖 Tín chỉ: {course['credits']}\n\n"
    return formatted

# OpenAI function definitions
FUNCTIONS = [
    {
        "name": "get_course_info",
        "description": "Get information about university courses",
        "parameters": {
            "type": "object",
            "properties": {
                "course_id": {"type": "string", "description": "Course ID (e.g., CS101)"},
                "course_name": {"type": "string", "description": "Course name"},
                "instructor": {"type": "string", "description": "Instructor name"}
            }
        }
    },
    {
        "name": "get_exam_schedule",
        "description": "Get exam schedule information",
        "parameters": {
            "type": "object",
            "properties": {
                "course_id": {"type": "string", "description": "Course ID"},
                "exam_type": {"type": "string", "description": "Type of exam (Midterm, Final)"},
                "date_range": {"type": "string", "description": "Date range for exams"}
            }
        }
    },
    {
        "name": "calculate_tuition",
        "description": "Calculate tuition and fees",
        "parameters": {
            "type": "object",
            "properties": {
                "credit_hours": {"type": "integer", "description": "Number of credit hours"},
                "student_type": {"type": "string", "description": "undergraduate or graduate"},
                "additional_fees": {"type": "boolean", "description": "Include additional fees"}
            },
            "required": ["credit_hours"]
        }
    },
    {
        "name": "get_student_services",
        "description": "Get information about student services",
        "parameters": {
            "type": "object",
            "properties": {
                "service_name": {"type": "string", "description": "Name of the service"}
            }
        }
    },
    {
        "name": "get_all_courses",
        "description": "Get all courses information",
        "parameters": {
            "type": "object",
            "properties": {
            }
        }
    }
]

# System prompt
SYSTEM_PROMPT = """Bạn là một trợ lý ảo thông minh của trường đại học, chuyên hỗ trợ sinh viên với các thông tin về:
- Thông tin môn học và lịch học
- Lịch thi và quy định thi cử  
- Học phí và các khoản phí
- Dịch vụ sinh viên (thư viện, tư vấn nghề nghiệp)
- Quy trình đăng ký môn học

Hãy trả lời một cách thân thiện, chính xác và hữu ích. Sử dụng emoji để làm cho câu trả lời sinh động hơn.
Nếu không chắc chắn về thông tin, hãy đề xuất sinh viên liên hệ trực tiếp với phòng ban liên quan.

Luôn trả lời bằng tiếng Việt trừ khi được yêu cầu khác."""

# Store conversation history (in production, use a proper database)
conversation_history = {}

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        include_audio = data.get('include_audio', False)
        
        logger.info(f"Processing chat request - Session: {session_id}, Audio: {include_audio}")
        
        # Initialize response variables
        assistant_message = ""
        audio_data = None
        response_source = "openai"
        
        # Step 1: Check ChromaDB for similar FAQs first (if available)
        if chroma_db:
            try:
                similar_faqs = chroma_db.search_similar_faqs(user_message, top_k=2, similarity_threshold=0.7)
                
                if similar_faqs["found_matches"] and len(similar_faqs["faqs"]) > 0:
                    best_faq = similar_faqs["faqs"][0]
                    confidence = best_faq["similarity"]
                    
                    logger.info(f"Found FAQ match with confidence: {confidence:.3f}")
                    
                    if confidence >= 0.8:  # High confidence threshold
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
                        
                        # Generate audio if requested
                        if include_audio and tts_service and tts_service.is_initialized:
                            try:
                                audio_data = tts_service.text_to_speech(assistant_message)
                                logger.debug("Generated TTS audio for FAQ response")
                            except Exception as tts_error:
                                logger.warning(f"TTS generation failed: {tts_error}")
                        
                        # Log to ChromaDB
                        chroma_db.log_user_query(user_message, assistant_message, session_id, "faq")
                        
                        return jsonify({
                            'response': assistant_message,
                            'audio': audio_data,
                            'source': response_source,
                            'confidence': confidence,
                            'session_id': session_id,
                            'timestamp': datetime.now().isoformat()
                        })
            
            except Exception as faq_error:
                logger.warning(f"FAQ search failed: {faq_error}")
        
        # Step 2: Proceed with OpenAI workflow if no FAQ match
        # Get or create conversation history
        if session_id not in conversation_history:
            conversation_history[session_id] = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
        
        # Add user message to history
        conversation_history[session_id].append({
            "role": "user", 
            "content": user_message
        })
        
        # Call OpenAI API (with error handling)
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=conversation_history[session_id],
                functions=FUNCTIONS,
                function_call="auto"
            )
        except Exception as api_error:
            logger.error(f"OpenAI API error: {str(api_error)}")
            # Fallback response for demo purposes
            fallback_message = f'Xin chào! Tôi là trợ lý ảo của trường đại học. Bạn đã gửi: "{user_message}". Hiện tại tôi đang trong chế độ demo. Vui lòng cấu hình API key để sử dụng đầy đủ tính năng.'
            
            # Still log the interaction
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
                'audio': None,
                'source': 'demo',
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })
        
        response_message = response.choices[0].message
        logger.debug(f'OpenAI response_message: {response_message}')
        
        # Handle function calls
        if hasattr(response_message, 'function_call') and response_message.function_call:
            function_name = response_message.function_call.name
            function_args = json.loads(response_message.function_call.arguments)
            
            logger.info(f"Executing function: {function_name} with args: {function_args}")
            
            # Call the appropriate function
            if function_name == "get_course_info":
                result = get_course_info(**function_args)
            elif function_name == "get_exam_schedule":
                result = get_exam_schedule(**function_args)
            elif function_name == "calculate_tuition":
                result = calculate_tuition(**function_args)
            elif function_name == "get_student_services":
                result = get_student_services(**function_args)
            elif function_name == "get_all_courses":
                result = get_all_courses(**function_args)
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
                model="gpt-4o-mini",
                messages=conversation_history[session_id]
            )
            
            assistant_message = final_response.choices[0].message.content
        else:
            assistant_message = response_message.content
            response_source = "openai"
        
        # Add assistant response to history
        conversation_history[session_id].append({
            "role": "assistant",
            "content": assistant_message
        })
        
        # Step 3: Generate audio if requested and TTS is available
        if include_audio and tts_service and tts_service.is_initialized:
            try:
                logger.info("Generating TTS audio...")
                audio_data = tts_service.text_to_speech(assistant_message)
                if audio_data:
                    logger.info("TTS audio generated successfully")
                else:
                    logger.warning("TTS audio generation returned empty result")
            except Exception as tts_error:
                logger.error(f"TTS generation failed: {tts_error}")
                audio_data = None
        
        # Step 4: Log conversation
        if conversation_logger:
            try:
                conversation_logger.log_message(session_id, {
                    "role": "user",
                    "content": user_message
                })
                conversation_logger.log_message(session_id, {
                    "role": "assistant",
                    "content": assistant_message,
                    "source": response_source,
                    "has_audio": audio_data is not None
                })
            except Exception as log_error:
                logger.warning(f"Conversation logging failed: {log_error}")
        
        # Step 5: Log to ChromaDB for future FAQ matching
        if chroma_db:
            try:
                chroma_db.log_user_query(user_message, assistant_message, session_id, response_source)
            except Exception as chroma_error:
                logger.warning(f"ChromaDB logging failed: {chroma_error}")
        
        return jsonify({
            'response': assistant_message,
            'audio': audio_data,
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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Enhanced health check with service status"""
    health_data = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Student Support Chatbot (Enhanced)',
        'services': {
            'chromadb': chroma_db is not None,
            'tts': tts_service is not None and tts_service.is_initialized if tts_service else False,
            'conversation_logger': conversation_logger is not None,
            'openai_api': api_key != "sk-demo-key-for-testing"
        }
    }
    
    # Add detailed service info if available
    if tts_service:
        health_data['tts_status'] = tts_service.get_status()
    
    if chroma_db:
        try:
            health_data['chromadb_analytics'] = chroma_db.get_analytics()
        except:
            health_data['chromadb_analytics'] = {"error": "Could not fetch analytics"}
    
    return jsonify(health_data)

# Admin endpoints for enhanced features
@app.route('/api/admin/faq', methods=['POST'])
def add_faq():
    """Admin endpoint để thêm FAQ mới"""
    try:
        if not chroma_db:
            return jsonify({'error': 'ChromaDB not available'}), 503
        
        data = request.get_json()
        question = data.get('question', '').strip()
        answer = data.get('answer', '').strip()
        category = data.get('category', 'general').strip()
        
        if not question or not answer:
            return jsonify({'error': 'Question and answer are required'}), 400
        
        faq_id = chroma_db.add_faq(question, answer, category)
        
        logger.info(f"Added new FAQ: {question[:50]}...")
        
        return jsonify({
            'status': 'success',
            'faq_id': faq_id,
            'message': 'FAQ đã được thêm thành công'
        })
        
    except Exception as e:
        logger.error(f"Error adding FAQ: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/faq', methods=['GET'])
def get_faqs():
    """Lấy danh sách tất cả FAQs"""
    try:
        if not chroma_db:
            return jsonify({'error': 'ChromaDB not available'}), 503
        
        faqs = chroma_db.export_faqs()
        
        return jsonify({
            'faqs': faqs,
            'total': len(faqs),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting FAQs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/analytics', methods=['GET'])
def get_analytics():
    """Lấy analytics và thống kê conversation"""
    try:
        analytics_data = {
            'timestamp': datetime.now().isoformat()
        }
        
        # ChromaDB analytics
        if chroma_db:
            analytics_data['chromadb'] = chroma_db.get_analytics()
        
        # Conversation analytics
        if conversation_logger:
            days = request.args.get('days', 7, type=int)
            analytics_data['conversations'] = conversation_logger.get_session_analytics(days)
        
        # TTS status
        if tts_service:
            analytics_data['tts'] = tts_service.get_status()
        
        return jsonify(analytics_data)
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/demo-conversations', methods=['POST'])
def create_demo_conversations():
    """Tạo demo conversations để demonstrate tính năng"""
    try:
        if not conversation_logger:
            return jsonify({'error': 'Conversation logger not available'}), 503
        
        demo_conversations = conversation_logger.create_demo_conversations()
        
        return jsonify({
            'status': 'success',
            'demos_created': len(demo_conversations),
            'message': f'Đã tạo {len(demo_conversations)} demo conversations',
            'demos': [
                {
                    'session_id': demo['session_id'],
                    'title': demo['title'],
                    'message_count': len(demo['messages'])
                }
                for demo in demo_conversations
            ]
        })
        
    except Exception as e:
        logger.error(f"Error creating demo conversations: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/test-tts', methods=['POST'])
def test_tts():
    """Test TTS service với custom text"""
    try:
        if not tts_service:
            return jsonify({'error': 'TTS service not available'}), 503
        
        data = request.get_json()
        test_text = data.get('text', 'Xin chào! Đây là test TTS service.')
        
        if not tts_service.is_initialized:
            return jsonify({'error': 'TTS service not initialized'}), 503
        
        audio_data = tts_service.text_to_speech(test_text)
        
        if audio_data:
            return jsonify({
                'status': 'success',
                'audio': audio_data,
                'message': 'TTS test thành công',
                'text_length': len(test_text),
                'audio_size': len(audio_data)
            })
        else:
            return jsonify({
                'status': 'failed',
                'error': 'Could not generate audio'
            }), 500
        
    except Exception as e:
        logger.error(f"Error testing TTS: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
