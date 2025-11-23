"""
数据库模型定义

定义agents系统使用的数据库表结构
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base


class Conversation(Base):
    """对话记录表"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    agent_type = Column(String(100), nullable=False)
    user_input = Column(Text, nullable=False)
    agent_response = Column(Text, nullable=False)  # JSON格式存储
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserProfile(Base):
    """用户画像表"""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    profile_data = Column(Text, nullable=False)  # JSON格式存储
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SessionMemory(Base):
    """会话记忆表"""
    __tablename__ = "session_memories"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    memory_data = Column(Text, nullable=False)  # JSON格式存储
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())