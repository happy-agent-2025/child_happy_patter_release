import sys
import os

# 将项目根目录添加到Python路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 为避免依赖项问题，我们在这里模拟一些常用的模块
import unittest.mock as mock
import sys

# 模拟缺少的模块
mock_modules = [
    'pyttsx3',
    'speech_recognition',
    'sqlalchemy',
    'pydantic',
    'passlib',
    'passlib.context',
    'jwt'
]

for module_name in mock_modules:
    if module_name not in sys.modules:
        sys.modules[module_name] = mock.MagicMock()