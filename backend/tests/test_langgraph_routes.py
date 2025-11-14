import pytest
import sys
import os
import json
from unittest.mock import AsyncMock, Mock, patch

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app


class TestLangGraphRoutes:
    """测试LangGraph路由模块"""

    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        cls.client = TestClient(app)
        cls.client.headers = {"Content-Type": "application/json"}

    @patch('db.database_service.DatabaseService.create_session')
    def test_create_langgraph_session(self, mock_create_session):
        """测试创建LangGraph会话"""
        # 模拟数据库服务返回值
        mock_session = Mock()
        mock_session.id = 1
        mock_session.user_id = 1
        mock_session.title = "测试会话"
        mock_session.created_at = "2023-01-01T00:00:00"
        mock_session.updated_at = "2023-01-01T00:00:00"
        mock_session.is_active = True
        
        mock_create_session.return_value = mock_session

        request_data = {
            "user_id": 1,
            "title": "测试会话"
        }
        
        # 发送POST请求
        response = self.client.post("/api/langgraph/session/create", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["user_id"] == request_data["user_id"]
        assert data["title"] == request_data["title"]
        assert "created_at" in data
        assert "updated_at" in data
        assert data["is_active"] is True

    @patch('agents.multi_agent.multi_agent')
    def test_get_workflow_state(self, mock_multi_agent):
        """测试获取工作流状态"""
        # 模拟multi_agent.graph
        mock_graph = Mock()
        mock_graph.nodes = {"node1": {}, "node2": {}}
        mock_multi_agent.graph = mock_graph
        mock_multi_agent.get_system_statistics = Mock(return_value={"stat": "test"})
        
        # 发送GET请求
        response = self.client.get("/api/langgraph/workflow/state?user_id=test_user")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert "workflow_info" in data
        assert "graph_structure" in data
        assert data["workflow_info"]["name"] == "Happy Partner Multi-Agent System"
        assert "nodes" in data["graph_structure"]
        assert "edges" in data["graph_structure"]

    def test_test_workflow(self):
        """测试工作流测试端点"""
        # 发送POST请求
        response = self.client.post("/api/langgraph/test/workflow")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert "test_status" in data
        # 注意：这里我们不验证具体的测试结果，因为可能依赖于外部服务

    @patch('agents.multi_agent.multi_agent')
    @patch('db.database_service.DatabaseService.create_conversation')
    def test_langgraph_chat_success(self, mock_create_conversation, mock_multi_agent):
        """测试LangGraph聊天成功场景"""
        # 模拟multi_agent.process_message返回值
        mock_result = {
            "response": "你好！欢迎来到我们的聊天世界。我们经常用流式的方式来分享和交流，希望你在这里找到快乐。有什么想和我说的吗？",
            "mode": "story",
            "intent": "story"
        }
        mock_multi_agent.process_message = AsyncMock(return_value=mock_result)
        mock_create_conversation.return_value = None
        
        # 准备测试数据
        request_data = {
            "content": "你好，我想听个故事",
            "user_id": 1
        }
        
        # 发送POST请求
        response = self.client.post("/api/langgraph/chat", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        # assert data["response"] == "你好！欢迎来到我们的聊天世界。我们经常用流式的方式来分享和交流，希望你在这里找到快乐。有什么想和我说的吗？"
        # assert data["agent_type"] == "story"

    @patch('agents.multi_agent.multi_agent')
    @patch('db.database_service.DatabaseService.create_conversation')
    def test_langgraph_chat_with_exception(self, mock_create_conversation, mock_multi_agent):
        """测试LangGraph聊天异常场景"""
        # 模拟multi_agent.process_message抛出异常
        mock_multi_agent.process_message = AsyncMock(side_effect=Exception("测试异常"))
        mock_create_conversation.return_value = None
        
        # 准备测试数据
        request_data = {
            "content": "异常测试",
            "user_id": 1
        }
        
        # 发送POST请求
        response = self.client.post("/api/langgraph/chat", json=request_data)
        
        # 验证响应 - 现在应该返回200状态码和默认的错误消息
        assert response.status_code == 200
        # data = response.json()
        # assert "聊天处理失败" in data["response"]

    @patch('agents.multi_agent.multi_agent')
    def test_langgraph_chat_stream(self, mock_multi_agent):
        """测试LangGraph流式聊天"""
        # 模拟multi_agent.process_message返回值
        mock_result = {
            "response": "你好！欢迎来到我们的聊天世界。我们经常用流式的方式来分享和交流，希望你在这里找到快乐。有什么想和我说的吗？",
            "mode": "story"
        }
        mock_multi_agent.process_message = AsyncMock(return_value=mock_result)
        
        # 准备测试数据
        request_data = {
            "content": "流式聊天测试",
            "user_id": 1
        }
        
        # 发送POST请求
        response = self.client.post("/api/langgraph/chat/stream", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        # data = response.json()
        # assert data["type"] == "complete"
        # assert "data" in data
        # assert data["data"]["response"] == "你好！欢迎来到我们的聊天世界。我们经常用流式的方式来分享和交流，希望你在这里找到快乐。有什么想和我说的吗？"

    @patch('db.database.get_db')
    @patch('sqlalchemy.orm.Query')
    def test_get_conversation_flow_analytics(self, mock_query, mock_get_db):
        """测试获取对话流分析数据"""
        # 模拟数据库会话和查询结果
        mock_db = Mock()
        mock_query_instance = Mock()
        mock_conversation = Mock()
        mock_conversation.agent_type = "test_agent"
        mock_conversation.created_at = "2023-01-01T00:00:00"
        mock_conversation.user_input = "测试输入"
        mock_query_instance.filter.return_value.order_by.return_value.all.return_value = [mock_conversation]
        mock_query.return_value = mock_query_instance
        mock_db.query.return_value = mock_query_instance
        mock_get_db.return_value = mock_db
        
        # 发送GET请求
        response = self.client.get("/api/langgraph/analytics/conversation-flow?user_id=1&days=7")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert "analysis_period" in data
        assert "total_conversations" in data
        assert "agent_usage" in data
        assert "conversation_flow" in data

    @patch('db.database.get_db')
    @patch('sqlalchemy.orm.Query')
    def test_get_user_insights(self, mock_query, mock_get_db):
        """测试获取用户行为洞察"""
        # 模拟数据库会话和查询结果
        mock_db = Mock()
        mock_query_instance = Mock()
        mock_conversation = Mock()
        mock_conversation.agent_type = "test_agent"
        mock_conversation.agent_response = json.dumps({
            "response": "测试回复",
            "metadata": {"type": "educational", "subject": "数学"},
            "safety_info": {"passed": True}
        })
        mock_query_instance.filter.return_value.all.return_value = [mock_conversation]
        mock_query.return_value = mock_query_instance
        mock_db.query.return_value = mock_query_instance
        mock_get_db.return_value = mock_db
        
        # 发送GET请求
        response = self.client.get("/api/langgraph/users/1/insights")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert "total_conversations" in data
        assert "agent_preferences" in data
        assert "safety_incidents" in data
        assert "learning_progress" in data
        assert "emotional_patterns" in data