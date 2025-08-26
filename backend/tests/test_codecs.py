import pytest
import numpy as np
from services.codecs import AudioCodecService


class TestAudioCodecService:
    """测试音频编解码服务"""
    
    def test_init(self):
        """测试AudioCodecService初始化"""
        service = AudioCodecService()
        assert service is not None
    
    def test_encode_wav_16bit(self):
        """测试16位WAV编码"""
        service = AudioCodecService()
        
        # 创建测试音频数据
        audio_data = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        wav_data = service.encode_wav(audio_data, sample_rate=16000, sample_width=2)
        
        # 验证结果
        assert isinstance(wav_data, bytes)
        assert len(wav_data) > 0
    
    def test_encode_wav_8bit(self):
        """测试8位WAV编码"""
        service = AudioCodecService()
        
        # 创建测试音频数据
        audio_data = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        wav_data = service.encode_wav(audio_data, sample_rate=16000, sample_width=1)
        
        # 验证结果
        assert isinstance(wav_data, bytes)
        assert len(wav_data) > 0
    
    def test_decode_wav(self):
        """测试WAV解码"""
        service = AudioCodecService()
        
        # 创建测试音频数据并编码
        original_data = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        wav_data = service.encode_wav(original_data, sample_rate=16000, sample_width=2)
        
        # 解码
        decoded_data, sample_rate = service.decode_wav(wav_data)
        
        # 验证结果
        assert isinstance(decoded_data, np.ndarray)
        assert sample_rate == 16000
        # 由于编码解码过程中的精度损失，使用近似相等比较
        np.testing.assert_array_almost_equal(decoded_data, original_data, decimal=4)
    
    def test_encode_mp3(self):
        """测试MP3编码"""
        service = AudioCodecService()
        
        # 创建测试音频数据
        audio_data = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        mp3_data = service.encode_mp3(audio_data, sample_rate=16000)
        
        # 验证结果
        assert isinstance(mp3_data, bytes)
        assert len(mp3_data) > 0
    
    def test_decode_mp3(self):
        """测试MP3解码"""
        service = AudioCodecService()
        
        # 创建测试音频数据并编码
        original_data = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        mp3_data = service.encode_mp3(original_data, sample_rate=16000)
        
        # 解码
        decoded_data, sample_rate = service.decode_mp3(mp3_data)
        
        # 验证结果
        assert isinstance(decoded_data, np.ndarray)
        assert sample_rate == 16000
    
    def test_encode_flac(self):
        """测试FLAC编码"""
        service = AudioCodecService()
        
        # 创建测试音频数据
        audio_data = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        flac_data = service.encode_flac(audio_data, sample_rate=16000)
        
        # 验证结果
        assert isinstance(flac_data, bytes)
        assert len(flac_data) > 0
    
    def test_decode_flac(self):
        """测试FLAC解码"""
        service = AudioCodecService()
        
        # 创建测试音频数据并编码
        original_data = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        flac_data = service.encode_flac(original_data, sample_rate=16000)
        
        # 解码
        decoded_data, sample_rate = service.decode_flac(flac_data)
        
        # 验证结果
        assert isinstance(decoded_data, np.ndarray)
        assert sample_rate == 16000
    
    def test_compress_decompress_audio(self):
        """测试音频压缩和解压缩"""
        service = AudioCodecService()
        
        # 创建测试音频数据（使用更长的数据以便压缩有效果）
        test_data = b"test audio data for compression" * 10  # 重复数据更容易压缩
        
        # 压缩
        compressed = service.compress_audio(test_data)
        assert isinstance(compressed, bytes)
        # 对于重复数据，压缩后应该更小
        assert len(compressed) < len(test_data)
        
        # 解压缩
        decompressed = service.decompress_audio(compressed)
        assert isinstance(decompressed, bytes)
        assert decompressed == test_data
    
    def test_convert_sample_rate(self):
        """测试采样率转换"""
        service = AudioCodecService()
        
        # 创建测试音频数据
        audio_data = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
        original_rate = 8000
        target_rate = 16000
        
        # 转换采样率
        converted_data = service.convert_sample_rate(audio_data, original_rate, target_rate)
        
        # 验证结果
        assert isinstance(converted_data, np.ndarray)
        # 上采样后数据长度应该增加
        assert len(converted_data) > len(audio_data)
    
    def test_convert_sample_rate_same_rate(self):
        """测试相同采样率转换"""
        service = AudioCodecService()
        
        # 创建测试音频数据
        audio_data = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        rate = 16000
        
        # 转换采样率
        converted_data = service.convert_sample_rate(audio_data, rate, rate)
        
        # 验证结果
        assert isinstance(converted_data, np.ndarray)
        np.testing.assert_array_equal(converted_data, audio_data)