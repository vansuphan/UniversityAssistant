"""
Text-to-Speech Service using HuggingFace Transformers
Converts text responses to audio for better user experience
"""
import torch
import numpy as np
import io
import base64
import logging
import os
from typing import Optional
from pathlib import Path

# Setup logging
logger = logging.getLogger(__name__)

try:
    from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
    from datasets import load_dataset
    import soundfile as sf
    import numpy as np
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"TTS dependencies not available: {e}")
    TRANSFORMERS_AVAILABLE = False

class TTSService:
    """
    Text-to-Speech service using Microsoft SpeechT5 model
    Handles Vietnamese text and converts to audio
    """
    
    def __init__(self, cache_dir: str = "./models_cache"):
        """
        Initialize TTS Service
        
        Args:
            cache_dir (str): Directory to cache downloaded models
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.processor = None
        self.model = None
        self.vocoder = None
        self.speaker_embeddings = None
        self.is_initialized = False
        
        if not TRANSFORMERS_AVAILABLE:
            logger.error("TTS service cannot be initialized - missing dependencies")
            return
        
        try:
            self._initialize_models()
        except Exception as e:
            logger.error(f"Failed to initialize TTS models: {e}")
            self.is_initialized = False
    
    def _initialize_models(self):
        """Initialize TTS models và speaker embeddings"""
        try:
            logger.info("Loading TTS models... This may take a while on first run.")
            
            # Load processor và models
            model_name = "microsoft/speecht5_tts"
            vocoder_name = "microsoft/speecht5_hifigan"
            
            self.processor = SpeechT5Processor.from_pretrained(
                model_name, 
                cache_dir=self.cache_dir
            )
            
            self.model = SpeechT5ForTextToSpeech.from_pretrained(
                model_name,
                cache_dir=self.cache_dir
            )
            
            self.vocoder = SpeechT5HifiGan.from_pretrained(
                vocoder_name,
                cache_dir=self.cache_dir
            )
            
            # Load speaker embeddings for voice quality
            logger.info("Loading speaker embeddings...")
            try:
                embeddings_dataset = load_dataset(
                    "Matthijs/cmu-arctic-xvectors", 
                    split="validation",
                    cache_dir=self.cache_dir
                )
                # Sử dụng speaker embedding có chất lượng tốt (speaker 7306)
                self.speaker_embeddings = torch.tensor(
                    embeddings_dataset[7306]["xvector"]
                ).unsqueeze(0)
                
            except Exception as e:
                logger.warning(f"Could not load speaker embeddings: {e}")
                # Tạo default embedding nếu không load được
                self.speaker_embeddings = torch.randn(1, 512)
            
            self.is_initialized = True
            logger.info("TTS service initialized successfully!")
            
        except Exception as e:
            logger.error(f"Error initializing TTS models: {e}")
            self.is_initialized = False
            raise
    
    def text_to_speech(self, text: str, max_length: int = 500) -> Optional[str]:
        """
        Chuyển đổi text thành audio và trả về base64 encoded
        
        Args:
            text (str): Text cần chuyển đổi
            max_length (int): Độ dài tối đa của text
            
        Returns:
            Optional[str]: Base64 encoded audio data hoặc None nếu có lỗi
        """
        if not self.is_initialized:
            logger.warning("TTS service not initialized, cannot convert text to speech")
            return None
        
        if not text or not text.strip():
            logger.warning("Empty text provided to TTS")
            return None
        
        try:
            # Xử lý text để tối ưu cho TTS
            processed_text = self._preprocess_text(text, max_length)
            
            if not processed_text:
                logger.warning("Text became empty after preprocessing")
                return None
            
            logger.debug(f"Converting text to speech: {processed_text[:100]}...")
            
            # Tokenize text
            inputs = self.processor(text=processed_text, return_tensors="pt")
            
            # Generate speech
            with torch.no_grad():
                speech = self.model.generate_speech(
                    inputs["input_ids"],
                    self.speaker_embeddings,
                    vocoder=self.vocoder
                )
            
            # Convert tensor to numpy
            speech_np = speech.numpy()
            
            # Normalize audio để tránh clipping
            speech_np = self._normalize_audio(speech_np)
            
            # Convert to WAV format in memory
            audio_buffer = io.BytesIO()
            sf.write(
                audio_buffer, 
                speech_np, 
                samplerate=16000, 
                format='WAV',
                subtype='PCM_16'
            )
            audio_buffer.seek(0)
            
            # Encode as base64
            audio_base64 = base64.b64encode(audio_buffer.read()).decode('utf-8')
            
            logger.debug(f"Successfully converted text to speech (audio size: {len(audio_base64)} chars)")
            return audio_base64
            
        except Exception as e:
            logger.error(f"Error converting text to speech: {e}")
            return None
    
    def _preprocess_text(self, text: str, max_length: int) -> str:
        """
        Xử lý text trước khi chuyển đổi TTS
        
        Args:
            text (str): Text gốc
            max_length (int): Độ dài tối đa
            
        Returns:
            str: Text đã được xử lý
        """
        try:
            # Loại bỏ các ký tự đặc biệt có thể gây lỗi TTS
            import re
            
            # Loại bỏ emojis
            text = re.sub(r'[^\w\s\.,!?;:()\-áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴĐ]', ' ', text)
            
            # Loại bỏ ký tự markdown/formatting
            text = re.sub(r'[*_`#]', '', text)
            
            # Chuẩn hóa khoảng trắng
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Cắt ngắn text nếu quá dài
            if len(text) > max_length:
                # Cắt tại câu gần nhất
                sentences = text.split('.')
                result = ""
                for sentence in sentences:
                    if len(result + sentence + '.') <= max_length:
                        result += sentence + '.'
                    else:
                        break
                
                if result:
                    text = result.rstrip('.')
                else:
                    # Nếu không có câu nào vừa, cắt cứng
                    text = text[:max_length].rstrip()
            
            # Thêm dấu câu cuối nếu chưa có
            if text and not text[-1] in '.!?':
                text += '.'
            
            return text
            
        except Exception as e:
            logger.error(f"Error preprocessing text: {e}")
            return text[:max_length]  # Fallback to simple truncation
    
    def _normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Chuẩn hóa audio để tránh clipping và cải thiện chất lượng
        
        Args:
            audio_data (np.ndarray): Raw audio data
            
        Returns:
            np.ndarray: Normalized audio data
        """
        try:
            # Tìm giá trị max để normalize
            max_val = np.abs(audio_data).max()
            
            if max_val > 0:
                # Normalize về range [-0.9, 0.9] để tránh clipping
                audio_data = audio_data / max_val * 0.9
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Error normalizing audio: {e}")
            return audio_data
    
    def test_tts(self) -> bool:
        """
        Test TTS service với một câu đơn giản
        
        Returns:
            bool: True nếu TTS hoạt động bình thường
        """
        try:
            test_text = "Xin chào! Tôi là trợ lý ảo của trường đại học."
            result = self.text_to_speech(test_text)
            
            if result and len(result) > 1000:  # Base64 audio should be reasonably long
                logger.info("TTS test passed successfully")
                return True
            else:
                logger.error("TTS test failed - no audio generated")
                return False
                
        except Exception as e:
            logger.error(f"TTS test failed with error: {e}")
            return False
    
    def get_status(self) -> dict:
        """
        Lấy trạng thái hiện tại của TTS service
        
        Returns:
            dict: Thông tin status
        """
        return {
            "initialized": self.is_initialized,
            "dependencies_available": TRANSFORMERS_AVAILABLE,
            "models_loaded": all([
                self.processor is not None,
                self.model is not None, 
                self.vocoder is not None,
                self.speaker_embeddings is not None
            ]) if self.is_initialized else False,
            "cache_dir": str(self.cache_dir)
        }

# Singleton instance
_tts_service = None

def get_tts_service() -> TTSService:
    """Get singleton TTS service instance"""
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service

# Utility function for easy access
def text_to_speech(text: str) -> Optional[str]:
    """
    Convenience function to convert text to speech
    
    Args:
        text (str): Text to convert
        
    Returns:
        Optional[str]: Base64 encoded audio or None
    """
    service = get_tts_service()
    return service.text_to_speech(text)
