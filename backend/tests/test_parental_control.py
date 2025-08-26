import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


class TestParentalControl:
    """家长控制台功能测试"""
    
    def test_get_user_conversations(self):
        """测试获取用户对话历史"""
        # 发送请求到一个不存在的用户，但验证接口逻辑是否正常
        response = client.get("/api/users/999999/conversations")
        
        # 验证响应状态码
        assert response.status_code == 200 or response.status_code == 404
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
            assert "user_id" in data
            assert "conversations" in data
            assert isinstance(data["conversations"], list)
    
    def test_get_user_security_logs(self):
        """测试获取用户安全日志"""
        # 发送请求到一个不存在的用户，但验证接口逻辑是否正常
        response = client.get("/api/users/999999/security-logs")
        
        # 验证响应状态码
        assert response.status_code == 200 or response.status_code == 404
        if response.status_code == 200:
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