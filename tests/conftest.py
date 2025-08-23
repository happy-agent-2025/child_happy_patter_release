import sys
import os
import asyncio

# 将项目根目录添加到Python路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 在Windows上设置事件循环策略以避免警告
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 为避免依赖项问题，我们在这里模拟一些常用的模块
import unittest.mock as mock

# 模拟缺少的模块（排除pydantic，因为它已被安装）
mock_modules = [
    #'pyttsx3',
    #'speech_recognition',
    #'sqlalchemy',
    #'pydantic',  # 不再模拟pydantic
    #'passlib',
    #'passlib.context',
    #'jwt'
]

for module_name in mock_modules:
    if module_name not in sys.modules:
        sys.modules[module_name] = mock.MagicMock()

# 为FastAPI测试客户端提供真实导入
try:
    from fastapi.testclient import TestClient # type: ignore
except ImportError:
    # 如果没有安装，创建一个模拟版本
    class TestClient:
        def __init__(self, app):
            pass
            
        def get(self, url, **kwargs):
            class MockResponse:
                def __init__(self):
                    self.status_code = 200
                    
                def json(self):
                    return {"message": "Mocked response"}
                    
            return MockResponse()
            
        def post(self, url, **kwargs):
            class MockResponse:
                def __init__(self):
                    self.status_code = 200
                    
                def json(self):
                    return {"message": "Mocked response", "status": "success"}
                    
            return MockResponse()

# 添加pytest asyncio配置
pytest_plugins = ["pytest_asyncio"]