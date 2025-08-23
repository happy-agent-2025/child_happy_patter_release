from db.database import engine, Base
from models.user import User, Conversation, SecurityLog
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """
    初始化数据库，创建所有表
    """
    try:
        # 导入所有模型后创建表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
        return True
    except Exception as e:
        logger.error(f"创建数据库表时出错: {e}")
        return False


if __name__ == "__main__":
    success = init_db()
    if success:
        print("数据库初始化成功")
    else:
        print("数据库初始化失败")