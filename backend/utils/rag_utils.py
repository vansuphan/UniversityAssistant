"""
RAG (Retrieval-Augmented Generation) utilities
"""
import logging

logger = logging.getLogger(__name__)

# System prompt base
SYSTEM_PROMPT_BASE = """Bạn là một trợ lý ảo thông minh của trường đại học, chuyên hỗ trợ sinh viên với các thông tin về:
- Thông tin môn học và lịch học
- Lịch thi và quy định thi cử  
- Học phí và các khoản phí
- Dịch vụ sinh viên (thư viện, tư vấn nghề nghiệp)
- Quy trình đăng ký môn học

Hãy trả lời một cách thân thiện, chính xác và hữu ích. Sử dụng emoji để làm cho câu trả lời sinh động hơn.
Nếu không chắc chắn về thông tin, hãy đề xuất sinh viên liên hệ trực tiếp với phòng ban liên quan.

Luôn trả lời bằng tiếng Việt trừ khi được yêu cầu khác."""

def retrieve_context_from_knowledge_base(chroma_db, query: str, top_k: int = 3, relevance_threshold: float = 0.7) -> str:
    """
    Retrieve relevant context from knowledge base using RAG
    
    Args:
        chroma_db: ChromaDB manager instance
        query (str): User query
        top_k (int): Number of documents to retrieve
        relevance_threshold (float): Minimum relevance score (0-1)
        
    Returns:
        str: Formatted context string for augmentation
    """
    if not chroma_db:
        return ""
    
    try:
        knowledge_results = chroma_db.search_knowledge(query, top_k=top_k)
        
        if not knowledge_results:
            return ""
        
        # Filter by relevance threshold and format context
        context_parts = []
        for item in knowledge_results:
            relevance = item.get('relevance', 0)
            if relevance >= relevance_threshold:
                title = item.get('title', 'Unknown')
                content = item.get('content', '')
                
                # Format context entry
                context_entry = f"📚 {title}\n{content}\n"
                context_parts.append(context_entry)
        
        if context_parts:
            formatted_context = "\n".join(context_parts)
            logger.info(f"Retrieved {len(context_parts)} relevant knowledge items for RAG")
            return formatted_context
        
        return ""
        
    except Exception as e:
        logger.warning(f"RAG retrieval failed: {e}")
        return ""

def augment_system_prompt(base_prompt: str, retrieved_context: str) -> str:
    """
    Augment system prompt with retrieved context from knowledge base
    
    Args:
        base_prompt (str): Base system prompt
        retrieved_context (str): Retrieved context from knowledge base
        
    Returns:
        str: Augmented system prompt
    """
    if not retrieved_context:
        return base_prompt
    
    augmented_prompt = f"""{base_prompt}

=== THÔNG TIN THAM KHẢO TỪ CƠ SỞ DỮ LIỆU ===
Dưới đây là thông tin liên quan từ cơ sở dữ liệu của trường đại học:

{retrieved_context}

HƯỚNG DẪN SỬ DỤNG THÔNG TIN:
- Hãy sử dụng thông tin trên để trả lời câu hỏi của sinh viên một cách chính xác
- Ưu tiên thông tin từ cơ sở dữ liệu trên thông tin chung chung
- Nếu thông tin không đủ, bạn có thể kết hợp với function calls để lấy thêm thông tin
- Luôn trích dẫn nguồn thông tin khi có thể
"""
    return augmented_prompt

