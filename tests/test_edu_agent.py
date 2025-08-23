import pytest
import sys
import os
from unittest.mock import patch

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.edu_agent import EduAgent


class TestEduAgent:
    """测试教育代理模块"""

    def test_init(self):
        """测试EduAgent初始化"""
        agent = EduAgent()
        assert agent is not None
        assert hasattr(agent, 'system_prompt')

    def test_answer_question(self):
        """测试回答问题功能"""
        agent = EduAgent()
        result = agent.answer_question("什么是数学？")
        
        # 验证返回结果不为空且包含相关内容
        assert result is not None
        assert len(result) > 0
        # 验证返回内容与数学相关
        assert "数学" in result or "math" in result.lower()

    def test_process_request(self):
        """测试处理请求功能"""
        agent = EduAgent()
        request = {
            "content": "什么是语文？",
            "user_id": "test_user_1"
        }
        result = agent.process_request(request)

        # 验证结果
        assert result["agent"] == "edu"
        assert result["question"] == "什么是语文？"
        assert "answer" in result
        assert result["answer"] is not None
        assert len(result["answer"]) > 0