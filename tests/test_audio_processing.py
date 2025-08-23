import pytest
import numpy as np
from services.processing import AudioProcessingService


class TestAudioProcessingService:
    """测试音频处理服务"""
    
    def test_init(self):
        """测试AudioProcessingService初始化"""
        service = AudioProcessingService()
        assert service is not None
    
    def test_normalize_audio(self):
        """测试音频归一化功能"""
        service = AudioProcessingService()
        
        # 创建测试音频数据
        audio_data = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        normalized = service.normalize_audio(audio_data, target_rms=0.2)
        
        # 验证归一化结果
        assert normalized is not None
        assert len(normalized) == len(audio_data)
        
        # 验证均方根值接近目标值
        rms = np.sqrt(np.mean(normalized**2))
        assert abs(rms - 0.2) < 0.01
    
    def test_normalize_audio_zero_rms(self):
        """测试零均方根值音频的归一化"""
        service = AudioProcessingService()
        
        # 创建零音频数据
        audio_data = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        normalized = service.normalize_audio(audio_data)
        
        # 验证结果
        assert np.array_equal(normalized, audio_data)
    
    def test_remove_silence(self):
        """测试移除静音功能"""
        service = AudioProcessingService()
        sample_rate = 16000
        
        # 创建包含静音的测试音频
        silent_part = np.zeros(1000)  # 静音部分
        audio_part = np.ones(1000) * 0.5  # 音频部分
        audio_data = np.concatenate([silent_part, audio_part, silent_part])
        
        # 移除静音
        processed = service.remove_silence(audio_data, sample_rate, silence_threshold=0.1)
        
        # 验证结果
        assert processed is not None
        # 处理后的音频应该比原音频短
        assert len(processed) <= len(audio_data)
        # 应该保留非静音部分
        assert len(processed) > 0
    
    def test_remove_all_silence(self):
        """测试全静音音频的处理"""
        service = AudioProcessingService()
        sample_rate = 16000
        
        # 创建全静音音频
        audio_data = np.zeros(1000)
        processed = service.remove_silence(audio_data, sample_rate)
        
        # 验证结果
        assert len(processed) == 0
    
    def test_resample_audio_upsample(self):
        """测试上采样功能"""
        service = AudioProcessingService()
        
        # 创建测试音频数据
        audio_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        original_rate = 8000
        target_rate = 16000
        
        # 上采样
        resampled = service.resample_audio(audio_data, original_rate, target_rate)
        
        # 验证结果
        assert resampled is not None
        # 上采样后长度应该增加
        assert len(resampled) > len(audio_data)
    
    def test_resample_audio_downsample(self):
        """测试下采样功能"""
        service = AudioProcessingService()
        
        # 创建测试音频数据
        audio_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
        original_rate = 16000
        target_rate = 8000
        
        # 下采样
        resampled = service.resample_audio(audio_data, original_rate, target_rate)
        
        # 验证结果
        assert resampled is not None
        # 下采样后长度应该减少
        assert len(resampled) < len(audio_data)
    
    def test_resample_audio_same_rate(self):
        """测试相同采样率的处理"""
        service = AudioProcessingService()
        
        # 创建测试音频数据
        audio_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        rate = 16000
        
        # 相同采样率处理
        resampled = service.resample_audio(audio_data, rate, rate)
        
        # 验证结果
        assert np.array_equal(resampled, audio_data)
    
    def test_preprocess_audio(self):
        """测试完整的音频预处理流程"""
        service = AudioProcessingService()
        original_rate = 16000
        target_rate = 16000
        
        # 创建测试音频数据
        silent_part = np.zeros(1000)
        audio_part = np.ones(1000) * 0.3
        audio_data = np.concatenate([silent_part, audio_part, silent_part])
        
        # 预处理
        processed = service.preprocess_audio(audio_data, original_rate, target_rate)
        
        # 验证结果
        assert processed is not None
        assert len(processed) <= len(audio_data)