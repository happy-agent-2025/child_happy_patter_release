"""
数据库服务

提供agents系统使用的数据库操作服务
"""

from sqlalchemy.orm import Session
from .models import Conversation, UserProfile, SessionMemory
import json


class DatabaseService:
    """数据库服务类"""

    @staticmethod
    def create_conversation(
        db: Session,
        user_id: int,
        session_id: str,
        agent_type: str,
        user_input: str,
        agent_response: str
    ) -> Conversation:
        """
        创建对话记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            session_id: 会话ID
            agent_type: Agent类型
            user_input: 用户输入
            agent_response: Agent响应（JSON格式）

        Returns:
            Conversation: 创建的对话记录
        """
        conversation = Conversation(
            user_id=user_id,
            session_id=session_id,
            agent_type=agent_type,
            user_input=user_input,
            agent_response=agent_response
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return conversation

    @staticmethod
    def update_user_profile(
        db: Session,
        user_id: int,
        profile_data: str
    ) -> UserProfile:
        """
        更新用户画像

        Args:
            db: 数据库会话
            user_id: 用户ID
            profile_data: 用户画像数据（JSON格式）

        Returns:
            UserProfile: 更新后的用户画像
        """
        # 检查用户画像是否存在
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

        if profile:
            # 更新现有用户画像
            profile.profile_data = profile_data
        else:
            # 创建新的用户画像
            profile = UserProfile(
                user_id=user_id,
                profile_data=profile_data
            )
            db.add(profile)

        db.commit()
        db.refresh(profile)

        return profile

    @staticmethod
    def get_user_profile(db: Session, user_id: int) -> UserProfile:
        """
        获取用户画像

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            UserProfile: 用户画像，如果不存在则返回None
        """
        return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    @staticmethod
    def update_session_memory(
        db: Session,
        session_id: str,
        memory_data: str
    ) -> SessionMemory:
        """
        更新会话记忆

        Args:
            db: 数据库会话
            session_id: 会话ID
            memory_data: 会话记忆数据（JSON格式）

        Returns:
            SessionMemory: 更新后的会话记忆
        """
        # 检查会话记忆是否存在
        memory = db.query(SessionMemory).filter(SessionMemory.session_id == session_id).first()

        if memory:
            # 更新现有会话记忆
            memory.memory_data = memory_data
        else:
            # 创建新的会话记忆
            memory = SessionMemory(
                session_id=session_id,
                memory_data=memory_data
            )
            db.add(memory)

        db.commit()
        db.refresh(memory)

        return memory

    @staticmethod
    def get_session_memory(db: Session, session_id: str) -> SessionMemory:
        """
        获取会话记忆

        Args:
            db: 数据库会话
            session_id: 会话ID

        Returns:
            SessionMemory: 会话记忆，如果不存在则返回None
        """
        return db.query(SessionMemory).filter(SessionMemory.session_id == session_id).first()

    @staticmethod
    def get_conversation_history(
        db: Session,
        user_id: int,
        limit: int = 10
    ) -> list[Conversation]:
        """
        获取用户对话历史

        Args:
            db: 数据库会话
            user_id: 用户ID
            limit: 返回记录数量限制

        Returns:
            list[Conversation]: 对话历史列表
        """
        return (
            db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_session_conversations(
        db: Session,
        session_id: str
    ) -> list[Conversation]:
        """
        获取会话对话记录

        Args:
            db: 数据库会话
            session_id: 会话ID

        Returns:
            list[Conversation]: 会话对话记录列表
        """
        return (
            db.query(Conversation)
            .filter(Conversation.session_id == session_id)
            .order_by(Conversation.created_at.asc())
            .all()
        )