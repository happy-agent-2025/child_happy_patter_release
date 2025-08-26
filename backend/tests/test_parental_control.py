import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from sqlalchemy.orm import Session


client = TestClient(app)


class TestParentalControl:
    """家长控制台功能测试"""
    
    @patch('api.routes.get_db')
    def test_get_user_conversations(self, mock_get_db):
        """测试获取用户对话历史"""
        # 模拟数据库会话
        mock_db = MagicMock(spec=Session)
        mock_get_db.return_value = mock_db
        
        # 模拟数据库查询结果
        mock_conversation = MagicMock()
        mock_conversation.id = 1
        mock_conversation.user_id = 1
        mock_conversation.session_id = 1
        mock_conversation.agent_type = "edu"
        mock_conversation.conversation_history = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！有什么我可以帮助你的吗？"}
        ]
        mock_conversation.created_at = "2023-01-01T00:00:00"
        mock_conversation.updated_at = "2023-01-01T00:00:00"
        
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_conversation]
        
        # 发送请求
        response = client.get("/api/users/1/conversations")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "user_id" in data
        assert "conversations" in data
        assert isinstance(data["conversations"], list)
    
    @patch('api.routes.get_db')
    def test_get_user_security_logs(self, mock_get_db):
        """测试获取用户安全日志"""
        # 模拟数据库会话
        mock_db = MagicMock(spec=Session)
        mock_get_db.return_value = mock_db
        
        # 模拟数据库查询结果
        mock_log = MagicMock()
        mock_log.id = 1
        mock_log.user_id = 1
        mock_log.content = "测试内容"
        mock_log.is_safe = 1
        mock_log.filtered_content = "测试内容"
        mock_log.created_at = "2023-01-01T00:00:00"
        
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_log]
        
        # 发送请求
        response = client.get("/api/users/1/security-logs")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "user_id" in data
        assert "security_logs" in data
        assert isinstance(data["security_logs"], list)
    
    def test_parental_control_endpoints_documented(self):
        """测试家长控制台端点是否在文档中"""
        # 测试根端点
        response = client.get("/")
        assert response.status_code == 200
        
        # 检查响应中是否包含API信息
        data = response.json()
        assert "message" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])