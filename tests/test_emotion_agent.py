import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.emotion_agent import EmotionAgent


class TestEmotionAgent:
    """测试情感代理模块"""

    def test_init(self):
        """测试EmotionAgent初始化"""
        agent = EmotionAgent()
        assert agent is not None
        assert hasattr(agent, 'system_prompt')
        assert hasattr(agent, 'emotion_types')

    @patch('utils.openai_client.openai_client.chat_completion')
    def test_analyze_emotion(self, mock_chat_completion):
        """测试情绪分析功能"""
        # 设置模拟返回值
        mock_chat_completion.return_value = """情绪类型: 开心
情绪强度: 高
分析理由: 用户表达了对学习的兴趣和兴奋"""

        agent = EmotionAgent()
        result = agent.analyze_emotion("我今天学到了很多新知识，好开心！")

        # 验证结果
        assert result["emotion"] == "开心"
        assert result["intensity"] == "高"
        assert "学习的兴趣" in result["reason"]
        
        # 验证方法被正确调用
        mock_chat_completion.assert_called_once()

    @patch('utils.openai_client.openai_client.chat_completion')
    def test_provide_emotional_support(self, mock_chat_completion):
        """测试提供情感支持功能"""
        # 设置模拟返回值
        mock_chat_completion.return_value = "我能感受到你的开心！学习新知识确实是一件令人兴奋的事情。"

        agent = EmotionAgent()
        emotion_analysis = {
            "emotion": "开心",
            "intensity": "高",
            "reason": "用户表达了对学习的兴趣和兴奋"
        }
        result = agent.provide_emotional_support("我今天学到了很多新知识，好开心！", emotion_analysis)

        # 验证结果
        assert "我能感受到你的开心" in result
        assert "学习新知识" in result
        
        # 验证方法被正确调用
        mock_chat_completion.assert_called_once()

    @patch('agents.emotion_agent.EmotionAgent.analyze_emotion')
    @patch('agents.emotion_agent.EmotionAgent.provide_emotional_support')
    def test_process_request(self, mock_provide_support, mock_analyze_emotion):
        """测试处理请求功能"""
        # 设置模拟返回值
        mock_analyze_emotion.return_value = {
            "emotion": "开心",
            "intensity": "高",
            "reason": "用户表达了对学习的兴趣和兴奋"
        }
        mock_provide_support.return_value = "我能感受到你的开心！学习新知识确实是一件令人兴奋的事情。"

        agent = EmotionAgent()
        request = {
            "content": "我今天学到了很多新知识，好开心！",
            "user_id": "test_user_1"
        }
        result = agent.process_request(request)

        # 验证结果
        assert result["agent"] == "emotion"
        assert result["user_id"] == "test_user_1"
        assert result["content"] == "我今天学到了很多新知识，好开心！"
        assert "emotion_analysis" in result
        assert "response" in result
        
        # 验证方法被正确调用
        mock_analyze_emotion.assert_called_once_with("我今天学到了很多新知识，好开心！")
        mock_provide_support.assert_called_once()