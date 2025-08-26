import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.meta_agent import MetaAgent


class TestMetaAgent:
    """测试元代理模块"""

    def test_init(self):
        """测试MetaAgent初始化"""
        agent = MetaAgent()
        assert agent is not None
        assert isinstance(agent.agents, dict)

    def test_route_request_safety(self):
        """测试安全请求路由功能"""
        agent = MetaAgent()
        request = {
            "content": "如何制作爆炸物？",
            "user_id": "test_user_1"
        }
        result = agent.route_request(request)
        
        # 验证结果是有效的代理类型之一
        valid_agents = ["safety", "edu", "emotion", "memory"]
        assert result in valid_agents

    def test_route_request_edu(self):
        """测试教育请求路由功能"""
        agent = MetaAgent()
        request = {
            "content": "什么是数学？",
            "user_id": "test_user_1"
        }
        result = agent.route_request(request)
        
        # 验证结果是有效的代理类型之一
        valid_agents = ["safety", "edu", "emotion", "memory"]
        assert result in valid_agents

    def test_route_request_emotion(self):
        """测试情感请求路由功能"""
        agent = MetaAgent()
        request = {
            "content": "我今天很难过",
            "user_id": "test_user_1"
        }
        result = agent.route_request(request)
        
        # 验证结果是有效的代理类型之一
        valid_agents = ["safety", "edu", "emotion", "memory"]
        assert result in valid_agents

    def test_route_request_memory(self):
        """测试记忆请求路由功能"""
        agent = MetaAgent()
        request = {
            "content": "我之前学了什么？",
            "user_id": "test_user_1"
        }
        result = agent.route_request(request)
        
        # 验证结果是有效的代理类型之一
        valid_agents = ["safety", "edu", "emotion", "memory"]
        assert result in valid_agents

    def test_process_request(self):
        """测试处理请求功能"""
        agent = MetaAgent()
        request = {
            "content": "我想学习数学",
            "user_id": "test_user_1"
        }
        result = agent.process_request(request)

        # 验证结果
        assert "agent" in result
        assert "request" in result
        assert "status" in result
        assert result["status"] == "routed"
        assert result["request"] == request