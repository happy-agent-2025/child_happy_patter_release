from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, LargeBinary, JSON
from datetime import datetime, timezone
from utils.db.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    title = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active = Column(Integer, default=1)  # 1为活跃，0为已删除


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), index=True, nullable=True)
    # 使用JSON类型存储对话历史
    conversation_history = Column(JSON, default=list)
    agent_type = Column(String)
    user_input = Column(Text)
    agent_response = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ArchivedConversation(Base):
    __tablename__ = "archived_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    session_id = Column(Integer, index=True, nullable=True)
    conversation_history = Column(LargeBinary)  # 压缩存储对话历史
    agent_type = Column(String)
    created_at = Column(DateTime)
    archived_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SecurityLog(Base):
    __tablename__ = "security_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    content = Column(Text)
    is_safe = Column(Integer)  # 0 for unsafe, 1 for safe
    filtered_content = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))