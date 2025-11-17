import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import hashlib
from scipy.fftpack import dct
from sqlalchemy.orm import Session
from models.voiceprint import Voiceprint, VoiceVerificationLog
from utils.db.database import get_db
import logging

# 配置日志
logger = logging.getLogger(__name__)


class VoiceVerificationService:
    """
    声纹验证服务
    用于验证用户身份的声纹识别功能
    """
    
    def __init__(self):
        # 存储用户声纹特征的字典（内存缓存，提高性能）
        self.user_voiceprints_cache = {}
    
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
    
    def register_user_voiceprint(self, user_id: int, features: List[float], sample_rate: int) -> bool:
        """
        注册用户声纹
        
        Args:
            user_id: 用户ID
            features: 声纹特征向量
            sample_rate: 音频采样率
            
        Returns:
            注册是否成功
        """
        db = None
        try:
            # 获取数据库会话
            db = next(get_db())
            
            # 检查是否已存在声纹记录
            existing_voiceprint = db.query(Voiceprint).filter(Voiceprint.user_id == user_id).first()
            
            if existing_voiceprint:
                # 更新现有声纹
                existing_voiceprint.set_features(features, sample_rate)
            else:
                # 创建新声纹记录
                voiceprint = Voiceprint(
                    user_id=user_id,
                    sample_rate=sample_rate,
                    feature_dimension=len(features)
                )
                voiceprint.set_features(features, sample_rate)
                db.add(voiceprint)
            
            # 确保数据库提交成功
            db.commit()
            
            # 验证提交是否真的成功 - 重新查询确认数据已持久化
            committed_voiceprint = db.query(Voiceprint).filter(Voiceprint.user_id == user_id).first()
            if not committed_voiceprint:
                raise Exception("数据库提交后数据未找到，提交可能未成功")
            
            # 只有在数据库操作确认成功后更新内存缓存
            self.user_voiceprints_cache[user_id] = {
                'features': features,
                'sample_rate': sample_rate,
                'created_at': np.datetime64('now')
            }
            
            logger.info(f"用户 {user_id} 声纹注册成功，数据库和缓存均已更新")
            return True
            
        except Exception as e:
            # 如果数据库操作失败，确保回滚
            if db:
                try:
                    db.rollback()
                    logger.warning(f"数据库操作失败，已执行回滚: {str(e)}")
                except Exception as rollback_error:
                    logger.error(f"回滚操作也失败: {str(rollback_error)}")
            
            logger.error(f"注册用户声纹失败: {str(e)}")
            
            # 如果缓存中可能存在不一致数据，清理缓存
            if user_id in self.user_voiceprints_cache:
                del self.user_voiceprints_cache[user_id]
                logger.warning(f"清理了可能不一致的缓存数据 for user {user_id}")
            
            return False
    
    def verify_user_voiceprint(self, user_id: int, features: List[float], 
                             threshold: float = 0.8, audio_duration: int = 0) -> Tuple[bool, float]:
        """
        验证用户声纹
        
        Args:
            user_id: 用户ID
            features: 待验证的声纹特征向量
            threshold: 验证阈值（相似度阈值）
            audio_duration: 音频时长(毫秒)
            
        Returns:
            (验证结果, 相似度分数)
        """
        # 首先检查内存缓存
        if user_id in self.user_voiceprints_cache:
            registered_features = self.user_voiceprints_cache[user_id]['features']
        else:
            # 从数据库查询声纹特征
            try:
                db = next(get_db())
                voiceprint = db.query(Voiceprint).filter(Voiceprint.user_id == user_id).first()
                
                if not voiceprint:
                    self._log_verification(user_id, False, 0.0, audio_duration)
                    return False, 0.0
                
                registered_features, sample_rate = voiceprint.get_features()
                if not registered_features:
                    self._log_verification(user_id, False, 0.0, audio_duration)
                    return False, 0.0
                
                # 更新内存缓存
                self.user_voiceprints_cache[user_id] = {
                    'features': registered_features,
                    'sample_rate': sample_rate,
                    'created_at': np.datetime64('now')
                }
                
            except Exception as e:
                logger.error(f"查询用户声纹失败: {str(e)}")
                self._log_verification(user_id, False, 0.0, audio_duration)
                return False, 0.0
        
        # 计算相似度
        similarity = self._calculate_similarity(registered_features, features)
        similarity_percent = round(similarity * 100, 2)
        
        # 判断验证结果
        is_verified = similarity >= threshold
        
        # 记录验证日志
        self._log_verification(user_id, is_verified, similarity_percent, audio_duration)
        
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
    
    def _log_verification(self, user_id: int, result: bool, similarity: float, audio_duration: int):
        """记录声纹验证日志"""
        try:
            db = next(get_db())
            log = VoiceVerificationLog(
                user_id=user_id,
                verification_result=1 if result else 0,
                similarity_score=int(similarity),
                audio_duration=audio_duration
            )
            db.add(log)
            db.commit()
            logger.info(f"声纹验证日志记录成功: 用户 {user_id}, 结果 {result}, 相似度 {similarity}%")
        except Exception as e:
            logger.error(f"记录声纹验证日志失败: {str(e)}")
    
    def remove_user_voiceprint(self, user_id: int) -> bool:
        """
        删除用户声纹
        
        Args:
            user_id: 用户ID
            
        Returns:
            删除是否成功（如果用户不存在返回False）
        """
        try:
            db = next(get_db())
            
            # 检查用户是否存在
            voiceprint = db.query(Voiceprint).filter(Voiceprint.user_id == user_id).first()
            
            # 如果用户不存在，返回False
            if not voiceprint and user_id not in self.user_voiceprints_cache:
                return False
            
            # 删除数据库中的声纹记录
            if voiceprint:
                db.delete(voiceprint)
            
            # 删除内存缓存
            if user_id in self.user_voiceprints_cache:
                del self.user_voiceprints_cache[user_id]
            
            db.commit()
            logger.info(f"用户 {user_id} 声纹删除成功")
            return True
            
        except Exception as e:
            logger.error(f"删除用户声纹失败: {str(e)}")
            return False
    
    def load_all_voiceprints_to_cache(self) -> bool:
        """
        加载所有声纹到内存缓存
        
        Returns:
            加载是否成功
        """
        try:
            db = next(get_db())
            voiceprints = db.query(Voiceprint).all()
            
            for voiceprint in voiceprints:
                features, sample_rate = voiceprint.get_features()
                if features and sample_rate:
                    self.user_voiceprints_cache[voiceprint.user_id] = {
                        'features': features,
                        'sample_rate': sample_rate,
                        'created_at': np.datetime64('now')
                    }
            
            logger.info(f"成功加载 {len(voiceprints)} 个声纹到内存缓存")
            return True
            
        except Exception as e:
            logger.error(f"加载声纹到缓存失败: {str(e)}")
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