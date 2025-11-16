# 简化处理以避免导入问题
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import declarative_base, sessionmaker
    import os

    from config.settings import settings

    # 获取数据库URL
    DATABASE_URL = settings.database_url

    # 创建数据库引擎
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

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