import pytest
from unittest.mock import patch, MagicMock
from services.stt_service import STTService
import numpy as np


class MockAudioData:
    """模拟AudioData对象"""
    def __init__(self, sample_rate, frame_data, sample_width):
        self.sample_rate = sample_rate
        self.frame_data = frame_data
        self.sample_width = sample_width


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
            assert hasattr(service, 'audio_processor')
            assert hasattr(service, 'audio_codec')
    
    def test_transcribe_audio_with_file(self):
        """测试使用音频文件转录"""
        with patch('services.stt_service.sr') as mock_sr:
            mock_recognizer = MagicMock()
            mock_sr.Recognizer.return_value = mock_recognizer
            mock_audio = MockAudioData(16000, b'fake_data' * 1600, 2)
            mock_sr.AudioFile.return_value.__enter__.return_value = mock_audio
            mock_sr.AudioFile.return_value.__exit__ = MagicMock()
            
            # 模拟识别结果
            mock_recognizer.recognize_google.return_value = "测试文本"
            mock_recognizer.record.return_value = mock_audio
            
            service = STTService()
            # 创建一个模拟的文件对象
            mock_file = MagicMock()
            result = service.transcribe_audio(mock_file)
            
            assert result == "测试文本"
    
    def test_transcribe_audio_with_preprocessing(self):
        """测试使用音频文件转录并启用预处理"""
        with patch('services.stt_service.sr') as mock_sr:
            mock_recognizer = MagicMock()
            mock_sr.Recognizer.return_value = mock_recognizer
            mock_audio = MockAudioData(16000, b'fake_data' * 1600, 2)
            mock_sr.AudioFile.return_value.__enter__.return_value = mock_audio
            mock_sr.AudioFile.return_value.__exit__ = MagicMock()
            
            # 模拟识别结果
            mock_recognizer.recognize_google.return_value = "预处理测试文本"
            mock_recognizer.record.return_value = mock_audio
            
            service = STTService()
            # 创建一个模拟的文件对象
            mock_file = MagicMock()
            result = service.transcribe_audio(mock_file, preprocess=True)
            
            assert result == "预处理测试文本"
    
    def test_transcribe_with_preprocessing(self):
        """测试带预处理的音频转文本"""
        with patch('services.stt_service.sr') as mock_sr:
            mock_recognizer = MagicMock()
            mock_sr.Recognizer.return_value = mock_recognizer
            mock_audio = MockAudioData(16000, b'fake_data' * 1600, 2)
            mock_sr.AudioFile.return_value.__enter__.return_value = mock_audio
            mock_sr.AudioFile.return_value.__exit__ = MagicMock()
            
            # 模拟识别结果
            mock_recognizer.recognize_google.return_value = "预处理测试文本"
            mock_recognizer.record.return_value = mock_audio
            
            service = STTService()
            # 创建一个模拟的文件对象
            mock_file = MagicMock()
            result = service.transcribe_with_preprocessing(mock_file)
            
            assert result == "预处理测试文本"
    
    def test_get_audio_info(self):
        """测试获取音频文件信息"""
        with patch('services.stt_service.sr') as mock_sr:
            mock_recognizer = MagicMock()
            mock_sr.Recognizer.return_value = mock_recognizer
            
            # 模拟recognizer.record方法的返回值
            mock_audio_data = MockAudioData(16000, b'fake_data' * 1600, 2)
            mock_recognizer.record.return_value = mock_audio_data
            
            mock_sr.AudioFile.return_value.__enter__.return_value = MagicMock()
            
            service = STTService()
            result = service.get_audio_info("fake_audio_file.wav")  # type: ignore
            
            assert "sample_rate" in result
            assert "duration" in result
            assert "sample_width" in result
            assert result["sample_rate"] == 16000
            assert result["sample_width"] == 2