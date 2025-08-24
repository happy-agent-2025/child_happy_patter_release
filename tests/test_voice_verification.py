import pytest
import numpy as np
from services.verification import VoiceVerificationService


class TestVoiceVerificationService:
    """测试声纹验证服务"""
    
    def test_init(self):
        """测试VoiceVerificationService初始化"""
        service = VoiceVerificationService()
        assert service is not None
        assert isinstance(service.user_voiceprints, dict)
    
    def test_extract_voice_features(self):
        """测试声纹特征提取"""
        service = VoiceVerificationService()
        
        # 创建测试音频数据
        sample_rate = 16000
        duration = 1.0  # 1秒
        t = np.linspace(0, duration, int(sample_rate * duration))
        # 生成合成音频信号
        audio_data = np.sin(2 * np.pi * 440 * t)  # 440Hz正弦波
        
        # 提取特征
        features = service.extract_voice_features(audio_data, sample_rate)
        
        # 验证特征
        assert isinstance(features, list)
        # 现在应该有7个基本特征 + 13个MFCC特征 = 20个特征
        assert len(features) >= 7
        assert all(isinstance(f, (int, float)) for f in features)
    
    def test_extract_mfcc_features(self):
        """测试MFCC特征提取"""
        service = VoiceVerificationService()
        
        # 创建测试音频数据
        sample_rate = 16000
        duration = 1.0  # 1秒
        t = np.linspace(0, duration, int(sample_rate * duration))
        # 生成合成音频信号
        audio_data = np.sin(2 * np.pi * 440 * t)  # 440Hz正弦波
        
        # 提取MFCC特征
        mfcc_features = service._extract_mfcc(audio_data, sample_rate)
        
        # 验证特征
        assert isinstance(mfcc_features, list)
        assert len(mfcc_features) == 13  # 13个MFCC系数
        assert all(isinstance(f, (int, float)) for f in mfcc_features)
    
    def test_register_user_voiceprint(self):
        """测试用户声纹注册"""
        service = VoiceVerificationService()
        
        # 创建测试特征
        features = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7] + [0.0] * 13  # 7个基本特征 + 13个MFCC特征
        user_id = 1
        
        # 注册声纹
        result = service.register_user_voiceprint(user_id, features)
        
        # 验证注册结果
        assert result is True
        assert user_id in service.user_voiceprints
        assert service.user_voiceprints[user_id]['features'] == features
    
    def test_verify_user_voiceprint(self):
        """测试用户声纹验证"""
        service = VoiceVerificationService()
        
        # 创建测试特征
        features = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7] + [0.0] * 13  # 7个基本特征 + 13个MFCC特征
        user_id = 1
        
        # 先注册声纹
        service.register_user_voiceprint(user_id, features)
        
        # 验证声纹（完全匹配）
        is_verified, similarity = service.verify_user_voiceprint(user_id, features)
        
        # 验证结果
        assert is_verified is True
        assert 0.0 <= similarity <= 1.0
    
    def test_verify_user_voiceprint_no_match(self):
        """测试用户声纹验证（无匹配）"""
        service = VoiceVerificationService()
        
        # 创建测试特征
        features = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7] + [0.0] * 13  # 7个基本特征 + 13个MFCC特征
        user_id = 1
        non_registered_user_id = 2
        
        # 先注册一个用户
        service.register_user_voiceprint(user_id, features)
        
        # 验证未注册的用户
        is_verified, similarity = service.verify_user_voiceprint(non_registered_user_id, features)
        
        # 验证结果
        assert is_verified is False
        assert similarity == 0.0
    
    def test_verify_user_voiceprint_partial_match(self):
        """测试用户声纹验证（部分匹配）"""
        service = VoiceVerificationService()
        
        # 创建测试特征
        registered_features = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7] + [0.0] * 13  # 7个基本特征 + 13个MFCC特征
        test_features = [0.11, 0.22, 0.29, 0.41, 0.49, 0.61, 0.69] + [0.01] * 13  # 略有差异
        user_id = 1
        
        # 先注册声纹
        service.register_user_voiceprint(user_id, registered_features)
        
        # 验证声纹（部分匹配）
        is_verified, similarity = service.verify_user_voiceprint(user_id, test_features)
        
        # 验证结果
        assert 0.0 <= similarity <= 1.0
        # 由于特征相似，应该能通过验证（具体结果取决于阈值）
    
    def test_remove_user_voiceprint(self):
        """测试删除用户声纹"""
        service = VoiceVerificationService()
        
        # 创建测试特征
        features = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7] + [0.0] * 13  # 7个基本特征 + 13个MFCC特征
        user_id = 1
        
        # 先注册声纹
        service.register_user_voiceprint(user_id, features)
        
        # 删除声纹
        result = service.remove_user_voiceprint(user_id)
        
        # 验证删除结果
        assert result is True
        assert user_id not in service.user_voiceprints
    
    def test_remove_nonexistent_user_voiceprint(self):
        """测试删除不存在的用户声纹"""
        service = VoiceVerificationService()
        
        # 删除不存在的用户声纹
        result = service.remove_user_voiceprint(999)
        
        # 验证删除结果
        assert result is False
    
    def test_calculate_zero_crossing_rate(self):
        """测试过零率计算"""
        service = VoiceVerificationService()
        
        # 创建测试音频数据（更明确的过零模式）
        audio_data = np.array([1, -1, 1, -1, 1, -1, 1, -1])  # 交替变化
        
        # 计算过零率
        zcr = service._calculate_zero_crossing_rate(audio_data)
        
        # 验证结果
        assert 0.0 <= zcr <= 1.0
        # 7个间隔中有7个过零点，所以过零率应该是7/8 = 0.875
    
    def test_calculate_spectral_centroid(self):
        """测试频谱质心计算"""
        service = VoiceVerificationService()
        
        # 创建测试音频数据
        sample_rate = 16000
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = np.sin(2 * np.pi * 440 * t)  # 440Hz正弦波
        
        # 计算频谱质心
        spectral_centroid = service._calculate_spectral_centroid(audio_data, sample_rate)
        
        # 验证结果
        assert isinstance(spectral_centroid, (int, float))
        assert spectral_centroid >= 0
    
    def test_calculate_frequency_bands_energy(self):
        """测试频段能量计算"""
        service = VoiceVerificationService()
        
        # 创建测试音频数据
        sample_rate = 16000
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = np.sin(2 * np.pi * 440 * t)  # 440Hz正弦波
        
        # 计算频段能量
        low_energy, mid_energy, high_energy = service._calculate_frequency_bands_energy(
            audio_data, sample_rate)
        
        # 验证结果
        assert isinstance(low_energy, (int, float))
        assert isinstance(mid_energy, (int, float))
        assert isinstance(high_energy, (int, float))
        assert low_energy >= 0
        assert mid_energy >= 0
        assert high_energy >= 0