import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.database import Base
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
        settings.database_url,
        echo=settings.DEBUG if hasattr(settings, 'DEBUG') else False,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialization completed, all tables created")

if __name__ == "__main__":
    init_db()