import sys
import os
import asyncio

# 将项目根目录添加到Python路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 在Windows上设置事件循环策略以避免警告
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 直接导入FastAPI测试客户端
from fastapi.testclient import TestClient

# 添加pytest asyncio配置
pytest_plugins = ["pytest_asyncio"]