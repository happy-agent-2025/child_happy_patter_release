import pytest
from unittest.mock import patch
import sys
import os

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

    @patch('utils.openai_client.openai_client.chat_completion')
    def test_answer_question(self, mock_chat_completion):
        """测试回答问题功能"""
        # 设置模拟返回值
        mock_chat_completion.return_value = "数学是研究数量、结构、空间以及变化等概念的一门学科。"

        agent = EduAgent()
        result = agent.answer_question("什么是数学？")

        # 验证结果
        assert "数学是研究数量" in result
        
        # 验证方法被正确调用
        mock_chat_completion.assert_called_once()

    @patch('utils.openai_client.openai_client.chat_completion')
    def test_process_request(self, mock_chat_completion):
        """测试处理请求功能"""
        # 设置模拟返回值
        mock_chat_completion.return_value = "数学是研究数量、结构、空间以及变化等概念的一门学科。"

        agent = EduAgent()
        request = {
            "content": "什么是数学？",
            "user_id": "test_user_1"
        }
        result = agent.process_request(request)

        # 验证结果
        assert result["agent"] == "edu"
        assert result["question"] == "什么是数学？"
        assert "数学是研究数量" in result["answer"]
        
        # 验证方法被正确调用
        mock_chat_completion.assert_called_once()