"""
数据库连接和会话管理

提供数据库连接池和会话管理功能
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库连接配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./agents.db"  # 使用SQLite数据库

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite需要这个参数
    echo=False  # 设置为True可以查看SQL语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """创建数据库表"""
    # 导入模型以确保表被创建
    from . import models
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """删除数据库表"""
    Base.metadata.drop_all(bind=engine)