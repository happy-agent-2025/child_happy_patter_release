import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.db.database import Base
from config.settings import Settings
# 确保所有模型都被导入，这样Base.metadata.create_all才能创建所有表
from models.user import User, Session, Conversation, ArchivedConversation, SecurityLog
from models.voiceprint import Voiceprint
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """
    初始化数据库，创建所有表
    """
    try:
        settings = Settings()
        
        # 创建数据库引擎
        engine = create_engine(
            settings.database_url,
            echo=settings.DEBUG if hasattr(settings, 'DEBUG') else False, # type: ignore
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialization completed, all tables created")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = init_db()
    if success:
        print("数据库初始化成功")
    else:
        print("数据库初始化失败")