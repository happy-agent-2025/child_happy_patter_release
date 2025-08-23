from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.user import Base
from config.settings import Settings
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """
    初始化数据库，创建所有表
    """
    settings = Settings()
    
    # 创建数据库引擎
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    logger.info("数据库初始化完成，所有表已创建")

if __name__ == "__main__":
    init_db()