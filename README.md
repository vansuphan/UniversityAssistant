# Student Support Chatbot (University Assistant)

Một chatbot AI thông minh được xây dựng để hỗ trợ sinh viên với các thông tin về trường đại học, sử dụng OpenAI API và function calling.

## 🚀 Tính năng

- **Thông tin môn học**: Tìm kiếm thông tin chi tiết về các môn học, giảng viên, lịch học
- **Lịch thi**: Xem lịch thi giữa kỳ, cuối kỳ cho các môn học
- **Tính học phí**: Tính toán học phí và các khoản phí dựa trên số tín chỉ
- **Dịch vụ sinh viên**: Thông tin về thư viện, hỗ trợ học tập
- **Multi-turn conversation**: Duy trì ngữ cảnh cuộc trò chuyện
- **Function calling**: Sử dụng OpenAI function calling để truy xuất dữ liệu động

## 🛠️ Công nghệ sử dụng

### Backend
- **Python Flask**: Web framework
- **OpenAI API**: GPT-4o-mini với function calling

### Frontend
- **Next.js 14**: React framework với App Router
- **Axios**: HTTP client

## 📁 Cấu trúc project

```
UniversityAssistant/
├── backend/
│   ├── app.py              # Flask backend với OpenAI integration
│   ├── data_loader.py      # Module load dữ liệu từ JSON files
│   ├── requirements.txt    # Python dependencies
│   ├── env_example.txt     # Environment variables example
│   └── data/               # Mock data files
│       ├── courses.json    # Thông tin môn học
│       ├── exams.json      # Lịch thi
│       ├── services.json   # Dịch vụ sinh viên
│       └── tuition.json    # Thông tin học phí
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx    # Main chat interface
│   │       ├── layout.tsx  # Root layout
│   │       └── globals.css # Global styles
│   ├── package.json        # Node.js dependencies
│   ├── tailwind.config.js  # Tailwind configuration
│   └── tsconfig.json       # TypeScript configuration
├── run.sh                  # Script khởi động tự động
├── start_backend.sh        # Script khởi động backend
├── test_chatbot.py         # Test suite cho chatbot
└── README.md
```

## 🚀 Cài đặt và chạy

### 🔧 Khởi động thủ công

#### 1. Backend Setup

```bash
cd backend

# Tạo virtual environment
python -m venv venv-app-2
source venv-app-2/bin/activate  # On Windows: venv-app-2\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt

# Tạo file .env từ env_example.txt
cp env_example.txt .env
# Chỉnh sửa .env và thêm OPENAI_API_KEY của bạn

# Chạy backend
python app.py
```

Backend sẽ chạy tại `http://localhost:5001`

#### 2. Frontend Setup

```bash
cd frontend

# Cài đặt dependencies
npm install

# Chạy development server
npm run dev
```

Frontend sẽ chạy tại `http://localhost:3000`

### 🎯 Lần đầu sử dụng

1. **Lấy OpenAI API Key:**
   - Truy cập [OpenAI Platform](https://platform.openai.com/api-keys)
   - Tạo API key mới
   - Copy API key

2. **Cấu hình Environment:**
   ```bash
   cd backend
   cp env_example.txt .env
   # Mở file .env và thay thế "your_openai_api_key_here" bằng API key thật
   ```

3. **Khởi động hệ thống:**
   ```bash
   ./run.sh
   ```

4. **Truy cập ứng dụng:**
   - Mở trình duyệt tại `http://localhost:3000`
   - Bắt đầu chat với chatbot!

## 🔧 Cấu hình

### Environment Variables

Tạo file `.env` trong thư mục `backend/` với nội dung:

```env
OPENAI_API_KEY=your_openai_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

**Lưu ý**: 
- Backend chạy trên port 5001
- Frontend kết nối đến `http://localhost:5001`

### API Endpoints

- `POST /api/chat` - Gửi tin nhắn đến chatbot
- `GET /api/health` - Health check endpoint

**Lưu ý**: Backend chạy trên port 5001, frontend kết nối đến `http://localhost:5001`

## 🧪 Test Cases

| Test ID | Scenario | Expected Behavior |
|---------|----------|-------------------|
| TC_01 | "Cho tôi biết thông tin môn CS101" | Trả về thông tin chi tiết môn học |
| TC_02 | "Tính học phí cho 15 tín chỉ đại học" | Gọi function tính học phí và trả về kết quả |
| TC_03 | "Khi nào thi cuối kỳ?" | Trả về lịch thi cuối kỳ |
| TC_04 | "Môn nào có giảng viên Dr. Nguyen?" | Tìm kiếm môn học theo tên giảng viên |

## 🎯 Function Calling

Chatbot sử dụng 5 function chính:

1. **get_course_info**: Tìm kiếm thông tin môn học
2. **get_exam_schedule**: Lấy lịch thi
3. **calculate_tuition**: Tính học phí
4. **get_student_services**: Thông tin dịch vụ sinh viên
5. **get_all_courses**: Lấy danh sách tất cả môn học

## 📊 Mock Data

Hệ thống sử dụng mock data được lưu trữ trong các file JSON riêng biệt:

### 📁 Cấu trúc dữ liệu
- **`courses.json`**: Thông tin môn học (CS101, CS201, MATH101, ENG101)
- **`exams.json`**: Lịch thi giữa kỳ và cuối kỳ
- **`services.json`**: Dịch vụ sinh viên (Thư viện, Tư vấn nghề nghiệp, Tư vấn học tập)
- **`tuition.json`**: Thông tin học phí và các khoản phí

### 🔧 Data Loading
Dữ liệu được load tự động thông qua `data_loader.py` module khi khởi động backend.

## 📖 Hướng dẫn sử dụng

### 💬 Cách chat với bot

1. **Câu hỏi về môn học:**
   - "Cho tôi biết thông tin môn CS101"
   - "Môn Data Structures có mấy tín chỉ?"
   - "Giảng viên môn MATH101 là ai?"

2. **Tìm hiểu lịch thi:**
   - "Khi nào thi cuối kỳ môn CS201?"
   - "Lịch thi giữa kỳ"
   - "Thi môn nào vào ngày 20/5?"

3. **Tính học phí:**
   - "Tính học phí cho 15 tín chỉ đại học"
   - "Học phí 12 tín chỉ cao học bao nhiêu?"
   - "Tính tổng chi phí cho 18 tín chỉ"

4. **Dịch vụ sinh viên:**
   - "Tôi cần tư vấn nghề nghiệp"
   - "Thông tin về thư viện"
   - "Hỗ trợ học tập ở đâu?"

### 🎯 Quick Actions

Sử dụng các nút hành động nhanh để:
- 📚 Xem thông tin môn học
- 📅 Kiểm tra lịch thi
- 💰 Tính học phí
- 🆘 Tìm dịch vụ hỗ trợ

### 🔄 Multi-turn Conversation

Bot có thể nhớ ngữ cảnh cuộc trò chuyện:
```
Bạn: Cho tôi biết về môn CS101
Bot: [Thông tin môn CS101]
Bạn: Môn này có mấy tín chỉ?
Bot: [Trả lời dựa trên thông tin CS101 đã cung cấp]
```

### ⚠️ Troubleshooting

**Lỗi thường gặp:**

1. **"The api_key client option must be set"**
   ```bash
   # Kiểm tra file .env
   cd backend
   cat .env
   
   # Nếu chưa có, tạo từ template
   cp env_example.txt .env
   # Chỉnh sửa .env và thêm OPENAI_API_KEY thật
   ```

2. **"OpenAI API Error"**
   - Kiểm tra OPENAI_API_KEY trong file .env
   - Đảm bảo API key còn hiệu lực và có credit
   - Test API key: `python test_setup.py`

3. **"Module not found"**
   - Chạy `pip install -r requirements.txt` trong backend
   - Chạy `npm install` trong frontend
   - Đảm bảo virtual environment được activate

4. **Frontend không load**
   - Kiểm tra Node.js version (>= 16)
   - Xóa node_modules và chạy lại `npm install`

### 🔧 Quick Fix Commands

```bash
# Test setup
cd backend
source venv-app-2/bin/activate
python test_setup.py

# Start backend
./start_backend.sh

# Start frontend (terminal khác)
cd frontend
npm run dev
```
---
