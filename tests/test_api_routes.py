import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient

from main import app
from agents.meta_agent import MetaAgent
from agents.safety_agent import SafetyAgent
from agents.edu_agent import EduAgent
from agents.memory_agent import MemoryAgent

client = TestClient(app)


class TestAPIRoutes:
    """测试API路由模块"""

    def test_root_endpoint(self):
        """测试根端点"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        assert response.json()["message"] == "Welcome to Happy Partner - 儿童教育AI系统"

    @patch('agents.meta_agent.MetaAgent.process_request')
    @patch('agents.safety_agent.SafetyAgent.process_request')
    def test_chat_endpoint_safety_route(self, mock_safety_process, mock_meta_process):
        """测试聊天端点 - 安全路由"""
        # 设置模拟返回值
        mock_meta_process.return_value = {"agent": "safety"}
        mock_safety_process.return_value = {"agent": "safety", "result": "安全内容处理结果"}
        
        # 发送请求
        request_data = {
            "content": "测试安全内容",
            "user_id": "test_user"
        }
        response = client.post("/api/chat", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        assert response.json()["agent"] == "safety"
        assert "result" in response.json()
        
        # 验证方法被正确调用
        mock_meta_process.assert_called_once_with(request_data)
        mock_safety_process.assert_called_once_with(request_data)

    @patch('agents.meta_agent.MetaAgent.process_request')
    @patch('agents.edu_agent.EduAgent.process_request')
    def test_chat_endpoint_edu_route(self, mock_edu_process, mock_meta_process):
        """测试聊天端点 - 教育路由"""
        # 设置模拟返回值
        mock_meta_process.return_value = {"agent": "edu"}
        mock_edu_process.return_value = {"agent": "edu", "result": "教育问答结果"}
        
        # 发送请求
        request_data = {
            "content": "什么是数学？",
            "user_id": "test_user"
        }
        response = client.post("/api/chat", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        assert response.json()["agent"] == "edu"
        assert "result" in response.json()
        
        # 验证方法被正确调用
        mock_meta_process.assert_called_once_with(request_data)
        mock_edu_process.assert_called_once_with(request_data)

    @patch('agents.meta_agent.MetaAgent.process_request')
    @patch('agents.memory_agent.MemoryAgent.process_request')
    def test_chat_endpoint_memory_route(self, mock_memory_process, mock_meta_process):
        """测试聊天端点 - 记忆路由"""
        # 设置模拟返回值
        mock_meta_process.return_value = {"agent": "memory"}
        mock_memory_process.return_value = {"agent": "memory", "result": "记忆处理结果"}
        
        # 发送请求
        request_data = {
            "content": "查询历史记录",
            "user_id": "test_user"
        }
        response = client.post("/api/chat", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        assert response.json()["agent"] == "memory"
        assert "result" in response.json()
        
        # 验证方法被正确调用
        mock_meta_process.assert_called_once_with(request_data)
        mock_memory_process.assert_called_once_with(request_data)

    @patch('agents.meta_agent.MetaAgent.process_request')
    def test_chat_endpoint_default_route(self, mock_meta_process):
        """测试聊天端点 - 默认路由"""
        # 设置模拟返回值
        mock_meta_process.return_value = {"agent": "unknown"}
        
        # 发送请求
        request_data = {
            "content": "未知类型请求",
            "user_id": "test_user"
        }
        response = client.post("/api/chat", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        assert response.json()["agent"] == "unknown"
        assert "message" in response.json()
        
        # 验证方法被正确调用
        mock_meta_process.assert_called_once_with(request_data)

    @patch('agents.safety_agent.SafetyAgent.process_request')
    def test_safety_check_endpoint(self, mock_safety_process):
        """测试安全检查端点"""
        # 设置模拟返回值
        mock_safety_process.return_value = {"agent": "safety", "result": "安全检查完成"}
        
        # 发送请求
        request_data = {
            "content": "待检查内容",
            "user_id": "test_user"
        }
        response = client.post("/api/safety/check", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        assert response.json()["agent"] == "safety"
        assert "result" in response.json()
        
        # 验证方法被正确调用
        mock_safety_process.assert_called_once_with(request_data)

    @patch('agents.edu_agent.EduAgent.process_request')
    def test_edu_ask_endpoint(self, mock_edu_process):
        """测试教育问答端点"""
        # 设置模拟返回值
        mock_edu_process.return_value = {"agent": "edu", "result": "教育问答结果"}
        
        # 发送请求
        request_data = {
            "content": "什么是语文？",
            "user_id": "test_user"
        }
        response = client.post("/api/edu/ask", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        assert response.json()["agent"] == "edu"
        assert "result" in response.json()
        
        # 验证方法被正确调用
        mock_edu_process.assert_called_once_with(request_data)

    @patch('agents.memory_agent.MemoryAgent.process_request')
    def test_memory_manage_endpoint(self, mock_memory_process):
        """测试记忆管理端点"""
        # 设置模拟返回值
        mock_memory_process.return_value = {"agent": "memory", "result": "记忆管理完成"}
        
        # 发送请求
        request_data = {
            "content": "清空历史记录",
            "user_id": "test_user"
        }
        response = client.post("/api/memory/manage", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        assert response.json()["agent"] == "memory"
        assert "result" in response.json()
        
        # 验证方法被正确调用
        mock_memory_process.assert_called_once_with(request_data)