from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ChatRequest(BaseModel):
    """聊天请求模型"""
    content: str = Field(..., description="用户输入的聊天内容", example="你好，今天天气怎么样？")
    user_id: Optional[int] = Field(1, description="用户ID，默认为1", example=1)
    session_id: Optional[int] = Field(None, description="会话ID，可选", example=123)
    

class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str = Field(..., description="AI代理的回复内容", example="今天天气很好，适合户外活动！")
    agent_type: str = Field(..., description="处理请求的代理类型", example="edu")
    confidence: Optional[float] = Field(None, description="置信度分数", example=0.95)
    timestamp: datetime = Field(..., description="响应时间")


class SafetyCheckRequest(BaseModel):
    """安全检查请求模型"""
    content: str = Field(..., description="需要检查的内容", example="一些不合适的内容")
    user_id: Optional[int] = Field(1, description="用户ID", example=1)


class SafetyCheckResponse(BaseModel):
    """安全检查响应模型"""
    is_safe: bool = Field(..., description="内容是否安全", example=True)
    reason: Optional[str] = Field(None, description="不安全的原因", example="包含敏感词汇")
    confidence: float = Field(..., description="安全检查置信度", example=0.98)
    suggested_content: Optional[str] = Field(None, description="建议的替代内容")


class EduQuestionRequest(BaseModel):
    """教育问答请求模型"""
    question: str = Field(..., description="教育相关问题", example="什么是光合作用？")
    user_id: Optional[int] = Field(1, description="用户ID", example=1)
    grade_level: Optional[str] = Field(None, description="年级水平", example="小学三年级")


class EduQuestionResponse(BaseModel):
    """教育问答响应模型"""
    answer: str = Field(..., description="问题答案", example="光合作用是植物利用阳光、水和二氧化碳制造食物的过程。")
    explanation: Optional[str] = Field(None, description="详细解释")
    related_topics: Optional[List[str]] = Field(None, description="相关主题")
    difficulty_level: Optional[str] = Field(None, description="难度级别", example="简单")


class EmotionSupportRequest(BaseModel):
    """情感支持请求模型"""
    content: str = Field(..., description="情感表达内容", example="我今天感到有点难过")
    user_id: Optional[int] = Field(1, description="用户ID", example=1)
    emotion_type: Optional[str] = Field(None, description="情感类型", example="sadness")


class EmotionSupportResponse(BaseModel):
    """情感支持响应模型"""
    response: str = Field(..., description="情感支持回复", example="我理解你的感受，每个人都会有难过的时候。")
    support_type: str = Field(..., description="支持类型", example="comfort")
    suggested_activities: Optional[List[str]] = Field(None, description="建议的活动")
    follow_up_questions: Optional[List[str]] = Field(None, description="跟进问题")