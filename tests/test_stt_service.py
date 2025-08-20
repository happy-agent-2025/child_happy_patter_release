import pytest
from unittest.mock import patch, MagicMock
from services.stt_service import STTService


class TestSTTService:
    """测试STTService类"""
    
    def test_init(self):
        """测试STTService初始化"""
        with patch('services.stt_service.sr') as mock_sr:
            mock_recognizer = MagicMock()
            mock_sr.Recognizer.return_value = mock_recognizer
            
            service = STTService()
            assert service is not None
            assert service.recognizer == mock_recognizer
    
    def test_transcribe_audio_with_file(self):
        """测试使用音频文件转录"""
        with patch('services.stt_service.sr') as mock_sr:
            mock_recognizer = MagicMock()
            mock_sr.Recognizer.return_value = mock_recognizer
            mock_audio = MagicMock()
            mock_sr.AudioFile.return_value.__enter__.return_value = mock_audio
            
            # 模拟识别结果
            mock_recognizer.recognize_google.return_value = "测试文本"
            
            service = STTService()
            result = service.transcribe_audio("fake_audio_file.wav")
            
            assert result == "测试文本"
            mock_sr.AudioFile.assert_called_once_with("fake_audio_file.wav")
    
    def test_transcribe_audio_exception(self):
        """测试转录异常处理"""
        with patch('services.stt_service.sr') as mock_sr:
            mock_recognizer = MagicMock()
            mock_sr.Recognizer.return_value = mock_recognizer
            mock_sr.AudioFile.side_effect = Exception("音频文件错误")
            
            service = STTService()
            result = service.transcribe_audio("invalid_file.wav")
            
            assert "语音识别失败" in result