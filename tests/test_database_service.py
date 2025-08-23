import pytest
import sys
import os
from unittest.mock import MagicMock

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database_service import DatabaseService
from models.user import User, Conversation, SecurityLog


class TestDatabaseService:
    """测试数据库服务模块"""

    def test_create_user(self):
        """测试创建用户功能"""
        # 创建模拟的数据库会话
        mock_db = MagicMock()
        mock_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # 调用方法
        result = DatabaseService.create_user(
            mock_db, 
            "testuser", 
            "test@example.com", 
            "hashed_password"
        )
        
        # 验证结果
        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_get_user_by_id(self):
        """测试根据ID获取用户功能"""
        # 创建模拟的数据库会话和查询
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        
        # 调用方法
        result = DatabaseService.get_user_by_id(mock_db, 1)
        
        # 验证结果
        assert result is not None
        assert result.id == 1 # type: ignore
        assert result.username == "testuser" # type: ignore
        mock_db.query.assert_called_once_with(User)
        mock_query.filter.assert_called_once()
        mock_query.first.assert_called_once()

    def test_create_conversation(self):
        """测试创建对话记录功能"""
        # 创建模拟的数据库会话
        mock_db = MagicMock()
        mock_conversation = Conversation(
            id=1,
            user_id=1,
            user_input="Hello",
            agent_response="Hi there!",
            agent_type="edu"
        )
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # 调用方法
        result = DatabaseService.create_conversation(
            mock_db,
            1,
            "Hello",
            "Hi there!",
            "edu"
        )
        
        # 验证结果
        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_create_security_log(self):
        """测试创建安全日志功能"""
        # 创建模拟的数据库会话
        mock_db = MagicMock()
        mock_security_log = SecurityLog(
            id=1,
            user_id=1,
            content="Test content",
            is_safe=1,
            filtered_content="Filtered content"
        )
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # 调用方法
        result = DatabaseService.create_security_log(
            mock_db,
            1,
            "Test content",
            True,
            "Filtered content"
        )
        
        # 验证结果
        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()