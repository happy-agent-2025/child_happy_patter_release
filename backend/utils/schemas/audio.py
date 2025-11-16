from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class AudioTranscribeRequest(BaseModel):
    """语音转文本请求模型"""
    audio_data: str = Field(..., description="Base64编码的音频数据", json_schema_extra={"example": "base64 encoded audio data"})
    preprocess: bool = Field(True, description="是否进行音频预处理", json_schema_extra={"example": True})
    language: Optional[str] = Field("zh-CN", description="语言代码", json_schema_extra={"example": "zh-CN"})


class AudioTranscribeResponse(BaseModel):
    """语音转文本响应模型"""
    text: str = Field(..., description="转录的文本内容", json_schema_extra={"example": "你好，今天天气很好"})
    confidence: float = Field(..., description="转录置信度", json_schema_extra={"example": 0.92})
    duration: float = Field(..., description="音频时长（秒）", json_schema_extra={"example": 3.5})
    language: str = Field(..., description="检测到的语言", json_schema_extra={"example": "zh-CN"})


class AudioSynthesizeRequest(BaseModel):
    """文本转语音请求模型"""
    text: str = Field(..., description="要合成的文本", json_schema_extra={"example": "你好，欢迎使用我们的系统"})
    voice_type: Optional[str] = Field("female", description="语音类型", json_schema_extra={"example": "female"})
    speed: Optional[float] = Field(1.0, description="语速（0.5-2.0）", json_schema_extra={"example": 1.0})
    volume: Optional[float] = Field(1.0, description="音量（0.0-1.0）", json_schema_extra={"example": 1.0})


class AudioSynthesizeResponse(BaseModel):
    """文本转语音响应模型"""
    audio_data: str = Field(..., description="Base64编码的音频数据", json_schema_extra={"example": "base64 encoded audio data"})
    duration: float = Field(..., description="生成的音频时长（秒）", json_schema_extra={"example": 2.8})
    format: str = Field(..., description="音频格式", json_schema_extra={"example": "wav"})
    sample_rate: int = Field(..., description="采样率", json_schema_extra={"example": 16000})


class AudioProcessRequest(BaseModel):
    """音频处理请求模型"""
    audio_data: str = Field(..., description="Base64编码的音频数据", json_schema_extra={"example": "base64 encoded audio data"})
    target_rate: Optional[int] = Field(16000, description="目标采样率", json_schema_extra={"example": 16000})
    target_rms: Optional[float] = Field(0.1, description="目标RMS值", json_schema_extra={"example": 0.1})
    silence_threshold: Optional[float] = Field(0.01, description="静音阈值", json_schema_extra={"example": 0.01})


class AudioProcessResponse(BaseModel):
    """音频处理响应模型"""
    processed_audio: str = Field(..., description="处理后的Base64音频数据", json_schema_extra={"example": "base64 encoded audio data"})
    original_duration: float = Field(..., description="原始音频时长（秒）", json_schema_extra={"example": 5.2})
    processed_duration: float = Field(..., description="处理后的音频时长（秒）", json_schema_extra={"example": 3.8})
    sample_rate: int = Field(..., description="处理后的采样率", json_schema_extra={"example": 16000})
    processing_steps: List[str] = Field(..., description="处理步骤", json_schema_extra={"example": ["silence_removal", "normalization", "resampling"]})


class VoiceRegisterRequest(BaseModel):
    """声纹注册请求模型"""
    user_id: int = Field(..., description="用户ID", json_schema_extra={"example": 1})
    audio_data: str = Field(..., description="Base64编码的音频数据", json_schema_extra={"example": "base64 encoded audio data"})
    sample_rate: int = Field(..., description="音频采样率", json_schema_extra={"example": 16000})
    audio_duration: Optional[int] = Field(None, description="音频时长（毫秒）", json_schema_extra={"example": 3000})


class VoiceRegisterResponse(BaseModel):
    """声纹注册响应模型"""
    success: bool = Field(..., description="注册是否成功", json_schema_extra={"example": True})
    user_id: int = Field(..., description="用户ID", json_schema_extra={"example": 1})
    feature_dimension: int = Field(..., description="声纹特征维度", json_schema_extra={"example": 20})
    message: Optional[str] = Field(None, description="额外信息")


class VoiceVerifyRequest(BaseModel):
    """声纹验证请求模型"""
    user_id: int = Field(..., description="用户ID", json_schema_extra={"example": 1})
    audio_data: str = Field(..., description="Base64编码的音频数据", json_schema_extra={"example": "base64 encoded audio data"})
    sample_rate: int = Field(..., description="音频采样率", json_schema_extra={"example": 16000})
    threshold: Optional[float] = Field(0.8, description="验证阈值", json_schema_extra={"example": 0.8})
    audio_duration: Optional[int] = Field(None, description="音频时长（毫秒）", json_schema_extra={"example": 2500})


class VoiceVerifyResponse(BaseModel):
    """声纹验证响应模型"""
    verified: bool = Field(..., description="验证是否通过", json_schema_extra={"example": True})
    similarity: float = Field(..., description="相似度分数", json_schema_extra={"example": 0.92})
    user_id: int = Field(..., description="用户ID", json_schema_extra={"example": 1})
    threshold: float = Field(..., description="使用的阈值", json_schema_extra={"example": 0.8})
    confidence: Optional[float] = Field(None, description="置信度", json_schema_extra={"example": 0.95})