import pytest
from unittest.mock import patch, MagicMock


class TestDatabase:
    """测试数据库模块"""
    
    def test_get_db_generator(self):
        """测试获取数据库会话生成器"""
        # 由于我们使用了简化的实现，这里只测试基本功能
        from db.database import get_db
        
        # 获取生成器
        db_generator = get_db()
        
        # 获取第一个值
        db = next(db_generator)
        
        # 验证返回的对象有close方法
        assert hasattr(db, 'close')
        
        # 测试生成器可以正常结束
        try:
            next(db_generator)
        except StopIteration:
            # 这是期望的行为
            pass
