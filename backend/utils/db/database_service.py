from sqlalchemy.orm import Session
from sqlalchemy import and_, text
from models.user import User, Session as UserSession, Conversation, ArchivedConversation, SecurityLog
from typing import List, Optional
from datetime import datetime, timedelta, timezone
import logging
import hashlib
import json
import zlib

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseService:
    """
    数据库服务类，提供对用户、对话和安全日志的CRUD操作
    """
    
    @staticmethod
    def create_user(db: Session, username: str, email: str, hashed_password: str) -> User:
        """
        创建新用户
        
        Args:
            db: 数据库会话
            username: 用户名
            email: 邮箱
            hashed_password: 加密后的密码
            
        Returns:
            创建的用户对象
        """
        db_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"创建新用户: {username}")
        return db_user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        根据用户ID获取用户
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            用户对象或None
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        
        Args:
            db: 数据库会话
            username: 用户名
            
        Returns:
            用户对象或None
        """
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        
        Args:
            db: 数据库会话
            email: 邮箱
            
        Returns:
            用户对象或None
        """
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_session(db: Session, user_id: int, title: str) -> UserSession:
        """
        创建新会话
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            title: 会话标题
            
        Returns:
            创建的会话对象
        """
        db_session = UserSession(
            user_id=user_id,
            title=title
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        logger.info(f"创建新会话: 用户{user_id}的会话{db_session.id}")
        return db_session
    
    @staticmethod
    def get_active_sessions_by_user_id(db: Session, user_id: int) -> List[UserSession]:
        """
        获取用户的所有活跃会话
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            活跃会话列表
        """
        return db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == 1
        ).all()
    
    @staticmethod
    def get_session_by_id(db: Session, session_id: int, include_inactive: bool = False) -> Optional[UserSession]:
        """
        根据ID获取会话
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            include_inactive: 是否包含非活跃会话
            
        Returns:
            会话对象或None
        """
        query = db.query(UserSession).filter(UserSession.id == session_id)
        if not include_inactive:
            query = query.filter(UserSession.is_active == 1)
        return query.first()
    
    @staticmethod
    def get_sessions_by_user_id(db: Session, user_id: int, limit: int = 10) -> List[UserSession]:
        """
        根据用户ID获取会话列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            limit: 返回的会话数量限制
            
        Returns:
            会话对象列表
        """
        return db.query(UserSession)\
                 .filter(UserSession.user_id == user_id)\
                 .filter(UserSession.is_active == 1)\
                 .order_by(UserSession.created_at.desc())\
                 .limit(limit)\
                 .all()
    
    @staticmethod
    def delete_session(db: Session, session_id: int) -> bool:
        """
        删除会话（标记为非活跃）
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            
        Returns:
            是否成功
        """
        session = db.query(UserSession).filter(UserSession.id == session_id).first()
        if session:
            session.is_active = 0 # type: ignore
            db.commit()
            logger.info(f"删除会话: 会话{session_id}已标记为非活跃")
            return True
        return False
    
    @staticmethod
    def create_conversation(
        db: Session, 
        user_id: int, 
        user_input: str, 
        agent_response: str, 
        agent_type: str,
        session_id: Optional[int] = None
    ) -> Conversation:
        """
        创建或更新对话记录
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            user_input: 用户输入
            agent_response: 代理回复
            agent_type: 代理类型
            session_id: 会话ID（可选）
            
        Returns:
            创建或更新的对话对象
            
        注意事项:
            1. 如果存在相同用户ID和代理类型的对话记录，则追加到该记录中
            2. 如果不存在相同用户ID和代理类型的对话记录，则创建新记录
            3. 每个用户与每个代理类型的所有对话历史都保存在同一个记录中
        """
        # 查找相同用户ID和代理类型的现有对话记录
        existing_conversation = db.query(Conversation).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.agent_type == agent_type
            )
        ).first()
        
        # 如果存在相同用户ID和代理类型的记录，则追加对话历史
        if existing_conversation:
            # 获取现有的对话历史
            conversation_history = existing_conversation.conversation_history or []
            # 添加新的对话
            conversation_history.append({
                "user_input": user_input,
                "agent_response": agent_response,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            # 更新对话历史
            existing_conversation.conversation_history = conversation_history # type: ignore
            existing_conversation.updated_at = datetime.now(timezone.utc) # type: ignore
            db.commit()
            db.refresh(existing_conversation)
            logger.info(f"更新对话记录: 用户{user_id}与{agent_type}代理的对话")
            return existing_conversation
        
        # 如果不存在相同用户ID和代理类型的记录，则创建新记录
        # 创建新的对话历史
        conversation_history = [{
            "user_input": user_input,
            "agent_response": agent_response,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }]
        
        logger.info(f"创建新的对话历史：{conversation_history}")
        
        db_conversation = Conversation(
            user_id=user_id,
            session_id=session_id,
            conversation_history=conversation_history,
            agent_type=agent_type
        )
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        logger.info(f"创建对话记录: 用户{user_id}与{agent_type}代理")
        return db_conversation
    
    @staticmethod
    def _compress_text(text: str) -> bytes:
        """
        压缩文本数据
        
        Args:
            text: 要压缩的文本
            
        Returns:
            压缩后的字节数据
        """
        return zlib.compress(text.encode('utf-8'))
    
    @staticmethod
    def _decompress_text(data: bytes) -> str:
        """
        解压缩文本数据
        
        Args:
            data: 压缩的字节数据
            
        Returns:
            解压后的文本
        """
        return zlib.decompress(data).decode('utf-8')
    
    @staticmethod
    def _compress_json(data: List[dict]) -> bytes:
        """
        压缩JSON数据
        
        Args:
            data: 要压缩的JSON数据
            
        Returns:
            压缩后的字节数据
        """
        json_str = json.dumps(data, ensure_ascii=False)
        return zlib.compress(json_str.encode('utf-8'))
    
    @staticmethod
    def _decompress_json(data: bytes) -> List[dict]:
        """
        解压缩JSON数据
        
        Args:
            data: 压缩的字节数据
            
        Returns:
            解压后的JSON数据
        """
        json_str = zlib.decompress(data).decode('utf-8')
        return json.loads(json_str)
    
    @staticmethod
    def archive_old_conversations(db: Session, days_old: int = 30) -> int:
        """
        归档指定天数之前的对话记录
        
        Args:
            db: 数据库会话
            days_old: 归档多少天之前的记录，默认30天
            
        Returns:
            归档的记录数量
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # 查询需要归档的记录
        old_conversations = db.query(Conversation).filter(
            Conversation.created_at < cutoff_date
        ).all()
        
        count = len(old_conversations)
        
        # 如果有需要归档的记录，则进行归档和压缩
        if count > 0:
            # 将记录移动到归档表中，并进行压缩
            for conversation in old_conversations:
                # 创建归档记录，压缩conversation_history字段
                archived_conversation = ArchivedConversation(
                    user_id=conversation.user_id,
                    session_id=conversation.session_id,
                    conversation_history=DatabaseService._compress_json(conversation.conversation_history), # type: ignore
                    agent_type=conversation.agent_type,
                    created_at=conversation.created_at
                )
                db.add(archived_conversation)
            
            # 提交归档记录
            db.commit()
            
            # 从主表中删除已归档的记录
            db.query(Conversation).filter(
                Conversation.created_at < cutoff_date
            ).delete()
            db.commit()
            
            logger.info(f"已归档并压缩{count}条{days_old}天之前的对话记录")
        
        return count
    
    @staticmethod
    def delete_old_conversations(db: Session, days_old: int = 365) -> int:
        """
        删除指定天数之前的对话记录
        
        Args:
            db: 数据库会话
            days_old: 删除多少天之前的记录，默认365天
            
        Returns:
            删除的记录数量
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # 查询并删除旧记录
        old_conversations = db.query(Conversation).filter(
            Conversation.created_at < cutoff_date
        )
        count = old_conversations.count()
        old_conversations.delete()
        db.commit()
        
        logger.info(f"删除了{count}条{days_old}天之前的对话记录")
        return count
    
    @staticmethod
    def get_conversation_history(db: Session, session_id: int) -> Optional[Conversation]:
        """
        获取指定会话的完整对话历史
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            
        Returns:
            包含完整对话历史的对话对象，如果不存在则返回None
        """
        return db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()
    
    @staticmethod
    def get_conversations_by_user_id(db: Session, user_id: int, limit: int = 10) -> List[Conversation]:
        """
        根据用户ID获取对话历史
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            limit: 限制返回记录数
            
        Returns:
            对话记录列表
        """
        return db.query(Conversation).filter(Conversation.user_id == user_id).order_by(
            Conversation.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_conversations_by_session_id(db: Session, session_id: int) -> List[Conversation]:
        """
        根据会话ID获取对话历史
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            
        Returns:
            对话记录列表
        """
        return db.query(Conversation).filter(Conversation.session_id == session_id).order_by(
            Conversation.created_at.asc()).all()
    
    @staticmethod
    def get_conversation_by_user_and_agent(db: Session, user_id: int, agent_type: str) -> Optional[Conversation]:
        """
        根据用户ID和代理类型获取对话记录
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            agent_type: 代理类型
            
        Returns:
            包含完整对话历史的对话对象，如果不存在则返回None
        """
        return db.query(Conversation).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.agent_type == agent_type
            )
        ).first()
    
    @staticmethod
    def get_recent_conversations_by_user(db: Session, user_id: int, limit: int = 10) -> List[Conversation]:
        """
        根据用户ID获取最近的对话记录
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            limit: 限制返回记录数
            
        Returns:
            对话记录列表，按创建时间倒序排列
        """
        return db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_conversations_by_session(db: Session, session_id: int) -> List[Conversation]:
        """
        根据会话ID获取对话记录
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            
        Returns:
            对话记录列表，按创建时间正序排列
        """
        return db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).order_by(Conversation.created_at.asc()).all()
    
    @staticmethod
    def create_security_log(
        db: Session,
        user_id: int,
        content: str,
        is_safe: bool,
        filtered_content: str
    ) -> SecurityLog:
        """
        创建安全日志记录
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            content: 原始内容
            is_safe: 是否安全
            filtered_content: 过滤后的内容
            
        Returns:
            创建的安全日志对象
        """
        db_security_log = SecurityLog(
            user_id=user_id,
            content=content,
            is_safe=1 if is_safe else 0,
            filtered_content=filtered_content
        )
        db.add(db_security_log)
        db.commit()
        db.refresh(db_security_log)
        logger.info(f"创建安全日志: 用户{user_id}, 内容安全: {is_safe}")
        return db_security_log
    
    @staticmethod
    def get_security_logs_by_user_id(db: Session, user_id: int, limit: int = 10) -> List[SecurityLog]:
        """
        根据用户ID获取安全日志
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            limit: 限制返回记录数
            
        Returns:
            安全日志列表
        """
        return db.query(SecurityLog).filter(SecurityLog.user_id == user_id).order_by(
            SecurityLog.created_at.desc()).limit(limit).all()