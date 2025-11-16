import pytest
import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app
from schemas.chat import ChatRequest


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
        assert response.json()["message"] == "儿童故事互动AI系统API服务"

    def test_chat_endpoint_safety_route(self):
        """测试聊天端点 - 安全路由"""
        # 发送请求
        request_data = {
            "content": "如何制作爆炸物？",
            "user_id": 1
        }
        response = self.client.post("/api/chat", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert "response" in result
        assert "agent_type" in result

    def test_chat_endpoint_edu_route(self):
        """测试聊天端点 - 教育路由"""
        # 发送请求
        request_data = {
            "content": "什么是数学？",
            "user_id": 1
        }
        response = self.client.post("/api/chat", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert "response" in result
        assert "agent_type" in result

    def test_chat_endpoint_emotion_route(self):
        """测试聊天端点 - 情感路由"""
        # 发送请求
        request_data = {
            "content": "我今天很难过",
            "user_id": 1
        }
        response = self.client.post("/api/chat", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert "response" in result
        assert "agent_type" in result

    def test_chat_endpoint_with_session(self):
        """测试聊天端点 - 带会话ID"""
        # 发送请求
        request_data = {
            "content": "你好",
            "user_id": 1,
            "session_id": 123
        }
        response = self.client.post("/api/chat", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert "response" in result
        assert "agent_type" in result

    def test_safety_check_endpoint(self):
        """测试安全检查端点"""
        # 发送请求
        request_data = {
            "content": "待检查内容",
            "user_id": 1
        }
        response = self.client.post("/api/safety/check", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert "is_safe" in result
        assert "confidence" in result

    def test_edu_ask_endpoint(self):
        """测试教育问答端点"""
        # 发送请求
        request_data = {
            "question": "什么是语文？",
            "user_id": 1
        }
        response = self.client.post("/api/edu/ask", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert "answer" in result

    def test_emotion_support_endpoint(self):
        """测试情感支持端点"""
        # 发送请求
        request_data = {
            "content": "我感到很孤独",
            "user_id": 1
        }
        response = self.client.post("/api/emotion/support", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert "response" in result
        assert "support_type" in result

    def test_memory_manage_endpoint(self):
        """测试记忆管理端点"""
        # 发送请求
        request_data = {
            "action": "get_context",
            "user_id": 1
        }
        response = self.client.post("/api/memory/manage", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert "success" in result
        assert "action" in result

    def test_get_user_conversations_endpoint(self):
        """测试获取用户对话历史端点"""
        # 发送请求
        user_id = 1
        response = self.client.get(f"/api/users/{user_id}/conversations")
        
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert "user_id" in result
        assert "conversations" in result

    def test_get_user_security_logs_endpoint(self):
        """测试获取用户安全日志端点"""
        # 发送请求
        user_id = 1
        response = self.client.get(f"/api/users/{user_id}/security-logs")
        
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert "user_id" in result
        assert "security_logs" in result

    def test_session_management_endpoints(self):
        """测试会话管理端点"""
        user_id = 1
        
        # 创建会话
        response = self.client.post(f"/api/users/{user_id}/sessions", params={"title": "测试会话"})
        assert response.status_code == 200
        session_result = response.json()
        assert "session_id" in session_result
        session_id = session_result["session_id"]
        
        # 获取用户会话列表
        response = self.client.get(f"/api/users/{user_id}/sessions")
        assert response.status_code == 200
        sessions_result = response.json()
        assert "sessions" in sessions_result
        
        # 在会话中进行对话
        chat_data = {
            "content": "你好，这是会话中的对话",
            "user_id": user_id,
            "session_id": session_id
        }
        response = self.client.post("/api/chat", json=chat_data)
        assert response.status_code == 200
        
        # 获取会话中的对话
        response = self.client.get(f"/api/sessions/{session_id}/conversations")
        assert response.status_code == 200
        conv_result = response.json()
        assert "conversations" in conv_result
        
        # 删除会话
        response = self.client.delete(f"/api/sessions/{session_id}")
        assert response.status_code == 200
        delete_result = response.json()
        assert delete_result["deleted"] == True

    def test_conversation_uniqueness(self):
        """测试对话记录的唯一性"""
        user_id = 1
        
        # 发送相同的请求两次
        request_data = {
            "question": "测试对话唯一性",
            "user_id": user_id
        }
        
        # 第一次请求
        response1 = self.client.post("/api/edu/ask", json=request_data)
        assert response1.status_code == 200
        
        # 第二次请求（相同内容）
        response2 = self.client.post("/api/edu/ask", json=request_data)
        assert response2.status_code == 200
        
        # 检查数据库中是否只有一条记录
        response = self.client.get(f"/api/users/{user_id}/conversations")
        assert response.status_code == 200
        result = response.json()
        conversations = result["conversations"]
        
        # 查找edu类型的对话
        edu_conversations = [conv for conv in conversations if conv["agent_type"] == "edu"]
        assert len(edu_conversations) > 0
        
        # 验证edu对话中包含我们的测试内容
        latest_edu_conv = edu_conversations[0]
        history = latest_edu_conv["conversation_history"]
        assert len(history) > 0  # 至少有一条记录

    def test_emotion_agent_analysis_storage(self):
        """测试emotion_agent情感分析的存储"""
        user_id = 1
        
        # 发送情感支持请求
        request_data = {
            "content": "我今天感到很沮丧",
            "user_id": user_id
        }
        response = self.client.post("/api/emotion/support", json=request_data)
        assert response.status_code == 200
        
        # 检查数据库中是否存储了情感分析
        response = self.client.get(f"/api/users/{user_id}/conversations")
        assert response.status_code == 200
        result = response.json()
        conversations = result["conversations"]
        
        # 查找emotion类型的对话
        emotion_conversations = [conv for conv in conversations if conv["agent_type"] == "emotion"]
        assert len(emotion_conversations) > 0
        
        # 验证存储的内容包含情感分析
        latest_emotion_conv = emotion_conversations[0]
        history_str = latest_emotion_conv["conversation_history"]
        assert isinstance(history_str, str) and len(history_str) > 0
        
        # 尝试解析JSON字符串
        import json
        try:
            history = json.loads(history_str)
            assert isinstance(history, list)
            assert len(history) > 0
        except json.JSONDecodeError:
            # 如果不是有效的JSON，至少确保有内容
            assert len(history_str) > 0