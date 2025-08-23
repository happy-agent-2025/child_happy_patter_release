from sqlalchemy.orm import Session
from models.user import User, Session as UserSession, Conversation, SecurityLog
from typing import List, Optional
import logging

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
        创建对话记录
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            user_input: 用户输入
            agent_response: 代理回复
            agent_type: 代理类型
            session_id: 会话ID（可选）
            
        Returns:
            创建的对话对象
        """
        db_conversation = Conversation(
            user_id=user_id,
            session_id=session_id,
            user_input=user_input,
            agent_response=agent_response,
            agent_type=agent_type
        )
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        logger.info(f"创建对话记录: 用户{user_id}与{agent_type}代理")
        return db_conversation
    
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