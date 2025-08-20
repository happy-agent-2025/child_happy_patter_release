import pytest
from unittest.mock import patch, MagicMock
from services.tts_service import TTSService
from io import BytesIO


class TestTTSService:
    """测试TTSService类"""
    
    def test_init(self):
        """测试TTSService初始化"""
        with patch('services.tts_service.pyttsx3') as mock_pyttsx3:
            mock_engine = MagicMock()
            mock_pyttsx3.init.return_value = mock_engine
            
            service = TTSService()
            assert service is not None
            assert service.engine == mock_engine
            mock_engine.setProperty.assert_any_call('rate', 150)
            mock_engine.setProperty.assert_any_call('volume', 0.9)
    
    def test_synthesize_speech(self):
        """测试语音合成"""
        with patch('services.tts_service.pyttsx3') as mock_pyttsx3:
            mock_engine = MagicMock()
            mock_pyttsx3.init.return_value = mock_engine
            
            service = TTSService()
            result = service.synthesize_speech("测试文本")
            
            assert isinstance(result, BytesIO)
            mock_engine.say.assert_called_once_with("测试文本")
            mock_engine.runAndWait.assert_called_once()
    
    def test_save_speech_to_file(self):
        """测试保存语音到文件"""
        with patch('services.tts_service.pyttsx3') as mock_pyttsx3:
            mock_engine = MagicMock()
            mock_pyttsx3.init.return_value = mock_engine
            
            service = TTSService()
            service.save_speech_to_file("测试文本", "output.mp3")
            
            mock_engine.save_to_file.assert_called_once_with("测试文本", "output.mp3")
            mock_engine.runAndWait.assert_called_once()