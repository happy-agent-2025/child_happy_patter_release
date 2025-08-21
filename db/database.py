# 简化处理以避免导入问题
try:
    from sqlalchemy import create_engine
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    import os

    # 获取数据库URL
    database_url = os.environ.get("DATABASE_URL", "sqlite:///./happy_partner.db")

    # 创建数据库引擎
    engine = create_engine(database_url, connect_args={"check_same_thread": False})

    # 创建数据库会话
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # 创建基础模型类
    Base = declarative_base()

    def get_db(): # type: ignore
        """
        获取数据库会话
        """
        db = SessionLocal() # type: ignore
        try:
            yield db
        finally:
            db.close()

except ImportError:
    # 如果SQLAlchemy不可用，提供简化版本用于测试
    Base = object
    engine = None
    SessionLocal = None
    
    def get_db():
        """
        简化的数据库会话生成器（用于测试）
        """
        class MockDB:
            def close(self):
                pass
                
        db = MockDB()
        try:
            yield db
        finally:
            pass