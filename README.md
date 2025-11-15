# Student Support Chatbot (University Assistant)

Một chatbot AI thông minh được xây dựng để hỗ trợ sinh viên với các thông tin về trường đại học, sử dụng OpenAI API, RAG (Retrieval-Augmented Generation), và ChromaDB.

## 🚀 Tính năng

### Core Features
- **Thông tin môn học**: Tìm kiếm thông tin chi tiết về các môn học, giảng viên, lịch học
- **Lịch thi**: Xem lịch thi giữa kỳ, cuối kỳ cho các môn học
- **Tính học phí**: Tính toán học phí và các khoản phí dựa trên số tín chỉ
- **Dịch vụ sinh viên**: Thông tin về thư viện, hỗ trợ học tập
- **Multi-turn conversation**: Duy trì ngữ cảnh cuộc trò chuyện
- **Function calling**: Sử dụng OpenAI function calling để truy xuất dữ liệu động

### Advanced Features
- **RAG (Retrieval-Augmented Generation)**: Tự động retrieve context từ knowledge base để trả lời chính xác hơn
- **FAQ Matching**: Semantic search trong ChromaDB để tìm câu trả lời nhanh
- **Knowledge Base Management**: Upload và quản lý documents (PDF, DOCX, TXT) làm knowledge base
- **Conversation Logging**: Lưu trữ và phân tích lịch sử conversation

## 🛠️ Công nghệ sử dụng

### Backend
- **Python Flask**: Web framework
- **OpenAI API**: GPT-4o-mini với function calling
- **ChromaDB**: Vector database cho semantic search và RAG
- **Sentence Transformers**: Embeddings cho vector search

### Frontend
- **Next.js 14**: React framework với App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client
- **Lucide React**: Icon library

## 📁 Cấu trúc project

```
UniversityAssistant/
├── backend/
│   ├── app.py                    # Main Flask application (67 dòng)
│   ├── config.py                 # Configuration và constants
│   ├── chroma_manager.py         # ChromaDB manager với RAG support
│   ├── conversation_logger.py    # Conversation logging service
│   ├── data_loader.py            # Module load dữ liệu từ JSON files
│   ├── requirements.txt           # Python dependencies
│   ├── env_example.txt            # Environment variables example
│   ├── test_upload_api.py         # Test script cho knowledge base APIs
│   ├── routes/                    # API routes (modular)
│   │   ├── chat.py               # Chat endpoint với RAG
│   │   ├── knowledge.py          # Knowledge base CRUD
│   │   └── health.py             # Health check endpoint
│   ├── utils/                     # Utility modules
│   │   ├── file_processor.py     # File processing (PDF, DOCX, TXT)
│   │   ├── openai_functions.py  # OpenAI function definitions
│   │   └── rag_utils.py          # RAG utilities
│   ├── data/                      # Mock data files
│   │   ├── courses.json
│   │   ├── exams.json
│   │   ├── services.json
│   │   └── tuition.json
│   ├── chroma_db/                 # ChromaDB storage
│   └── conversation_logs/         # Conversation logs
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── components/        # React components
│   │       │   ├── Header.tsx
│   │       │   ├── ChatInput.tsx
│   │       │   ├── MessageList.tsx
│   │       │   ├── MessageBubble.tsx
│   │       │   ├── QuickActions.tsx
│   │       │   └── KnowledgeBaseManager.tsx
│   │       ├── hooks/             # Custom hooks
│   │       │   └── useChat.ts
│   │       ├── types/             # TypeScript types
│   │       │   └── index.ts
│   │       ├── constants/         # Constants
│   │       │   └── index.ts
│   │       ├── page.tsx           # Main chat interface
│   │       ├── layout.tsx         # Root layout
│   │       └── globals.css        # Global styles
│   ├── package.json
│   ├── tailwind.config.js
│   └── tsconfig.json
└── README.md
```

## 🚀 Cài đặt và chạy

### 🔧 Khởi động thủ công

#### 1. Backend Setup

```bash
cd backend

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt

# Tạo file .env từ env_example.txt
cp env_example.txt .env
# Chỉnh sửa .env và thêm OPENAI_API_KEY của bạn
```

**Lưu ý**: ChromaDB sẽ tự động tạo thư mục `chroma_db/` khi chạy lần đầu.

```bash
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

### Configuration

Các cấu hình có thể chỉnh sửa trong `backend/config.py`:

- **RAG Configuration**: `RAG_TOP_K`, `RAG_RELEVANCE_THRESHOLD`
- **FAQ Configuration**: `FAQ_TOP_K`, `FAQ_SIMILARITY_THRESHOLD`, `FAQ_CONFIDENCE_THRESHOLD`
- **File Upload**: `ALLOWED_EXTENSIONS`, `MAX_FILE_SIZE`

## 📡 API Endpoints

### Chat API
- **`POST /api/chat`** - Gửi tin nhắn đến chatbot
  ```json
  {
    "message": "Cho tôi biết thông tin về môn CS101",
    "session_id": "session_123"
  }
  ```
  Response:
  ```json
  {
    "response": "...",
    "source": "rag|faq|openai|function",
    "session_id": "session_123",
    "timestamp": "2024-01-01T00:00:00"
  }
  ```

### Knowledge Base API
- **`POST /api/knowledge/upload-file`** - Upload file (PDF, DOCX, TXT)
  - Form-data: `file`, `title` (optional), `category` (optional)
  
- **`POST /api/knowledge/upload-text`** - Upload text trực tiếp
  ```json
  {
    "title": "Quy định học tập",
    "content": "...",
    "category": "regulations"
  }
  ```

- **`GET /api/knowledge/documents`** - Lấy danh sách documents

- **`DELETE /api/knowledge/documents/<title>`** - Xóa document

### Health Check
- **`GET /api/health`** - Health check với service status

## 🎯 RAG (Retrieval-Augmented Generation) Flow

Hệ thống sử dụng RAG để cải thiện độ chính xác của câu trả lời:

1. **User Query** → User hỏi câu hỏi
2. **FAQ Matching** → Tìm trong FAQ collection (nếu confidence ≥ 0.8 → return ngay)
3. **RAG Retrieve** → Tìm kiếm trong knowledge base với semantic search
4. **Augment Prompt** → Thêm retrieved context vào system prompt
5. **LLM Generate** → OpenAI generate response dựa trên context
6. **Return Response** → Trả về response với source tracking

## 🎯 Function Calling

Chatbot sử dụng 5 function chính:

1. **get_course_info**: Tìm kiếm thông tin môn học
2. **get_exam_schedule**: Lấy lịch thi
3. **calculate_tuition**: Tính học phí
4. **get_student_services**: Thông tin dịch vụ sinh viên
5. **get_all_courses**: Lấy danh sách tất cả môn học

## 📊 Knowledge Base Management

### Upload Documents

#### Qua UI (Frontend):
1. Click button "Knowledge Base" ở header
2. Chọn "Upload File" hoặc "Nhập Text"
3. Điền thông tin và upload

#### Qua API:
```bash
# Upload file
curl -X POST http://localhost:5001/api/knowledge/upload-file \
  -F "file=@document.pdf" \
  -F "title=Quy định học tập" \
  -F "category=regulations"

# Upload text
curl -X POST http://localhost:5001/api/knowledge/upload-text \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Thông tin CS101",
    "content": "Môn CS101 học ở phòng A101...",
    "category": "courses"
  }'
```

### Document Processing

- **Automatic Chunking**: Documents dài được tự động chia thành chunks (1000 ký tự, overlap 200)
- **Embedding**: ChromaDB tự động tạo embeddings cho semantic search
- **Metadata**: Lưu title, category, created_at cho mỗi document

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
   - "Thông tin về thư viện"
   - "Hỗ trợ học tập ở đâu?"

### 🎯 Quick Actions

Sử dụng các nút hành động nhanh để:
- 📚 Xem thông tin môn học
- 📅 Kiểm tra lịch thi
- 💰 Tính học phí
- 🆘 Tìm dịch vụ hỗ trợ

### 📚 Knowledge Base

1. **Upload Documents**: Thêm tài liệu (PDF, DOCX, TXT) vào knowledge base
2. **RAG Search**: Bot tự động tìm kiếm trong knowledge base khi trả lời
3. **Manage Documents**: Xem và xóa documents qua UI

## 🧪 Testing

### Test Chat API
```bash
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Cho tôi biết thông tin về môn CS101",
    "session_id": "test_session"
  }'
```

### Test Knowledge Base Upload
```bash
# Sử dụng test script
cd backend
python test_upload_api.py
```

## ⚠️ Troubleshooting

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
   - Kiểm tra base_url trong config.py

3. **"Module not found"**
   - Chạy `pip install -r requirements.txt` trong backend
   - Chạy `npm install` trong frontend
   - Đảm bảo virtual environment được activate

4. **"ChromaDB not initialized"**
   - Kiểm tra quyền ghi trong thư mục backend
   - ChromaDB sẽ tự động tạo thư mục `chroma_db/` khi chạy

5. **"File upload failed"**
   - Kiểm tra file size (tối đa 10MB)
   - Đảm bảo file format được hỗ trợ (PDF, DOCX, TXT)
   - Cài đặt PyPDF2 và python-docx: `pip install PyPDF2 python-docx`

6. **Frontend không load**
   - Kiểm tra Node.js version (>= 16)
   - Xóa node_modules và chạy lại `npm install`
   - Kiểm tra backend đang chạy tại port 5001

## 📦 Dependencies

### Backend
- Flask 3.1.2
- OpenAI 2.3.0
- ChromaDB 0.4.18
- Sentence Transformers (cho embeddings)
- PyPDF2, python-docx (cho file processing)

### Frontend
- Next.js 14
- React 18
- TypeScript 5
- Tailwind CSS 3.4
- Axios 1.7.2

## 🏗️ Architecture

### Backend Architecture
- **Modular Design**: Routes, utils, config tách biệt
- **RAG Pipeline**: Retrieve → Augment → Generate
- **Vector Search**: ChromaDB với semantic search
- **Function Calling**: OpenAI functions cho structured data

### Frontend Architecture
- **Component-based**: Tách thành các components nhỏ
- **Custom Hooks**: useChat cho chat logic
- **Type Safety**: TypeScript với interfaces
- **State Management**: React hooks

## 📝 Notes

- ChromaDB data được lưu trong `backend/chroma_db/`
- Conversation logs được lưu trong `backend/conversation_logs/`
- Knowledge base documents được tự động chunking nếu quá dài
- RAG chỉ hoạt động khi có documents trong knowledge base

---

**Version**: 2.0.0  
**Last Updated**: 2024


📄 quy_dinh_hoc_tap.txt        → Category: regulations
📄 thong_tin_hoc_bong.txt      → Category: tuition  
📄 hoat_dong_ngoai_khoa.txt    → Category: services
📄 ky_tuc_xa.txt               → Category: services
📄 quy_trinh_dang_ky_mon_hoc.txt → Category: regulations

📂 Knowledge Base
├── 📁 regulations (2 documents)
│   ├── quy_dinh_hoc_tap.txt
│   └── quy_trinh_dang_ky_mon_hoc.txt
├── 📁 services (2 documents) 
│   ├── ky_tuc_xa.txt
│   └── hoat_dong_ngoai_khoa.txt
└── 📁 tuition (1 document)
    └── thong_tin_hoc_bong.txt