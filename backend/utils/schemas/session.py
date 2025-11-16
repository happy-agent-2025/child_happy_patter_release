"""
会话管理相关的 Pydantic 模型
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class SessionCreateRequest(BaseModel):
    """创建会话请求模型"""
    user_id: int
    title: Optional[str] = None


class SessionResponse(BaseModel):
    """会话响应模型"""
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

class SessionUpdateRequest(BaseModel):
    """更新会话请求模型"""
    title: Optional[str] = None
    is_active: Optional[bool] = None