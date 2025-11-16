from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class MemoryActionRequest(BaseModel):
    """记忆操作请求模型"""
    action: str = Field(..., description="操作类型: store|retrieve|delete", json_schema_extra={"example": "store"})
    user_id: Optional[int] = Field(1, description="用户ID", json_schema_extra={"example": 1})
    session_id: Optional[int] = Field(None, description="会话ID", json_schema_extra={"example": 123})
    content: Optional[str] = Field(None, description="记忆内容", json_schema_extra={"example": "用户喜欢数学"})
    memory_key: Optional[str] = Field(None, description="记忆键名", json_schema_extra={"example": "user_preferences"})
    memory_type: Optional[str] = Field(None, description="记忆类型", json_schema_extra={"example": "preference"})


class MemoryActionResponse(BaseModel):
    """记忆操作响应模型"""
    success: bool = Field(..., description="操作是否成功", json_schema_extra={"example": True})
    action: str = Field(..., description="执行的操作类型", json_schema_extra={"example": "store"})
    memory_data: Optional[Dict[str, Any]] = Field(None, description="记忆数据")
    message: Optional[str] = Field(None, description="操作结果消息")
    timestamp: datetime = Field(..., description="操作时间")


class ConversationHistoryResponse(BaseModel):
    """对话历史响应模型"""
    user_id: int = Field(..., description="用户ID", json_schema_extra={"example": 1})
    conversations: List[Dict[str, Any]] = Field(..., description="对话历史列表")
    total_count: int = Field(..., description="总对话数量", json_schema_extra={"example": 15})
    page: int = Field(..., description="当前页码", json_schema_extra={"example": 1})
    page_size: int = Field(..., description="每页数量", json_schema_extra={"example": 10})


class SecurityLogResponse(BaseModel):
    """安全日志响应模型"""
    user_id: int = Field(..., description="用户ID", json_schema_extra={"example": 1})
    logs: List[Dict[str, Any]] = Field(..., description="安全日志列表")
    total_count: int = Field(..., description="总日志数量", json_schema_extra={"example": 8})
    page: int = Field(..., description="当前页码", json_schema_extra={"example": 1})
    page_size: int = Field(..., description="每页数量", json_schema_extra={"example": 10})


class ConversationItem(BaseModel):
    """对话项模型"""
    id: int = Field(..., description="对话ID", json_schema_extra={"example": 1})
    user_id: int = Field(..., description="用户ID", json_schema_extra={"example": 1})
    session_id: Optional[int] = Field(None, description="会话ID", json_schema_extra={"example": 123})
    agent_type: str = Field(..., description="代理类型", json_schema_extra={"example": "edu"})
    conversation_history: str = Field(..., description="对话历史JSON")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ConversationListResponse(BaseModel):
    """对话列表响应模型"""
    user_id: int = Field(..., description="用户ID", json_schema_extra={"example": 1})
    conversations: List[ConversationItem] = Field(..., description="对话列表")


class SecurityLogItem(BaseModel):
    """安全日志项模型"""
    id: int = Field(..., description="日志ID", json_schema_extra={"example": 1})
    content: str = Field(..., description="日志内容")
    is_safe: bool = Field(..., description="是否安全", json_schema_extra={"example": True})
    filtered_content: Optional[str] = Field(None, description="过滤后的内容")
    created_at: datetime = Field(..., description="创建时间")


class SecurityLogListResponse(BaseModel):
    """安全日志列表响应模型"""
    user_id: int = Field(..., description="用户ID", json_schema_extra={"example": 1})
    security_logs: List[SecurityLogItem] = Field(..., description="安全日志列表")