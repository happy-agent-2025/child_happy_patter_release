import pytest
from unittest.mock import patch, MagicMock
from services.tts_service import TTSService
from io import BytesIO
import tempfile
import os


class TestTTSService:
    """测试TTSService类"""
    
    def test_init(self):
        """测试TTSService初始化"""
        with patch('services.tts_service.pyttsx3') as mock_pyttsx3:
            mock_engine = MagicMock()
            mock_pyttsx3.init.return_value = mock_engine
            mock_voice = MagicMock()
            mock_voice.id = 'test_voice'
            mock_voice.name = 'Test Voice'
            mock_voice.languages = ['zh-CN']
            mock_engine.getProperty.return_value = [mock_voice]
            
            service = TTSService()
            assert service is not None
            assert service.engine == mock_engine
            mock_engine.setProperty.assert_any_call('rate', 150)
            mock_engine.setProperty.assert_any_call('volume', 0.9)
    
    def test_synthesize_speech(self):
        """测试语音合成"""
        with patch('services.tts_service.pyttsx3') as mock_pyttsx3, \
             patch('services.tts_service.tempfile') as mock_tempfile, \
             patch('services.tts_service.open', create=True) as mock_open, \
             patch('services.tts_service.os') as mock_os:
            
            mock_engine = MagicMock()
            mock_pyttsx3.init.return_value = mock_engine
            
            # 模拟临时文件
            mock_temp_file = MagicMock()
            mock_tempfile.NamedTemporaryFile.return_value.__enter__.return_value = mock_temp_file
            mock_temp_file.name = 'temp_test.wav'
            
            # 模拟文件读取
            mock_open.return_value.__enter__.return_value.read.return_value = b'fake_audio_data'
            mock_os.path.exists.return_value = True
            
            service = TTSService()
            result = service.synthesize_speech("测试文本")
            
            assert isinstance(result, BytesIO)
            mock_engine.save_to_file.assert_called_once_with("测试文本", 'temp_test.wav')
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
    
    def test_set_voice_properties(self):
        """测试设置语音属性"""
        with patch('services.tts_service.pyttsx3') as mock_pyttsx3:
            mock_engine = MagicMock()
            mock_pyttsx3.init.return_value = mock_engine
            
            service = TTSService()
            
            # 测试设置语速
            service.set_voice_properties(rate=200)
            mock_engine.setProperty.assert_called_with('rate', 200)
            
            # 测试设置音量
            service.set_voice_properties(volume=0.5)
            mock_engine.setProperty.assert_called_with('volume', 0.5)
            
            # 测试设置语音
            service.set_voice_properties(voice_id='test_voice')
            mock_engine.setProperty.assert_called_with('voice', 'test_voice')
    
    def test_get_available_voices(self):
        """测试获取可用语音列表"""
        with patch('services.tts_service.pyttsx3') as mock_pyttsx3:
            mock_engine = MagicMock()
            mock_pyttsx3.init.return_value = mock_engine
            
            # 模拟语音数据
            mock_voice = MagicMock()
            mock_voice.id = 'test_voice'
            mock_voice.name = 'Test Voice'
            mock_voice.languages = ['zh-CN']
            mock_voice.gender = 'female'
            mock_engine.getProperty.return_value = [mock_voice]
            
            service = TTSService()
            voices = service.get_available_voices()
            
            assert isinstance(voices, list)
            assert len(voices) == 1
            assert voices[0]['id'] == 'test_voice'
            assert voices[0]['name'] == 'Test Voice'
            assert voices[0]['languages'] == ['zh-CN']
            assert voices[0]['gender'] == 'female'