"""
Conversation Logger for University Assistant
Handles logging, analytics, and conversation history management
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Setup logging
logger = logging.getLogger(__name__)

class ConversationLogger:
    """
    Manages conversation logging, analytics and demo data generation
    """
    
    def __init__(self, log_dir: str = "./conversation_logs"):
        """
        Initialize conversation logger
        
        Args:
            log_dir (str): Directory to store conversation logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.log_dir / "sessions").mkdir(exist_ok=True)
        (self.log_dir / "analytics").mkdir(exist_ok=True)
        (self.log_dir / "demos").mkdir(exist_ok=True)
        
        logger.info(f"Conversation logger initialized at: {self.log_dir}")
    
    def log_conversation(self, session_id: str, messages: List[Dict[str, Any]], 
                        metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Log toàn bộ conversation của một session
        
        Args:
            session_id (str): ID của session
            messages (List[Dict]): Danh sách messages trong conversation
            metadata (Optional[Dict]): Thông tin metadata thêm
            
        Returns:
            bool: True nếu log thành công
        """
        try:
            # Tạo conversation data
            conversation_data = {
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "messages": messages,
                "stats": self._calculate_conversation_stats(messages),
                "metadata": metadata or {}
            }
            
            # Lưu file log theo session
            log_file = self.log_dir / "sessions" / f"{session_id}.json"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Logged conversation for session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging conversation: {e}")
            return False
    
    def log_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """
        Log một message đơn lẻ và append vào file session
        
        Args:
            session_id (str): ID của session
            message (Dict): Message data
            
        Returns:
            bool: True nếu log thành công
        """
        try:
            log_file = self.log_dir / "sessions" / f"{session_id}.json"
            
            # Load existing conversation hoặc tạo mới
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    conversation_data = json.load(f)
            else:
                conversation_data = {
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "messages": [],
                    "stats": {},
                    "metadata": {}
                }
            
            # Thêm message mới
            conversation_data["messages"].append({
                **message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Cập nhật stats
            conversation_data["stats"] = self._calculate_conversation_stats(
                conversation_data["messages"]
            )
            conversation_data["last_updated"] = datetime.now().isoformat()
            
            # Lưu lại file
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"Error logging message: {e}")
            return False
    
    def _calculate_conversation_stats(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Tính toán thống kê cho conversation
        
        Args:
            messages (List[Dict]): Danh sách messages
            
        Returns:
            Dict: Conversation statistics
        """
        try:
            stats = {
                "total_messages": len(messages),
                "user_messages": 0,
                "bot_messages": 0,
                "avg_response_length": 0,
                "response_sources": {"faq": 0, "openai": 0, "function": 0},
                "message_types": {},
                "duration_minutes": 0
            }
            
            bot_response_lengths = []
            timestamps = []
            
            for msg in messages:
                role = msg.get("role", msg.get("sender", ""))
                
                if role in ["user"]:
                    stats["user_messages"] += 1
                elif role in ["assistant", "bot"]:
                    stats["bot_messages"] += 1
                    
                    # Track response length
                    content = msg.get("content", "")
                    if content:
                        bot_response_lengths.append(len(content))
                    
                    # Track response source
                    source = msg.get("source", "openai")
                    if source in stats["response_sources"]:
                        stats["response_sources"][source] += 1
                
                # Track message types
                msg_type = msg.get("type", "text")
                stats["message_types"][msg_type] = stats["message_types"].get(msg_type, 0) + 1
                
                # Collect timestamps
                timestamp_str = msg.get("timestamp", "")
                if timestamp_str:
                    try:
                        timestamps.append(datetime.fromisoformat(timestamp_str.replace('Z', '+00:00')))
                    except:
                        pass
            
            # Calculate averages
            if bot_response_lengths:
                stats["avg_response_length"] = sum(bot_response_lengths) / len(bot_response_lengths)
            
            # Calculate conversation duration
            if len(timestamps) >= 2:
                duration = timestamps[-1] - timestamps[0]
                stats["duration_minutes"] = duration.total_seconds() / 60
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating conversation stats: {e}")
            return {"error": str(e)}
    
    def get_session_analytics(self, days: int = 7) -> Dict[str, Any]:
        """
        Lấy analytics cho tất cả sessions trong khoảng thời gian
        
        Args:
            days (int): Số ngày để phân tích (từ hôm nay trở về trước)
            
        Returns:
            Dict: Analytics data
        """
        try:
            sessions_dir = self.log_dir / "sessions"
            cutoff_date = datetime.now() - timedelta(days=days)
            
            analytics = {
                "period_days": days,
                "total_sessions": 0,
                "total_messages": 0,
                "total_users": 0,
                "avg_messages_per_session": 0,
                "response_sources": {"faq": 0, "openai": 0, "function": 0},
                "common_categories": {},
                "user_engagement": {
                    "short_sessions": 0,  # <= 3 messages
                    "medium_sessions": 0, # 4-10 messages
                    "long_sessions": 0    # > 10 messages
                },
                "peak_hours": {},
                "generated_at": datetime.now().isoformat()
            }
            
            session_files = list(sessions_dir.glob("*.json"))
            
            for session_file in session_files:
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    # Check if session is within time range
                    session_timestamp = datetime.fromisoformat(
                        session_data.get("timestamp", "").replace('Z', '+00:00')
                    )
                    
                    if session_timestamp < cutoff_date:
                        continue
                    
                    analytics["total_sessions"] += 1
                    
                    # Process session stats
                    stats = session_data.get("stats", {})
                    analytics["total_messages"] += stats.get("total_messages", 0)
                    
                    # Response sources
                    for source, count in stats.get("response_sources", {}).items():
                        analytics["response_sources"][source] += count
                    
                    # User engagement
                    msg_count = stats.get("total_messages", 0)
                    if msg_count <= 3:
                        analytics["user_engagement"]["short_sessions"] += 1
                    elif msg_count <= 10:
                        analytics["user_engagement"]["medium_sessions"] += 1
                    else:
                        analytics["user_engagement"]["long_sessions"] += 1
                    
                    # Peak hours analysis
                    for msg in session_data.get("messages", []):
                        timestamp_str = msg.get("timestamp", "")
                        if timestamp_str:
                            try:
                                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                hour = dt.hour
                                analytics["peak_hours"][hour] = analytics["peak_hours"].get(hour, 0) + 1
                            except:
                                pass
                
                except Exception as e:
                    logger.warning(f"Error processing session file {session_file}: {e}")
                    continue
            
            # Calculate averages
            if analytics["total_sessions"] > 0:
                analytics["avg_messages_per_session"] = analytics["total_messages"] / analytics["total_sessions"]
            
            analytics["total_users"] = analytics["total_sessions"]  # Assuming 1 session = 1 user for now
            
            # Save analytics
            analytics_file = self.log_dir / "analytics" / f"analytics_{datetime.now().strftime('%Y%m%d')}.json"
            with open(analytics_file, 'w', encoding='utf-8') as f:
                json.dump(analytics, f, ensure_ascii=False, indent=2)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating analytics: {e}")
            return {"error": str(e)}
    
    def create_demo_conversations(self) -> List[Dict[str, Any]]:
        """
        Tạo demo conversations để demonstrate multi-turn interaction
        
        Returns:
            List[Dict]: Danh sách demo conversations
        """
        try:
            demo_conversations = [
                {
                    "session_id": f"demo_session_1_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "title": "Tư vấn đăng ký môn học",
                    "messages": [
                        {
                            "role": "user",
                            "content": "Chào bạn! Tôi muốn đăng ký môn Computer Science cơ bản.",
                            "timestamp": datetime.now().isoformat()
                        },
                        {
                            "role": "assistant", 
                            "content": "Xin chào! Tôi có thể giúp bạn tìm hiểu về môn CS101 - Introduction to Computer Science. Đây là môn cơ bản với 3 tín chỉ, do Dr. Smith giảng dạy vào Thứ 2, Thứ 4, Thứ 6 lúc 9:00-10:30 tại phòng Lab A.",
                            "source": "openai",
                            "timestamp": datetime.now().isoformat()
                        },
                        {
                            "role": "user",
                            "content": "Môn này có điều kiện tiên quyết không?",
                            "timestamp": datetime.now().isoformat()
                        },
                        {
                            "role": "assistant",
                            "content": "Môn CS101 không yêu cầu điều kiện tiên quyết. Đây là môn dành cho sinh viên mới bắt đầu học lập trình. Bạn có muốn biết về lịch thi hoặc học phí không?",
                            "source": "function",
                            "timestamp": datetime.now().isoformat()
                        },
                        {
                            "role": "user", 
                            "content": "Vậy học phí cho 3 tín chỉ này bao nhiêu?",
                            "timestamp": datetime.now().isoformat()
                        },
                        {
                            "role": "assistant",
                            "content": "💰 Tính toán học phí:\n📚 Số tín chỉ: 3\n🎓 Loại sinh viên: Undergraduate\n💵 Học phí cơ bản: 4,500,000 VND\n💵 Phí đăng ký: 200,000 VND\n💵 Phí thư viện: 100,000 VND\n💵 Phí công nghệ: 150,000 VND\n💵 TỔNG CỘNG: 4,950,000 VND",
                            "source": "function",
                            "timestamp": datetime.now().isoformat()
                        }
                    ]
                },
                {
                    "session_id": f"demo_session_2_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "title": "Hỗ trợ dịch vụ thư viện",
                    "messages": [
                        {
                            "role": "user",
                            "content": "Thư viện mở cửa mấy giờ?",
                            "timestamp": datetime.now().isoformat()
                        },
                        {
                            "role": "assistant",
                            "content": "Thư viện mở cửa từ Thứ 2-Chủ Nhật: 7:00-22:00. Bạn có thể sử dụng dịch vụ học tập 24/7 tại khu vực tự học.",
                            "source": "faq",
                            "timestamp": datetime.now().isoformat()
                        },
                        {
                            "role": "user",
                            "content": "Tôi cần mượn sách về AI và Machine Learning",
                            "timestamp": datetime.now().isoformat()
                        },
                        {
                            "role": "assistant",
                            "content": "🏢 Dịch vụ sinh viên:\n\n🔹 Thư viện\n📝 Mô tả: Dịch vụ mượn sách, nghiên cứu, và học tập\n📍 Địa điểm: Tầng 1-3, Tòa A\n⏰ Giờ làm việc: Thứ 2-Chủ Nhật: 7:00-22:00\n📧 Liên hệ: library@university.edu.vn\n\nBạn có thể tìm sách AI/ML ở khu vực Computer Science tầng 2, hoặc liên hệ thủ thư để được hỗ trợ tìm kiếm cụ thể.",
                            "source": "function",
                            "timestamp": datetime.now().isoformat()
                        }
                    ]
                },
                {
                    "session_id": f"demo_session_3_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "title": "Kiểm tra lịch thi",
                    "messages": [
                        {
                            "role": "user",
                            "content": "Khi nào thi cuối kỳ môn Data Structures?",
                            "timestamp": datetime.now().isoformat()
                        },
                        {
                            "role": "assistant",
                            "content": "📅 Lịch thi:\n\n📚 Môn: CS201\n📝 Loại thi: Final Exam\n📅 Ngày: 2024-05-25\n⏰ Giờ: 14:00\n🏫 Phòng: Exam Room 1\n⏱️ Thời gian: 120 phút\n\nBạn nhớ đến sớm 15 phút để làm thủ tục nhé!",
                            "source": "function",
                            "timestamp": datetime.now().isoformat()
                        },
                        {
                            "role": "user",
                            "content": "Còn thi giữa kỳ nữa không?",
                            "timestamp": datetime.now().isoformat()
                        },
                        {
                            "role": "assistant",
                            "content": "📅 Lịch thi:\n\n📚 Môn: CS201\n📝 Loại thi: Midterm Exam\n📅 Ngày: 2024-04-15\n⏰ Giờ: 09:00\n🏫 Phòng: Room 301\n⏱️ Thời gian: 90 phút\n\nThi giữa kỳ đã qua rồi. Bạn có thể tập trung chuẩn bị cho kỳ thi cuối kỳ vào 25/5 nhé!",
                            "source": "function", 
                            "timestamp": datetime.now().isoformat()
                        }
                    ]
                }
            ]
            
            # Lưu demo conversations
            demos_dir = self.log_dir / "demos"
            demo_index = {
                "created_at": datetime.now().isoformat(),
                "total_demos": len(demo_conversations),
                "demos": []
            }
            
            for i, demo in enumerate(demo_conversations, 1):
                # Tính stats cho demo
                demo["stats"] = self._calculate_conversation_stats(demo["messages"])
                
                # Lưu file demo
                demo_file = demos_dir / f"demo_{i}_{datetime.now().strftime('%Y%m%d')}.json"
                with open(demo_file, 'w', encoding='utf-8') as f:
                    json.dump(demo, f, ensure_ascii=False, indent=2)
                
                demo_index["demos"].append({
                    "id": i,
                    "title": demo["title"],
                    "session_id": demo["session_id"],
                    "file": demo_file.name,
                    "message_count": len(demo["messages"])
                })
            
            # Lưu demo index
            index_file = demos_dir / f"demo_index_{datetime.now().strftime('%Y%m%d')}.json"
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(demo_index, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Created {len(demo_conversations)} demo conversations")
            return demo_conversations
            
        except Exception as e:
            logger.error(f"Error creating demo conversations: {e}")
            return []
    
    def export_all_logs(self, output_file: Optional[str] = None) -> str:
        """
        Export tất cả logs để backup hoặc analysis
        
        Args:
            output_file (Optional[str]): Tên file output, nếu None sẽ auto generate
            
        Returns:
            str: Path của file export
        """
        try:
            if not output_file:
                output_file = f"conversation_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            export_path = self.log_dir / output_file
            
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "sessions": [],
                "analytics": self.get_session_analytics(30),  # 30 days
                "total_files": 0
            }
            
            # Collect all session files
            sessions_dir = self.log_dir / "sessions"
            for session_file in sessions_dir.glob("*.json"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    export_data["sessions"].append(session_data)
                    export_data["total_files"] += 1
                except Exception as e:
                    logger.warning(f"Could not export session {session_file}: {e}")
            
            # Save export
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Exported {export_data['total_files']} sessions to {export_path}")
            return str(export_path)
            
        except Exception as e:
            logger.error(f"Error exporting logs: {e}")
            return ""

# Singleton instance
_conversation_logger = None

def get_conversation_logger() -> ConversationLogger:
    """Get singleton conversation logger instance"""
    global _conversation_logger
    if _conversation_logger is None:
        _conversation_logger = ConversationLogger()
    return _conversation_logger
