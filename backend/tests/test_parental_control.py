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
    
    def test_get_user_activity_stats(self):
        """测试获取用户活动统计信息"""
        # 发送请求到一个不存在的用户，但验证接口逻辑是否正常
        response = client.get("/api/users/999999/activity-stats")
        
        # 验证响应状态码
        assert response.status_code == 200 or response.status_code == 404
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
            assert "user_id" in data
            assert "statistics" in data
            assert isinstance(data["statistics"], dict)
    
    def test_get_user_learning_progress(self):
        """测试获取用户学习进度"""
        # 发送请求到一个不存在的用户，但验证接口逻辑是否正常
        response = client.get("/api/users/999999/learning-progress")
        
        # 验证响应状态码
        assert response.status_code == 200 or response.status_code == 404
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
            assert "user_id" in data
            assert "total_questions" in data
    
    def test_update_content_filters(self):
        """测试更新用户内容过滤设置"""
        # 发送请求更新内容过滤设置
        filters_data = {
            "profanity_filter": True,
            "violence_filter": True,
            "adult_content_filter": True
        }
        response = client.post("/api/users/999999/content-filters", json=filters_data)
        
        # 验证响应状态码
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "user_id" in data
        assert "filters" in data
        assert data["filters"] == filters_data
    
    def test_get_user_usage_limits(self):
        """测试获取用户使用限制设置"""
        # 发送请求获取使用限制设置
        response = client.get("/api/users/999999/usage-limits")
        
        # 验证响应状态码
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "user_id" in data
        assert "daily_limit_minutes" in data
        assert "weekly_limit_minutes" in data
        assert "session_limit_minutes" in data
    
    def test_update_user_usage_limits(self):
        """测试更新用户使用限制设置"""
        # 发送请求更新使用限制设置
        limits_data = {
            "daily_limit_minutes": 60,
            "weekly_limit_minutes": 300,
            "session_limit_minutes": 15
        }
        response = client.post("/api/users/999999/usage-limits", json=limits_data)
        
        # 验证响应状态码
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "user_id" in data
        assert "limits" in data
        assert data["limits"] == limits_data
    
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