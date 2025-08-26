import pytest
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

    def test_filter_content_safe(self):
        """测试安全内容过滤"""
        agent = SafetyAgent()
        result = agent.filter_content("安全的教育内容")

        # 验证结果
        assert "original_content" in result
        assert result["original_content"] == "安全的教育内容"
        assert "is_safe" in result

    def test_filter_content_unsafe(self):
        """测试不安全内容过滤"""
        agent = SafetyAgent()
        result = agent.filter_content("包含暴力和危险的内容")

        # 验证结果
        assert "original_content" in result
        assert result["original_content"] == "包含暴力和危险的内容"
        assert "is_safe" in result

    def test_process_request(self):
        """测试处理请求功能"""
        agent = SafetyAgent()
        request = {
            "content": "测试内容",
            "user_id": "test_user_1"
        }
        result = agent.process_request(request)

        # 验证结果
        assert result["agent"] == "safety"
        assert "result" in result
        assert "original_content" in result["result"]