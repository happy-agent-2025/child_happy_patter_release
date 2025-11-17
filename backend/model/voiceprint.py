from sqlalchemy import Column, Integer, String, DateTime, LargeBinary, ForeignKey
from datetime import datetime, timezone
import json
import numpy as np
from utils.db.database import Base


class Voiceprint(Base):
    __tablename__ = "voiceprints"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, unique=True)
    # 存储声纹特征向量（序列化为JSON字符串）
    features = Column(LargeBinary)  # 存储序列化的特征数据
    algorithm_version = Column(String, default="v1.0")  # 特征提取算法版本
    sample_rate = Column(Integer)  # 音频采样率
    feature_dimension = Column(Integer)  # 特征向量维度
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc))
    
    def set_features(self, features: list, sample_rate: int):
        """序列化并存储声纹特征"""
        feature_data = {
            'features': features,
            'sample_rate': sample_rate,
            'dimension': len(features)
        }
        self.features = json.dumps(feature_data).encode('utf-8')
        self.sample_rate = sample_rate
        self.feature_dimension = len(features)
    
    def get_features(self) -> tuple:
        """反序列化获取声纹特征"""
        if not self.features:
            return None, None
        
        try:
            feature_data = json.loads(self.features.decode('utf-8'))
            return feature_data['features'], feature_data['sample_rate']
        except (json.JSONDecodeError, KeyError):
            return None, None


class VoiceVerificationLog(Base):
    __tablename__ = "voice_verification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    verification_result = Column(Integer)  # 0: 失败, 1: 成功
    similarity_score = Column(Integer)  # 相似度分数 (0-100)
    audio_duration = Column(Integer)  # 音频时长(毫秒)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))