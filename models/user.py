# 简化导入以避免相对导入问题
try:
    from sqlalchemy import Column, Integer, String, DateTime
    from datetime import datetime

    # 简化Base处理
    Base = object

    class User(Base):
        __tablename__ = "users"
        
        id = Column(Integer, primary_key=True, index=True)
        username = Column(String, unique=True, index=True)
        email = Column(String, unique=True, index=True)
        hashed_password = Column(String)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
except ImportError:
    # 如果SQLAlchemy不可用，提供一个简化版本用于测试
    from datetime import datetime

    class User:
        def __init__(self, **kwargs):
            self.id = kwargs.get('id')
            self.username = kwargs.get('username')
            self.email = kwargs.get('email')
            self.hashed_password = kwargs.get('hashed_password')
            self.created_at = kwargs.get('created_at', datetime.utcnow())
            self.updated_at = kwargs.get('updated_at', datetime.utcnow())
            self.__tablename__ = "users"