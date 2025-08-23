import numpy as np
from typing import List, Tuple, Optional
import hashlib


class VoiceVerificationService:
    """
    声纹验证服务
    用于验证用户身份的声纹识别功能
    """
    
    def __init__(self):
        # 存储用户声纹特征的字典
        self.user_voiceprints = {}
    
    def extract_voice_features(self, audio_data: np.ndarray, sample_rate: int) -> List[float]:
        """
        提取音频的声纹特征
        
        Args:
            audio_data: 音频数据数组
            sample_rate: 采样率
            
        Returns:
            声纹特征向量
        """
        # 简化的声纹特征提取方法
        # 实际项目中可以使用更复杂的特征提取算法
        
        # 1. 计算音频的基本统计特征
        mean_amplitude = np.mean(np.abs(audio_data))
        std_amplitude = np.std(audio_data)
        zero_crossing_rate = self._calculate_zero_crossing_rate(audio_data)
        spectral_centroid = self._calculate_spectral_centroid(audio_data, sample_rate)
        
        # 2. 计算能量分布特征
        energy_low, energy_mid, energy_high = self._calculate_frequency_bands_energy(
            audio_data, sample_rate)
        
        # 3. 组合特征向量
        features = [
            mean_amplitude,
            std_amplitude,
            zero_crossing_rate,
            spectral_centroid,
            energy_low,
            energy_mid,
            energy_high
        ]
        
        return features
    
    def _calculate_zero_crossing_rate(self, audio_data: np.ndarray) -> float:
        """
        计算过零率
        
        Args:
            audio_data: 音频数据数组
            
        Returns:
            过零率
        """
        # 计算符号变化次数
        zero_crossings = np.sum(np.diff(np.sign(audio_data)) != 0)
        return zero_crossings / len(audio_data)
    
    def _calculate_spectral_centroid(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """
        计算频谱质心
        
        Args:
            audio_data: 音频数据数组
            sample_rate: 采样率
            
        Returns:
            频谱质心
        """
        # 计算FFT
        fft = np.fft.fft(audio_data)
        magnitude = np.abs(fft)
        freqs = np.fft.fftfreq(len(audio_data), 1/sample_rate)
        
        # 只考虑正频率部分
        positive_freqs = freqs[:len(freqs)//2]
        positive_magnitude = magnitude[:len(magnitude)//2]
        
        # 计算频谱质心
        if np.sum(positive_magnitude) == 0:
            return 0.0
            
        spectral_centroid = np.sum(positive_freqs * positive_magnitude) / np.sum(positive_magnitude)
        return spectral_centroid
    
    def _calculate_frequency_bands_energy(self, audio_data: np.ndarray, sample_rate: int) -> Tuple[float, float, float]:
        """
        计算不同频段的能量分布
        
        Args:
            audio_data: 音频数据数组
            sample_rate: 采样率
            
        Returns:
            低频、中频、高频能量
        """
        # 计算FFT
        fft = np.fft.fft(audio_data)
        magnitude = np.abs(fft)
        freqs = np.fft.fftfreq(len(audio_data), 1/sample_rate)
        
        # 只考虑正频率部分
        positive_freqs = freqs[:len(freqs)//2]
        positive_magnitude = magnitude[:len(magnitude)//2]
        
        # 定义频段（Hz）
        low_freq = 300
        mid_freq = 1000
        high_freq = 3000
        
        # 计算各频段能量
        low_energy = np.sum(positive_magnitude[positive_freqs <= low_freq])
        mid_energy = np.sum(positive_magnitude[(positive_freqs > low_freq) & (positive_freqs <= mid_freq)])
        high_energy = np.sum(positive_magnitude[(positive_freqs > mid_freq) & (positive_freqs <= high_freq)])
        
        return float(low_energy), float(mid_energy), float(high_energy)
    
    def register_user_voiceprint(self, user_id: int, features: List[float]) -> bool:
        """
        注册用户声纹
        
        Args:
            user_id: 用户ID
            features: 声纹特征向量
            
        Returns:
            注册是否成功
        """
        try:
            # 存储用户声纹特征
            self.user_voiceprints[user_id] = {
                'features': features,
                'created_at': np.datetime64('now')
            }
            return True
        except Exception as e:
            print(f"注册用户声纹失败: {str(e)}")
            return False
    
    def verify_user_voiceprint(self, user_id: int, features: List[float], 
                             threshold: float = 0.8) -> Tuple[bool, float]:
        """
        验证用户声纹
        
        Args:
            user_id: 用户ID
            features: 待验证的声纹特征向量
            threshold: 验证阈值（相似度阈值）
            
        Returns:
            (验证结果, 相似度分数)
        """
        # 检查用户是否存在
        if user_id not in self.user_voiceprints:
            return False, 0.0
        
        # 获取注册的声纹特征
        registered_features = self.user_voiceprints[user_id]['features']
        
        # 计算相似度
        similarity = self._calculate_similarity(registered_features, features)
        
        # 判断验证结果
        is_verified = similarity >= threshold
        
        return is_verified, similarity
    
    def _calculate_similarity(self, features1: List[float], features2: List[float]) -> float:
        """
        计算两个特征向量的相似度（余弦相似度）
        
        Args:
            features1: 特征向量1
            features2: 特征向量2
            
        Returns:
            相似度分数 (0-1)
        """
        # 转换为numpy数组
        vec1 = np.array(features1)
        vec2 = np.array(features2)
        
        # 计算余弦相似度
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        similarity = dot_product / (norm1 * norm2)
        # 限制在0-1范围内
        return max(0.0, min(1.0, similarity))
    
    def remove_user_voiceprint(self, user_id: int) -> bool:
        """
        删除用户声纹
        
        Args:
            user_id: 用户ID
            
        Returns:
            删除是否成功
        """
        if user_id in self.user_voiceprints:
            del self.user_voiceprints[user_id]
            return True
        return False