import pytest
from unittest.mock import patch
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

    @patch('utils.openai_client.openai_client.chat_completion')
    def test_route_request(self, mock_chat_completion):
        """测试请求路由功能"""
        # 设置模拟返回值
        mock_chat_completion.return_value = "edu"

        agent = MetaAgent()
        default_request = {
            "content": "我想学习数学",
            "user_id": "test_user_1"
        }
        result = agent.route_request(default_request)

        # 验证结果
        assert result == "edu"
        
        # 验证方法被正确调用
        mock_chat_completion.assert_called_once()

    @patch('agents.meta_agent.MetaAgent.route_request')
    def test_process_request(self, mock_route_request):
        """测试处理请求功能"""
        # 设置模拟返回值
        mock_route_request.return_value = "edu"

        agent = MetaAgent()
        request = {
            "content": "我想学习数学",
            "user_id": "test_user_1"
        }
        result = agent.process_request(request)

        # 验证结果
        assert result["agent"] == "edu"
        assert result["request"] == request
        assert result["status"] == "routed"
        
        # 验证方法被正确调用
        mock_route_request.assert_called_once_with(request)