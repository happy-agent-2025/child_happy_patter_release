import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from models.user import User, Conversation, ArchivedConversation, SecurityLog
from db.database_service import DatabaseService
from datetime import datetime, timedelta
import zlib


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
        assert result.id == 1
        assert result.username == "testuser"
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

    def test_create_conversation_always_append(self):
        """测试创建对话记录功能 - 始终追加新记录"""
        # 创建模拟的数据库会话
        mock_db = MagicMock()
        mock_conversation = Conversation(
            id=2,  # 新的ID
            user_id=1,
            user_input="Hello",
            agent_response="Hi there again!",
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
            "Hi there again!",
            "edu"
        )

        # 验证结果 - 应该总是调用add方法创建新记录
        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_create_conversation_with_same_user_and_session(self):
        """测试相同用户和会话ID的对话存储"""
        # 创建模拟的数据库会话
        mock_db = MagicMock()
        mock_conversation1 = Conversation(
            id=1,
            user_id=1,
            session_id=100,
            user_input="Hello",
            agent_response="Hi there!",
            agent_type="edu"
        )
        mock_conversation2 = Conversation(
            id=2,  # 不同的ID
            user_id=1,  # 相同的用户ID
            session_id=100,  # 相同的会话ID
            user_input="How are you?",
            agent_response="I'm fine, thanks!",
            agent_type="edu"
        )
        
        # 设置模拟对象的返回值
        mock_db.add.side_effect = lambda x: setattr(x, 'id', 1 if x.user_input == "Hello" else 2)
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        # 创建第一条对话
        result1 = DatabaseService.create_conversation(
            mock_db,
            1,  # user_id
            "Hello",
            "Hi there!",
            "edu",
            100  # session_id
        )

        # 创建第二条对话
        result2 = DatabaseService.create_conversation(
            mock_db,
            1,  # 相同的user_id
            "How are you?",
            "I'm fine, thanks!",
            "edu",
            100  # 相同的session_id
        )

        # 验证结果 - 应该创建两条独立的记录
        assert result1 is not None
        assert result2 is not None
        assert result1.id != result2.id  # 确保是不同的记录
        assert mock_db.add.call_count == 2  # 确保调用了两次add方法
        assert mock_db.commit.call_count == 2  # 确保调用了两次commit方法
        assert mock_db.refresh.call_count == 2  # 确保调用了两次refresh方法

    def test_database_resource_usage(self):
        """测试数据库资源使用情况"""
        # 创建模拟的数据库会话
        mock_db = MagicMock()
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        # 模拟多次创建对话记录
        for i in range(10):
            DatabaseService.create_conversation(
                mock_db,
                1,
                f"User input {i}",
                f"Agent response {i}",
                "edu"
            )

        # 验证资源使用情况
        assert mock_db.add.call_count == 10  # 确保调用了10次add方法
        assert mock_db.commit.call_count == 10  # 确保调用了10次commit方法
        assert mock_db.refresh.call_count == 10  # 确保调用了10次refresh方法

    def test_archive_old_conversations(self):
        """测试归档旧对话记录功能"""
        # 创建模拟的数据库会话
        mock_db = MagicMock()
        
        # 模拟查询结果
        old_conversations = [
            Conversation(
                id=1, 
                user_id=1, 
                user_input="Old message 1", 
                agent_response="Response 1", 
                agent_type="edu",
                created_at=datetime.now() - timedelta(days=40)
            ),
            Conversation(
                id=2, 
                user_id=2, 
                user_input="Old message 2", 
                agent_response="Response 2", 
                agent_type="safety",
                created_at=datetime.now() - timedelta(days=40)
            )
        ]
        
        # 设置模拟查询行为
        mock_query_conversation = MagicMock()
        mock_query_conversation.filter.return_value.all.return_value = old_conversations
        mock_query_conversation.filter.return_value.delete.return_value = None
        
        mock_db.query.side_effect = lambda model: mock_query_conversation if model == Conversation else MagicMock()
        
        mock_db.add.return_value = None
        mock_db.commit.return_value = None

        # 调用方法
        result = DatabaseService.archive_old_conversations(mock_db, 30)

        # 验证结果
        assert result == 2  # 应该归档2条记录
        assert mock_db.add.call_count == 2  # 应该添加2条归档记录
        assert mock_db.commit.call_count == 2  # 应该提交2次（一次归档记录，一次删除）
        mock_query_conversation.filter.return_value.delete.assert_called_once()

    def test_archive_old_conversations_compression(self):
        """测试归档旧对话记录的压缩功能"""
        # 测试文本压缩功能
        original_text = "This is a test message that will be compressed"
        compressed_data = DatabaseService._compress_text(original_text)
        decompressed_text = DatabaseService._decompress_text(compressed_data)
        
        assert isinstance(compressed_data, bytes)
        assert decompressed_text == original_text

    def test_delete_old_conversations(self):
        """测试删除旧对话记录功能"""
        # 创建模拟的数据库会话
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        
        # 模拟删除操作
        mock_filter = MagicMock()
        mock_query.filter.return_value = mock_filter
        mock_filter.count.return_value = 5
        mock_filter.delete.return_value = None
        mock_db.commit.return_value = None

        # 调用方法
        result = DatabaseService.delete_old_conversations(mock_db, 365)

        # 验证结果
        assert result == 5  # 应该删除5条记录
        mock_db.query.assert_called_once_with(Conversation)
        mock_filter.delete.assert_called_once()
        mock_db.commit.assert_called_once()

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