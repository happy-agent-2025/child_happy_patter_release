import numpy as np
from typing import Tuple, Optional
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)


class AudioProcessingService:
    """
    音频预处理服务
    包括音频归一化、静音移除、重采样等功能
    """
    
    def __init__(self):
        pass
    
    def normalize_audio(self, audio_data: np.ndarray, target_rms: float = 0.1) -> np.ndarray:
        """
        音频归一化处理
        
        Args:
            audio_data: 音频数据数组
            target_rms: 目标均方根值
            
        Returns:
            归一化后的音频数据
        """
        # 计算当前音频的均方根值
        current_rms = np.sqrt(np.mean(audio_data**2))
        
        if current_rms == 0:
            return audio_data
            
        # 计算增益因子
        gain = target_rms / current_rms
        
        # 应用增益
        normalized_audio = audio_data * gain
        
        # 确保数值在合法范围内
        normalized_audio = np.clip(normalized_audio, -1.0, 1.0)
        
        return normalized_audio
    
    def remove_silence(self, audio_data: np.ndarray, sample_rate: int, 
                      silence_threshold: float = 0.01, 
                      min_silence_duration: float = 0.1) -> np.ndarray:
        """
        移除音频中的静音段
        
        Args:
            audio_data: 音频数据数组
            sample_rate: 采样率
            silence_threshold: 静音阈值（0-1之间）
            min_silence_duration: 最小静音持续时间（秒）
            
        Returns:
            移除静音后的音频数据
        """
        # 计算最小静音样本数
        min_silence_samples = int(sample_rate * min_silence_duration)
        
        # 找到非静音区域
        non_silent_indices = np.where(np.abs(audio_data) > silence_threshold)[0]
        
        if len(non_silent_indices) == 0:
            # 如果整个音频都是静音，返回空数组
            return np.array([])
        
        # 找到第一个和最后一个非静音样本
        start_idx = max(0, non_silent_indices[0] - min_silence_samples)
        end_idx = min(len(audio_data), non_silent_indices[-1] + min_silence_samples)
        
        # 返回非静音部分
        return audio_data[start_idx:end_idx]
    
    def resample_audio(self, audio_data: np.ndarray, original_rate: int, 
                      target_rate: int) -> np.ndarray:
        """
        音频重采样
        
        Args:
            audio_data: 音频数据数组
            original_rate: 原始采样率
            target_rate: 目标采样率
            
        Returns:
            重采样后的音频数据
        """
        if original_rate == target_rate:
            return audio_data
            
        # 计算重采样比例
        ratio = target_rate / original_rate
        
        # 计算新长度
        new_length = int(len(audio_data) * ratio)
        
        # 简单的线性重采样（实际项目中可以使用更高级的算法）
        if new_length > len(audio_data):
            # 上采样 - 插值
            indices = np.linspace(0, len(audio_data) - 1, new_length)
            resampled = np.interp(indices, np.arange(len(audio_data)), audio_data)
        else:
            # 下采样 - 选择性采样
            indices = np.linspace(0, len(audio_data) - 1, new_length)
            resampled = audio_data[np.round(indices).astype(int)]
            
        return resampled
    
    def preprocess_audio(self, audio_data: np.ndarray, original_rate: int,
                        target_rate: int = 16000, target_rms: float = 0.1,
                        silence_threshold: float = 0.01) -> np.ndarray:
        """
        完整的音频预处理流程
        
        Args:
            audio_data: 音频数据数组
            original_rate: 原始采样率
            target_rate: 目标采样率
            target_rms: 目标均方根值
            silence_threshold: 静音阈值
            
        Returns:
            预处理后的音频数据
        """
        # 1. 移除静音
        audio_data = self.remove_silence(audio_data, original_rate, silence_threshold)
        
        # 2. 归一化
        audio_data = self.normalize_audio(audio_data, target_rms)
        
        # 3. 重采样
        audio_data = self.resample_audio(audio_data, original_rate, target_rate)
        
        return audio_data