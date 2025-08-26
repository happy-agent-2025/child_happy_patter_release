import pytest
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
        assert hasattr(agent, 'emotions')

    def test_analyze_emotion(self):
        """测试情绪分析功能"""
        agent = EmotionAgent()
        result = agent.analyze_emotion("我今天学到了很多新知识，好开心！")

        # 验证结果
        assert "emotion" in result
        assert "intensity" in result
        assert "reason" in result
        assert result["emotion"] is not None

    def test_provide_emotional_support(self):
        """测试提供情感支持功能"""
        agent = EmotionAgent()
        emotion_analysis = {
            "emotion": "开心",
            "intensity": "高",
            "reason": "学习了新知识"
        }
        result = agent.provide_emotional_support("我今天学到了很多新知识，好开心！", emotion_analysis)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_process_request(self):
        """测试处理请求功能"""
        agent = EmotionAgent()
        request = {
            "content": "我今天学到了很多新知识，好开心！",
            "user_id": "test_user"
        }
        result = agent.process_request(request)
        assert "agent" in result
        assert "user_id" in result
        assert "content" in result
        assert "emotion_analysis" in result
        assert "response" in result
        assert "status" in result
        assert result["agent"] == "emotion"
        assert result["status"] == "processed"