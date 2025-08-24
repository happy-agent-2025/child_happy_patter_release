import numpy as np
from typing import List, Tuple, Optional
import hashlib
from scipy.fftpack import dct


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
        # 使用更全面的声纹特征提取方法
        
        # 1. 计算基本统计特征
        mean_amplitude = np.mean(np.abs(audio_data))
        std_amplitude = np.std(audio_data)
        zero_crossing_rate = self._calculate_zero_crossing_rate(audio_data)
        spectral_centroid = self._calculate_spectral_centroid(audio_data, sample_rate)
        
        # 2. 计算能量分布特征
        energy_low, energy_mid, energy_high = self._calculate_frequency_bands_energy(
            audio_data, sample_rate)
        
        # 3. 计算MFCC特征
        mfcc_features = self._extract_mfcc(audio_data, sample_rate)
        
        # 4. 组合所有特征向量
        features = [
            mean_amplitude,
            std_amplitude,
            zero_crossing_rate,
            spectral_centroid,
            energy_low,
            energy_mid,
            energy_high
        ]
        
        # 添加MFCC特征
        features.extend(mfcc_features)
        
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
    
    def _extract_mfcc(self, audio_data: np.ndarray, sample_rate: int, 
                      num_mfcc: int = 13) -> List[float]:
        """
        提取MFCC（梅尔频率倒谱系数）特征
        
        Args:
            audio_data: 音频数据数组
            sample_rate: 采样率
            num_mfcc: 要提取的MFCC系数数量
            
        Returns:
            MFCC特征向量
        """
        # 预加重
        pre_emphasis = 0.97
        emphasized_signal = np.append(audio_data[0], audio_data[1:] - pre_emphasis * audio_data[:-1])
        
        # 分帧
        frame_size = 0.025  # 25ms
        frame_stride = 0.01  # 10ms
        frame_length = int(round(frame_size * sample_rate))
        frame_step = int(round(frame_stride * sample_rate))
        signal_length = len(emphasized_signal)
        num_frames = int(np.ceil(float(np.abs(signal_length - frame_length)) / frame_step)) + 1
        pad_signal_length = num_frames * frame_step + frame_length
        z = np.zeros((pad_signal_length - signal_length))
        pad_signal = np.append(emphasized_signal, z)
        
        # 提取帧
        indices = np.tile(np.arange(0, frame_length), (num_frames, 1)) + np.tile(
            np.arange(0, num_frames * frame_step, frame_step), (frame_length, 1)).T
        frames = pad_signal[indices.astype(np.int32, copy=False)]
        
        # 加窗
        frames *= np.hamming(frame_length)
        
        # FFT和功率谱
        NFFT = 512
        mag_frames = np.absolute(np.fft.rfft(frames, NFFT))
        pow_frames = ((1.0 / NFFT) * ((mag_frames) ** 2))
        
        # 计算梅尔滤波器组
        nfilt = 40
        low_freq_mel = 0
        high_freq_mel = (2595 * np.log10(1 + (sample_rate / 2) / 700))
        mel_points = np.linspace(low_freq_mel, high_freq_mel, nfilt + 2)
        hz_points = (700 * (10**(mel_points / 2595) - 1))
        bin = np.floor((NFFT + 1) * hz_points / sample_rate)
        fbank = np.zeros((nfilt, int(np.floor(NFFT / 2 + 1))))
        
        for m in range(1, nfilt + 1):
            f_m_minus = int(bin[m - 1])
            f_m = int(bin[m])
            f_m_plus = int(bin[m + 1])
            
            for k in range(f_m_minus, f_m):
                fbank[m - 1, k] = (k - bin[m - 1]) / (bin[m] - bin[m - 1])
            for k in range(f_m, f_m_plus):
                fbank[m - 1, k] = (bin[m + 1] - k) / (bin[m + 1] - bin[m])
        
        filter_banks = np.dot(pow_frames, fbank.T)
        filter_banks = np.where(filter_banks == 0, np.finfo(float).eps, filter_banks)
        filter_banks = 20 * np.log10(filter_banks)
        
        # DCT变换得到MFCC
        mfcc = dct(filter_banks, type=2, axis=1, norm='ortho')[:, :num_mfcc]
        
        # 返回平均MFCC系数作为特征
        return np.mean(mfcc, axis=0).tolist()