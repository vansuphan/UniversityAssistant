"""
Test script for knowledge base upload APIs
Run this after starting the Flask server
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_upload_text():
    """Test uploading text directly"""
    print("\n=== Testing Upload Text ===")
    url = f"{BASE_URL}/api/knowledge/upload-text"
    
    data = {
        "title": "Test Document - Quy định học tập",
        "content": """
        Quy định học tập tại trường đại học:
        1. Sinh viên phải tham gia đầy đủ các buổi học
        2. Điểm danh được thực hiện vào đầu mỗi buổi học
        3. Sinh viên vắng mặt quá 20% số buổi học sẽ không được thi cuối kỳ
        4. Thời gian học: 8:00 - 17:00 từ thứ 2 đến thứ 6
        """,
        "category": "regulations"
    }
    
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json()

def test_list_documents():
    """Test listing all documents"""
    print("\n=== Testing List Documents ===")
    url = f"{BASE_URL}/api/knowledge/documents"
    
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json()

def test_upload_file(file_path, title=None, category="general"):
    """Test uploading a file"""
    print(f"\n=== Testing Upload File: {file_path} ===")
    url = f"{BASE_URL}/api/knowledge/upload-file"
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {}
        if title:
            data['title'] = title
        data['category'] = category
        
        response = requests.post(url, files=files, data=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.json()

def test_delete_document(title):
    """Test deleting a document"""
    print(f"\n=== Testing Delete Document: {title} ===")
    from urllib.parse import quote
    url = f"{BASE_URL}/api/knowledge/documents/{quote(title)}"
    
    response = requests.delete(url)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json()

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Check ===")
    url = f"{BASE_URL}/api/health"
    
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json()

if __name__ == "__main__":
    print("🚀 Testing Knowledge Base Upload APIs")
    print("=" * 50)
    
    # Test health first
    try:
        test_health()
    except Exception as e:
        print(f"❌ Server not running or error: {e}")
        print("Please start the Flask server first: python app.py")
        exit(1)
    
    # Test upload text
    try:
        result = test_upload_text()
        if result.get('success'):
            print("✅ Upload text successful")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test list documents
    try:
        result = test_list_documents()
        if result.get('success'):
            print(f"✅ List documents successful - Found {result.get('total', 0)} documents")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test upload file (if you have a test file)
    # Uncomment and provide a file path:
    # try:
    #     test_upload_file("test_document.txt", title="Test File", category="test")
    # except Exception as e:
    #     print(f"❌ Error: {e}")
    
    # Test delete document (uncomment to test deletion)
    # try:
    #     test_delete_document("Test Document - Quy định học tập")
    # except Exception as e:
    #     print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")

