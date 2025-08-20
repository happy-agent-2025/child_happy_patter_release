import pytest
from agents.meta_agent import MetaAgent


class TestMetaAgent:
    """测试MetaAgent类"""
    
    def test_init(self):
        """测试MetaAgent初始化"""
        agent = MetaAgent()
        assert agent is not None
        assert isinstance(agent.agents, dict)
    
    def test_route_request(self):
        """测试请求路由功能"""
        agent = MetaAgent()
        
        # 测试路由到安全代理
        safety_request = {"content": "安全检查"}
        assert agent.route_request(safety_request) == "safety"
        
        # 测试路由到教育代理
        edu_request = {"content": "学习数学"}
        assert agent.route_request(edu_request) == "edu"
        
        # 测试默认路由
        default_request = {"content": "你好"}
        assert agent.route_request(default_request) == "edu"
    
    def test_process_request(self):
        """测试请求处理功能"""
        agent = MetaAgent()
        request = {"content": "学习语文"}
        result = agent.process_request(request)
        
        assert result["agent"] == "edu"
        assert result["request"] == request
        assert result["status"] == "routed"