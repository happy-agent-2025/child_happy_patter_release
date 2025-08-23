import pytest
from unittest.mock import patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.safety_agent import SafetyAgent


class TestSafetyAgent:
    """测试安全代理模块"""

    def test_init(self):
        """测试SafetyAgent初始化"""
        agent = SafetyAgent()
        assert agent is not None
        assert hasattr(agent, 'safety_guidelines')

    @patch('utils.openai_client.openai_client.chat_completion')
    def test_filter_content_safe(self, mock_chat_completion):
        """测试安全内容过滤"""
        # 设置模拟返回值
        mock_chat_completion.return_value = """安全状态: 安全
检测到的问题: 无
过滤后内容: 保持原样"""

        agent = SafetyAgent()
        result = agent.filter_content("安全的教育内容")

        # 验证结果
        assert result["is_safe"] == True
        assert result["issues"] == []
        assert result["original_content"] == "安全的教育内容"
        
        # 验证方法被正确调用
        mock_chat_completion.assert_called_once()

    @patch('utils.openai_client.openai_client.chat_completion')
    def test_filter_content_unsafe(self, mock_chat_completion):
        """测试不安全内容过滤"""
        # 设置模拟返回值
        mock_chat_completion.return_value = """安全状态: 不安全
检测到的问题: 包含暴力相关内容
过滤后内容: 建议将内容修改为积极健康的主题，例如友谊、合作或学习相关的正面内容"""

        agent = SafetyAgent()
        result = agent.filter_content("包含暴力和危险的内容")

        # 验证结果
        assert result["is_safe"] == False
        assert len(result["issues"]) > 0
        assert "暴力相关" in result["issues"][0]
        assert result["original_content"] == "包含暴力和危险的内容"
        
        # 验证方法被正确调用
        mock_chat_completion.assert_called_once()

    @patch('agents.safety_agent.SafetyAgent.filter_content')
    def test_process_request(self, mock_filter_content):
        """测试处理请求功能"""
        # 设置模拟返回值
        mock_filter_content.return_value = {
            "original_content": "测试内容",
            "is_safe": True,
            "issues": [],
            "filtered_content": "测试内容"
        }

        agent = SafetyAgent()
        request = {
            "content": "测试内容",
            "user_id": "test_user_1"
        }
        result = agent.process_request(request)

        # 验证结果
        assert result["agent"] == "safety"
        assert "result" in result
        assert result["result"]["is_safe"] == True
        
        # 验证方法被正确调用
        mock_filter_content.assert_called_once_with("测试内容")