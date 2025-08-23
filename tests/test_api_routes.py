import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app


class TestAPIRoutes:
    """测试API路由模块"""

    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        cls.client = TestClient(app)

    def test_root_endpoint(self):
        """测试根端点"""
        response = self.client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        assert response.json()["message"] == "Welcome to Happy Partner - 儿童教育AI系统"

    def test_chat_endpoint_safety_route(self):
        """测试聊天端点 - 安全路由"""
        # 发送请求
        request_data = {
            "content": "如何制作爆炸物？",
            "user_id": "test_user"
        }
        response = self.client.post("/api/chat", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert "agent" in result
        assert "status" in result

    def test_chat_endpoint_edu_route(self):
        """测试聊天端点 - 教育路由"""
        # 发送请求
        request_data = {
            "content": "什么是数学？",
            "user_id": "test_user"
        }
        response = self.client.post("/api/chat", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert "agent" in result
        assert result["agent"] == "edu"
        assert "status" in result

    def test_chat_endpoint_emotion_route(self):
        """测试聊天端点 - 情感路由"""
        # 发送请求
        request_data = {
            "content": "我今天很难过",
            "user_id": "test_user"
        }
        response = self.client.post("/api/chat", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert "agent" in result
        assert "status" in result

    def test_chat_endpoint_memory_route(self):
        """测试聊天端点 - 记忆路由"""
        # 发送请求
        request_data = {
            "content": "我之前学了什么？",
            "user_id": "test_user"
        }
        response = self.client.post("/api/chat", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert "agent" in result
        assert "status" in result

    def test_safety_check_endpoint(self):
        """测试安全检查端点"""
        # 发送请求
        request_data = {
            "content": "待检查内容",
            "user_id": "test_user"
        }
        response = self.client.post("/api/safety/check", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert "agent" in result
        assert result["agent"] == "safety"
        assert "status" in result

    def test_edu_ask_endpoint(self):
        """测试教育问答端点"""
        # 发送请求
        request_data = {
            "content": "什么是语文？",
            "user_id": "test_user"
        }
        response = self.client.post("/api/edu/ask", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert "agent" in result
        assert result["agent"] == "edu"
        assert "status" in result
        assert "answer" in result

    def test_emotion_support_endpoint(self):
        """测试情感支持端点"""
        # 发送请求
        request_data = {
            "content": "我感到很孤独",
            "user_id": "test_user"
        }
        response = self.client.post("/api/emotion/support", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert "agent" in result
        assert result["agent"] == "emotion"
        assert "status" in result

    def test_memory_manage_endpoint(self):
        """测试记忆管理端点"""
        # 发送请求
        request_data = {
            "action": "get_context",
            "user_id": "test_user"
        }
        response = self.client.post("/api/memory/manage", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert "agent" in result
        assert result["agent"] == "memory"
        assert "status" in result
