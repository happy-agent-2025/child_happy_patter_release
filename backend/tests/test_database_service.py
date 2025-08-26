import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from models.user import User, Conversation, ArchivedConversation, SecurityLog
from db.database_service import DatabaseService
from datetime import datetime, timedelta
import zlib
import json


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

    def test_create_conversation_new_session(self):
        """测试为新用户和代理类型创建对话记录功能"""
        # 创建模拟的数据库会话
        mock_db = MagicMock()
        
        # 模拟查询结果为空（没有现有对话）
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        mock_conversation = Conversation(
            id=1,
            user_id=1,
            session_id=100,
            conversation_history=[{
                "user_input": "Hello",
                "agent_response": "Hi there!",
                "timestamp": datetime.now().isoformat()
            }],
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
            "edu",
            100  # session_id
        )

        # 验证结果
        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_create_conversation_existing_session(self):
        """测试为现有用户和代理类型追加对话记录功能"""
        # 创建模拟的数据库会话
        mock_db = MagicMock()
        
        # 模拟已存在的对话记录
        existing_conversation = Conversation(
            id=1,
            user_id=1,
            session_id=100,
            conversation_history=[{
                "user_input": "Hello",
                "agent_response": "Hi there!",
                "timestamp": datetime.now().isoformat()
            }],
            agent_type="edu"
        )
        
        # 模拟查询结果为已存在的对话
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = existing_conversation
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        # 调用方法
        result = DatabaseService.create_conversation(
            mock_db,
            1,
            "How are you?",
            "I'm fine, thanks!",
            "edu",
            100  # session_id
        )

        # 验证结果 - 应该更新现有记录而不是创建新记录
        assert result is not None
        assert len(result.conversation_history) == 2  # 应该有两条对话记录
        mock_db.add.assert_not_called()  # 不应该调用add方法
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_get_conversation_by_user_and_agent(self):
        """测试根据用户ID和代理类型获取对话记录功能"""
        # 创建模拟的数据库会话和查询
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        
        conversation_history = [{
            "user_input": "Hello",
            "agent_response": "Hi there!",
            "timestamp": datetime.now().isoformat()
        }, {
            "user_input": "How are you?",
            "agent_response": "I'm fine, thanks!",
            "timestamp": datetime.now().isoformat()
        }]
        
        mock_filter = MagicMock()
        mock_filter.first.return_value = Conversation(
            id=1,
            user_id=1,
            session_id=100,
            conversation_history=conversation_history,
            agent_type="edu"
        )
        mock_query.filter.return_value = mock_filter

        # 调用方法
        result = DatabaseService.get_conversation_by_user_and_agent(mock_db, 1, "edu")

        # 验证结果
        assert result is not None
        assert result.user_id == 1
        assert result.agent_type == "edu"
        assert len(result.conversation_history) == 2
        mock_db.query.assert_called_once_with(Conversation)
        mock_query.filter.assert_called_once()

    def test_get_recent_conversations_by_user(self):
        """测试根据用户ID获取最近对话记录功能"""
        # 创建模拟的数据库会话和查询
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        
        conversation_history = [{
            "user_input": "Hello",
            "agent_response": "Hi there!",
            "timestamp": datetime.now().isoformat()
        }]
        
        mock_filter = MagicMock()
        mock_order_by = MagicMock()
        mock_limit = MagicMock()
        mock_filter.order_by.return_value = mock_order_by
        mock_order_by.limit.return_value = mock_limit
        mock_limit.all.return_value = [
            Conversation(
                id=1,
                user_id=1,
                session_id=100,
                conversation_history=conversation_history,
                agent_type="edu"
            ),
            Conversation(
                id=2,
                user_id=1,
                session_id=101,
                conversation_history=conversation_history,
                agent_type="safety"
            )
        ]
        mock_query.filter.return_value = mock_filter

        # 调用方法
        result = DatabaseService.get_recent_conversations_by_user(mock_db, 1, 10)

        # 验证结果
        assert result is not None
        assert len(result) == 2
        mock_db.query.assert_called_once_with(Conversation)
        mock_query.filter.assert_called_once()

    def test_get_conversations_by_session(self):
        """测试根据会话ID获取对话记录功能"""
        # 创建模拟的数据库会话和查询
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        
        conversation_history = [{
            "user_input": "Hello",
            "agent_response": "Hi there!",
            "timestamp": datetime.now().isoformat()
        }]
        
        mock_filter = MagicMock()
        mock_order_by = MagicMock()
        mock_filter.order_by.return_value = mock_order_by
        mock_order_by.all.return_value = [
            Conversation(
                id=1,
                user_id=1,
                session_id=100,
                conversation_history=conversation_history,
                agent_type="edu"
            ),
            Conversation(
                id=2,
                user_id=1,
                session_id=100,
                conversation_history=conversation_history,
                agent_type="safety"
            )
        ]
        mock_query.filter.return_value = mock_filter

        # 调用方法
        result = DatabaseService.get_conversations_by_session(mock_db, 100)

        # 验证结果
        assert result is not None
        assert len(result) == 2
        mock_db.query.assert_called_once_with(Conversation)
        mock_query.filter.assert_called_once()

    def test_database_resource_usage(self):
        """测试数据库资源使用情况"""
        # 创建模拟的数据库会话
        mock_db = MagicMock()
        
        # 模拟查询行为
        mock_query = MagicMock()
        
        # 使用side_effect来模拟第一次查询返回None，后续返回已创建的对话对象
        call_count = 0
        def query_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_filter = MagicMock()
            if call_count == 1:
                # 第一次查询返回None（没有现有对话）
                mock_filter.first.return_value = None
            else:
                # 后续查询返回已创建的对话对象
                mock_filter.first.return_value = Conversation(
                    id=1,
                    user_id=1,
                    session_id=100,
                    conversation_history=[{
                        "user_input": "Test input",
                        "agent_response": "Test response",
                        "timestamp": datetime.now().isoformat()
                    }],
                    agent_type="edu"
                )
            return mock_filter
        
        mock_query.filter.side_effect = query_side_effect
        mock_db.query.return_value = mock_query
        
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        # 模拟多次创建对话记录（相同用户ID和代理类型）
        for i in range(10):
            DatabaseService.create_conversation(
                mock_db,
                1,
                f"User input {i}",
                f"Agent response {i}",
                "edu",
                100  # session_id
            )

        # 验证资源使用情况
        # 第一次调用add创建新记录，后续9次应该更新现有记录
        assert mock_db.add.call_count == 1  
        assert mock_db.commit.call_count == 10  # 每次都应该调用commit
        assert mock_db.refresh.call_count == 10  # 每次都应该调用refresh

    def test_archive_old_conversations(self):
        """测试归档旧对话记录功能"""
        # 创建模拟的数据库会话
        mock_db = MagicMock()
        
        # 模拟查询结果
        old_conversations = [
            Conversation(
                id=1, 
                user_id=1, 
                session_id=100,
                conversation_history=[{
                    "user_input": "Old message 1", 
                    "agent_response": "Response 1", 
                    "timestamp": datetime.now().isoformat()
                }],
                agent_type="edu",
                created_at=datetime.now() - timedelta(days=40)
            ),
            Conversation(
                id=2, 
                user_id=2, 
                session_id=101,
                conversation_history=[{
                    "user_input": "Old message 2", 
                    "agent_response": "Response 2", 
                    "timestamp": datetime.now().isoformat()
                }],
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
        
        # 测试JSON压缩功能
        original_json = [{
            "user_input": "Hello",
            "agent_response": "Hi there!",
            "timestamp": datetime.now().isoformat()
        }]
        compressed_json = DatabaseService._compress_json(original_json)
        decompressed_json = DatabaseService._decompress_json(compressed_json)
        
        assert isinstance(compressed_json, bytes)
        assert decompressed_json == original_json

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