"""
OpenAI function definitions and handlers
"""
from data_loader import COURSES_DATA, EXAM_SCHEDULE, STUDENT_SERVICES, TUITION_INFO

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
    """Format course results for display"""
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
    """Format exam results for display"""
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

# Function mapping for execution
FUNCTION_MAP = {
    "get_course_info": get_course_info,
    "get_exam_schedule": get_exam_schedule,
    "calculate_tuition": calculate_tuition,
    "get_student_services": get_student_services,
    "get_all_courses": get_all_courses
}

