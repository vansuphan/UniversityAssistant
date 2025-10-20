"""
Data loader module for loading mock data from JSON files
"""
import json
import os
from typing import Dict, List, Any

def load_json_data(filename: str) -> Any:
    """
    Load data from a JSON file in the data directory
    
    Args:
        filename (str): Name of the JSON file (without .json extension)
        
    Returns:
        Any: Parsed JSON data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    # Get the directory where this script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, 'data')
    file_path = os.path.join(data_dir, f"{filename}.json")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def load_courses_data() -> List[Dict[str, Any]]:
    """Load courses data from courses.json"""
    return load_json_data('courses')

def load_exams_data() -> List[Dict[str, Any]]:
    """Load exam schedule data from exams.json"""
    return load_json_data('exams')

def load_services_data() -> List[Dict[str, Any]]:
    """Load student services data from services.json"""
    return load_json_data('services')

def load_tuition_data() -> Dict[str, Any]:
    """Load tuition information from tuition.json"""
    return load_json_data('tuition')

# Load all data at module level for easy access
try:
    COURSES_DATA = load_courses_data()
    EXAM_SCHEDULE = load_exams_data()
    STUDENT_SERVICES = load_services_data()
    TUITION_INFO = load_tuition_data()
except Exception as e:
    print(f"Error loading data: {e}")
    # Fallback empty data
    COURSES_DATA = []
    EXAM_SCHEDULE = []
    STUDENT_SERVICES = []
    TUITION_INFO = {}
