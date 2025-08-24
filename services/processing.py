import numpy as np
from typing import Tuple, Optional
import warnings
from scipy import signal
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
        移除音频中的静音段（改进算法）
        
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
        
        # 计算音频的短时能量
        frame_length = int(sample_rate * 0.02)  # 20ms帧长
        hop_length = int(sample_rate * 0.01)    # 10ms帧移
        
        # 计算帧数
        num_frames = 1 + int((len(audio_data) - frame_length) / hop_length)
        
        # 计算每帧的能量
        energies = []
        for i in range(num_frames):
            start_idx = i * hop_length
            end_idx = min(start_idx + frame_length, len(audio_data))
            frame = audio_data[start_idx:end_idx]
            energy = np.sum(frame ** 2) / len(frame)
            energies.append(energy)
        
        # 归一化能量
        energies = np.array(energies)
        if np.max(energies) > 0:
            energies = energies / np.max(energies)
        
        # 找到非静音帧
        non_silent_frames = np.where(energies > silence_threshold)[0]
        
        if len(non_silent_frames) == 0:
            # 如果整个音频都是静音，返回空数组
            return np.array([])
        
        # 找到第一个和最后一个非静音帧
        first_frame = max(0, non_silent_frames[0] - min_silence_samples // hop_length)
        last_frame = min(num_frames - 1, non_silent_frames[-1] + min_silence_samples // hop_length)
        
        # 转换为样本索引
        start_idx = max(0, first_frame * hop_length)
        end_idx = min(len(audio_data), (last_frame + 1) * hop_length)
        
        # 返回非静音部分
        return audio_data[start_idx:end_idx]
    
    def resample_audio(self, audio_data: np.ndarray, original_rate: int, 
                      target_rate: int) -> np.ndarray:
        """
        音频重采样（使用scipy高质量重采样算法）
        
        Args:
            audio_data: 音频数据数组
            original_rate: 原始采样率
            target_rate: 目标采样率
            
        Returns:
            重采样后的音频数据
        """
        if original_rate == target_rate:
            return audio_data
            
        # 使用scipy的高质量重采样算法
        # 计算重采样系数
        resample_ratio = target_rate / original_rate
        
        # 使用scipy.signal.resample进行高质量重采样
        if resample_ratio > 1:
            # 上采样
            new_length = int(len(audio_data) * resample_ratio)
            resampled = signal.resample(audio_data, new_length)
        else:
            # 下采样
            new_length = int(len(audio_data) * resample_ratio)
            resampled = signal.resample(audio_data, new_length)
            
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