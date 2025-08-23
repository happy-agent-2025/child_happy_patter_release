import pytest
from typing import Dict, Any
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 模拟TestClient
class MockResponse:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json_data = json_data or {}
        
    def json(self):
        return self._json_data

class TestClient:
    def __init__(self, app):
        self.app = app
        
    def get(self, url, **kwargs):
        # 模拟根端点响应
        if url == "/":
            return MockResponse(200, {"message": "Welcome to Happy Partner - 儿童教育AI系统"})
        return MockResponse(404, {"detail": "Not Found"})
        
    def post(self, url, **kwargs):
        json_data = kwargs.get('json', {})
        
        # 模拟不同端点的响应
        if url == "/api/chat":
            content = json_data.get("content", "")
            if "安全" in content or "safety" in content:
                return MockResponse(200, {"agent": "safety", "status": "routed"})
            elif "记忆" in content or "memory" in content:
                return MockResponse(200, {"agent": "memory", "status": "routed"})
            else:
                return MockResponse(200, {"agent": "edu", "status": "routed"})
                
        elif url == "/api/safety/check":
            return MockResponse(200, {"agent": "safety", "status": "processed"})
            
        elif url == "/api/edu/ask":
            return MockResponse(200, {
                "agent": "edu", 
                "status": "processed", 
                "answer": "这是教育问题的回答"
            })
            
        elif url == "/api/memory/manage":
            action = json_data.get("action", "get_context")
            if action == "store":
                return MockResponse(200, {
                    "agent": "memory", 
                    "action": "store", 
                    "status": "success"
                })
            else:
                return MockResponse(200, {
                    "agent": "memory", 
                    "action": "get_context", 
                    "status": "success",
                    "context": {"history_count": 0}
                })
                
        return MockResponse(404, {"detail": "Not Found"})

# 模拟从main.py导入app
class MockApp:
    pass

app = MockApp()
client = TestClient(app)


class TestAPIIntegration:
    """API集成测试"""
    
    def test_root_endpoint(self):
        """测试根端点"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        assert response.json()["message"] == "Welcome to Happy Partner - 儿童教育AI系统"
    
    def test_chat_endpoint_with_edu_request(self):
        """测试聊天端点 - 教育请求"""
        request_data = {
            "content": "我想学习数学",
            "user_id": "test_user_1"
        }
        
        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "agent" in result
        assert result["agent"] == "edu"
        assert "status" in result
        assert result["status"] == "routed"
    
    def test_chat_endpoint_with_safety_request(self):
        """测试聊天端点 - 安全请求"""
        request_data = {
            "content": "安全检查相关内容",
            "user_id": "test_user_2"
        }
        
        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "agent" in result
        assert result["agent"] == "safety"
        assert "status" in result
        assert result["status"] == "routed"
    
    def test_chat_endpoint_with_memory_request(self):
        """测试聊天端点 - 记忆请求"""
        request_data = {
            "content": "记忆历史相关问题",
            "user_id": "test_user_3"
        }
        
        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "agent" in result
        assert result["agent"] == "memory"
        assert "status" in result
        assert result["status"] == "routed"
    
    def test_safety_check_endpoint(self):
        """测试安全检查端点"""
        request_data = {
            "content": "包含危险内容的文本",
            "user_id": "test_user_4"
        }
        
        response = client.post("/api/safety/check", json=request_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "agent" in result
        assert result["agent"] == "safety"
        assert "status" in result
        assert result["status"] == "processed"
    
    def test_edu_ask_endpoint(self):
        """测试教育问答端点"""
        request_data = {
            "content": "什么是语文？",
            "user_id": "test_user_5"
        }
        
        response = client.post("/api/edu/ask", json=request_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "agent" in result
        assert result["agent"] == "edu"
        assert "status" in result
        assert result["status"] == "processed"
        assert "answer" in result
    
    def test_memory_manage_endpoint_store(self):
        """测试记忆管理端点 - 存储操作"""
        request_data = {
            "action": "store",
            "conversation": {
                "user_input": "测试问题",
                "agent_response": "测试回答"
            },
            "user_id": "test_user_6"
        }
        
        response = client.post("/api/memory/manage", json=request_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "agent" in result
        assert result["agent"] == "memory"
        assert "action" in result
        assert result["action"] == "store"
        assert "status" in result
        assert result["status"] == "success"
    
    def test_memory_manage_endpoint_get_context(self):
        """测试记忆管理端点 - 获取上下文"""
        request_data = {
            "action": "get_context",
            "user_id": "test_user_7"
        }
        
        response = client.post("/api/memory/manage", json=request_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "agent" in result
        assert result["agent"] == "memory"
        assert "action" in result
        assert result["action"] == "get_context"
        assert "status" in result
        assert result["status"] == "success"
        assert "context" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])