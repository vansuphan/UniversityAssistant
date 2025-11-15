"""
ChromaDB Manager for University Assistant
Handles semantic search, FAQ storage, and query logging
"""
import chromadb
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

# Setup logging
logger = logging.getLogger(__name__)

class ChromaDBManager:
    def __init__(self, persist_directory="./chroma_db"):
        """
        Initialize ChromaDB Manager
        
        Args:
            persist_directory (str): Directory to store ChromaDB data
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(path=str(self.persist_directory))
            logger.info(f"ChromaDB initialized at: {self.persist_directory}")
            
            # Create or get collections
            self.faq_collection = self.client.get_or_create_collection(
                name="faqs",
                metadata={"description": "Frequently asked questions"}
            )
            
            self.queries_collection = self.client.get_or_create_collection(
                name="user_queries", 
                metadata={"description": "User query logs with responses"}
            )
            
            self.knowledge_collection = self.client.get_or_create_collection(
                name="knowledge_base",
                metadata={"description": "University knowledge base"}
            )
            
            # Initialize with default FAQs
            self._initialize_default_faqs()
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise
    
    def _initialize_default_faqs(self):
        """Initialize với một số FAQs mặc định về trường đại học"""
        default_faqs = [
            {
                "question": "Học phí một tín chỉ đại học bao nhiêu?",
                "answer": "Học phí đại học là 1,500,000 VND/tín chỉ. Bạn có thể dùng tính năng tính học phí để biết tổng chi phí cho số tín chỉ mong muốn.",
                "category": "tuition"
            },
            {
                "question": "Làm thế nào để đăng ký môn học?",
                "answer": "Bạn có thể đăng ký môn học thông qua hệ thống online của trường hoặc liên hệ phòng đào tạo. Vui lòng kiểm tra lịch đăng ký để biết thời gian chính xác.",
                "category": "registration"
            },
            {
                "question": "Thư viện mở cửa vào giờ nào?",
                "answer": "Thư viện mở cửa từ Thứ 2-Chủ Nhật: 7:00-22:00. Bạn có thể sử dụng dịch vụ học tập 24/7 tại khu vực tự học.",
                "category": "services"
            },
            {
                "question": "Khi nào có lịch thi cuối kỳ?",
                "answer": "Lịch thi cuối kỳ thường được công bố 2 tuần trước kỳ thi. Bạn có thể kiểm tra lịch thi cụ thể cho từng môn học trong hệ thống.",
                "category": "exams"
            },
            {
                "question": "Tôi cần hỗ trợ tư vấn học tập ở đâu?",
                "answer": "Dịch vụ tư vấn học tập có tại Phòng 201, Tòa A. Thời gian: Thứ 2-Thứ 6: 8:00-17:00. Email: tuvan@university.edu.vn",
                "category": "services"
            }
        ]
        
        try:
            existing_count = self.faq_collection.count()
            if existing_count == 0:
                logger.info("Adding default FAQs to ChromaDB...")
                for faq in default_faqs:
                    self.add_faq(
                        question=faq["question"],
                        answer=faq["answer"], 
                        category=faq["category"]
                    )
                logger.info(f"Added {len(default_faqs)} default FAQs")
            else:
                logger.info(f"ChromaDB already has {existing_count} FAQs")
                
        except Exception as e:
            logger.error(f"Error initializing default FAQs: {e}")
    
    def add_faq(self, question: str, answer: str, category: str = "general") -> str:
        """
        Thêm FAQ vào ChromaDB
        
        Args:
            question (str): Câu hỏi FAQ
            answer (str): Câu trả lời
            category (str): Danh mục (tuition, registration, services, exams, etc.)
            
        Returns:
            str: ID của FAQ đã thêm
        """
        try:
            faq_id = str(uuid.uuid4())
            
            self.faq_collection.add(
                documents=[question],
                metadatas=[{
                    "answer": answer,
                    "category": category,
                    "created_at": datetime.now().isoformat()
                }],
                ids=[faq_id]
            )
            
            logger.info(f"Added FAQ: {question[:50]}... (Category: {category})")
            return faq_id
            
        except Exception as e:
            logger.error(f"Error adding FAQ: {e}")
            raise
    
    def search_similar_faqs(self, query: str, top_k: int = 3, similarity_threshold: float = 0.7) -> Dict[str, Any]:
        """
        Tìm FAQs tương tự dựa trên semantic search
        
        Args:
            query (str): Câu hỏi cần tìm
            top_k (int): Số lượng kết quả trả về
            similarity_threshold (float): Ngưỡng độ tương tự (0-1)
            
        Returns:
            Dict: Kết quả tìm kiếm với FAQs và độ tin cậy
        """
        try:
            results = self.faq_collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            # Xử lý kết quả và tính độ tin cậy
            formatted_results = {
                "found_matches": False,
                "faqs": [],
                "confidence_scores": []
            }
            
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0], 
                    results['distances'][0]
                )):
                    # Chuyển distance thành similarity score (ChromaDB trả về distance)
                    similarity = 1 - distance if distance <= 1 else 0
                    
                    if similarity >= similarity_threshold:
                        formatted_results["found_matches"] = True
                        formatted_results["faqs"].append({
                            "question": doc,
                            "answer": metadata["answer"],
                            "category": metadata["category"],
                            "similarity": similarity
                        })
                        formatted_results["confidence_scores"].append(similarity)
            
            logger.info(f"FAQ search for '{query}': {len(formatted_results['faqs'])} matches found")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching FAQs: {e}")
            return {"found_matches": False, "faqs": [], "confidence_scores": []}
    
    def log_user_query(self, query: str, response: str, session_id: str, source: str = "openai") -> str:
        """
        Log user query và response để phân tích sau này
        
        Args:
            query (str): Câu hỏi của user
            response (str): Câu trả lời của bot
            session_id (str): ID phiên chat
            source (str): Nguồn response (openai, faq, etc.)
            
        Returns:
            str: ID của log entry
        """
        try:
            log_id = str(uuid.uuid4())
            
            self.queries_collection.add(
                documents=[query],
                metadatas=[{
                    "response": response,
                    "session_id": session_id,
                    "source": source,
                    "timestamp": datetime.now().isoformat(),
                    "response_length": len(response)
                }],
                ids=[log_id]
            )
            
            logger.debug(f"Logged query: {query[:50]}... (Session: {session_id})")
            return log_id
            
        except Exception as e:
            logger.error(f"Error logging query: {e}")
            return ""
    
    def add_knowledge(self, title: str, content: str, category: str = "general") -> str:
        """
        Thêm thông tin vào knowledge base
        
        Args:
            title (str): Tiêu đề thông tin
            content (str): Nội dung chi tiết
            category (str): Danh mục
            
        Returns:
            str: ID của knowledge entry
        """
        try:
            knowledge_id = str(uuid.uuid4())
            
            # Combine title and content for better search
            searchable_text = f"{title}\n{content}"
            
            self.knowledge_collection.add(
                documents=[searchable_text],
                metadatas=[{
                    "title": title,
                    "content": content,
                    "category": category,
                    "created_at": datetime.now().isoformat()
                }],
                ids=[knowledge_id]
            )
            
            logger.info(f"Added knowledge: {title} (Category: {category})")
            return knowledge_id
            
        except Exception as e:
            logger.error(f"Error adding knowledge: {e}")
            raise
    
    def search_knowledge(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Tìm kiếm trong knowledge base
        
        Args:
            query (str): Truy vấn tìm kiếm
            top_k (int): Số lượng kết quả
            
        Returns:
            List[Dict]: Danh sách kết quả tìm kiếm
        """
        try:
            results = self.knowledge_collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            knowledge_items = []
            if results['documents'] and results['documents'][0]:
                for doc, metadata, distance in zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                ):
                    knowledge_items.append({
                        "title": metadata["title"],
                        "content": metadata["content"],
                        "category": metadata["category"],
                        "relevance": 1 - distance if distance <= 1 else 0
                    })
            
            return knowledge_items
            
        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            return []
    
    def get_analytics(self) -> Dict[str, Any]:
        """
        Lấy thống kê về database và usage
        
        Returns:
            Dict: Thông tin analytics
        """
        try:
            analytics = {
                "collections": {
                    "faqs": self.faq_collection.count(),
                    "queries": self.queries_collection.count(), 
                    "knowledge": self.knowledge_collection.count()
                },
                "storage_path": str(self.persist_directory),
                "last_updated": datetime.now().isoformat()
            }
            
            # Thống kê queries gần đây (nếu có)
            try:
                recent_queries = self.queries_collection.get(limit=10, include=['metadatas'])
                if recent_queries['metadatas']:
                    sources = [meta.get('source', 'unknown') for meta in recent_queries['metadatas']]
                    analytics['recent_query_sources'] = {
                        'openai': sources.count('openai'),
                        'faq': sources.count('faq'),
                        'other': len(sources) - sources.count('openai') - sources.count('faq')
                    }
            except:
                analytics['recent_query_sources'] = {}
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {"error": str(e)}
    
    def add_document_from_text(self, title: str, content: str, category: str = "general", chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """
        Thêm document từ text, tự động chunking nếu cần
        
        Args:
            title (str): Tiêu đề document
            content (str): Nội dung document
            category (str): Danh mục
            chunk_size (int): Kích thước mỗi chunk (số ký tự)
            chunk_overlap (int): Số ký tự overlap giữa các chunk
            
        Returns:
            List[str]: Danh sách IDs của các chunks đã thêm
        """
        try:
            # Chunking nếu content quá dài
            if len(content) > chunk_size:
                chunks = self._chunk_text(content, chunk_size, chunk_overlap)
                logger.info(f"Document '{title}' split into {len(chunks)} chunks")
            else:
                chunks = [content]
            
            chunk_ids = []
            for i, chunk in enumerate(chunks):
                chunk_id = str(uuid.uuid4())
                chunk_title = f"{title} (Part {i+1}/{len(chunks)})" if len(chunks) > 1 else title
                
                searchable_text = f"{chunk_title}\n{chunk}"
                
                self.knowledge_collection.add(
                    documents=[searchable_text],
                    metadatas=[{
                        "title": chunk_title,
                        "content": chunk,
                        "original_title": title,
                        "category": category,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "created_at": datetime.now().isoformat()
                    }],
                    ids=[chunk_id]
                )
                chunk_ids.append(chunk_id)
            
            logger.info(f"Added document '{title}' with {len(chunks)} chunks to knowledge base")
            return chunk_ids
            
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            raise
    
    def _chunk_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """
        Chia text thành các chunks với overlap
        
        Args:
            text (str): Text cần chia
            chunk_size (int): Kích thước mỗi chunk
            chunk_overlap (int): Số ký tự overlap
            
        Returns:
            List[str]: Danh sách chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            
            # Move start position with overlap
            start = end - chunk_overlap
            if start >= len(text):
                break
        
        return chunks

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        Lấy danh sách tất cả documents trong knowledge base
        
        Returns:
            List[Dict]: Danh sách documents với metadata
        """
        try:
            all_docs = self.knowledge_collection.get(include=['documents', 'metadatas'])
            
            documents = []
            seen_titles = {}
            
            if all_docs['documents'] and all_docs['metadatas']:
                for doc, metadata in zip(all_docs['documents'], all_docs['metadatas']):
                    original_title = metadata.get('original_title', metadata.get('title', 'Unknown'))
                    
                    # Group chunks by original title
                    if original_title not in seen_titles:
                        seen_titles[original_title] = {
                            "title": original_title,
                            "category": metadata.get("category", "general"),
                            "created_at": metadata.get("created_at", ""),
                            "chunks": 1
                        }
                    else:
                        seen_titles[original_title]["chunks"] += 1
            
            documents = list(seen_titles.values())
            return documents
            
        except Exception as e:
            logger.error(f"Error getting documents: {e}")
            return []

    def delete_document(self, title: str) -> bool:
        """
        Xóa document khỏi knowledge base (xóa tất cả chunks)
        
        Args:
            title (str): Tiêu đề document cần xóa
            
        Returns:
            bool: True nếu xóa thành công
        """
        try:
            # Get all documents with this title
            all_docs = self.knowledge_collection.get(include=['metadatas'])
            
            ids_to_delete = []
            if all_docs['metadatas'] and all_docs.get('ids'):
                for i, metadata in enumerate(all_docs['metadatas']):
                    original_title = metadata.get('original_title', metadata.get('title', ''))
                    if original_title == title:
                        ids_to_delete.append(all_docs['ids'][i])
            
            if ids_to_delete:
                self.knowledge_collection.delete(ids=ids_to_delete)
                logger.info(f"Deleted document '{title}' ({len(ids_to_delete)} chunks)")
                return True
            else:
                logger.warning(f"Document '{title}' not found")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False

    def export_faqs(self) -> List[Dict[str, Any]]:
        """
        Export tất cả FAQs để backup hoặc review
        
        Returns:
            List[Dict]: Danh sách tất cả FAQs
        """
        try:
            all_faqs = self.faq_collection.get(include=['documents', 'metadatas'])
            
            exported_faqs = []
            if all_faqs['documents'] and all_faqs['metadatas']:
                for doc, metadata in zip(all_faqs['documents'], all_faqs['metadatas']):
                    exported_faqs.append({
                        "question": doc,
                        "answer": metadata["answer"],
                        "category": metadata["category"],
                        "created_at": metadata.get("created_at", "")
                    })
            
            logger.info(f"Exported {len(exported_faqs)} FAQs")
            return exported_faqs
            
        except Exception as e:
            logger.error(f"Error exporting FAQs: {e}")
            return []

# Singleton instance
_chroma_manager = None

def get_chroma_manager() -> ChromaDBManager:
    """Get singleton ChromaDB manager instance"""
    global _chroma_manager
    if _chroma_manager is None:
        _chroma_manager = ChromaDBManager()
    return _chroma_manager
