import pytest
from agents.emotion_agent import EmotionAgent


class TestEnhancedEmotionAgent:
    """增强版EmotionAgent测试"""
    
    def test_init(self):
        """测试EmotionAgent初始化"""
        agent = EmotionAgent()
        assert agent is not None
        assert hasattr(agent, 'system_prompt')
        assert hasattr(agent, 'emotions')
        # 验证情绪字典包含基本情绪
        assert "开心" in agent.emotions
        assert "难过" in agent.emotions
    
    def test_analyze_emotion(self):
        """测试情绪分析功能"""
        agent = EmotionAgent()
        content = "我今天考试得了满分，太高兴了！"
        result = agent.analyze_emotion(content)
        
        # 验证返回结果结构
        assert "emotion" in result
        assert "intensity" in result
        assert "reason" in result
        assert "suggestion" in result
        assert isinstance(result["emotion"], str)
        assert isinstance(result["intensity"], str)
        assert isinstance(result["reason"], str)
        assert isinstance(result["suggestion"], str)
        assert len(result["emotion"]) > 0
        assert len(result["intensity"]) > 0
    
    def test_provide_emotional_support(self):
        """测试情感支持功能"""
        agent = EmotionAgent()
        content = "我今天考试得了满分，太高兴了！"
        emotion_analysis = {
            "emotion": "开心",
            "intensity": "高",
            "reason": "表达了积极的情感",
            "suggestion": "分享这份快乐"
        }
        
        support = agent.provide_emotional_support(content, emotion_analysis)
        assert isinstance(support, str)
        assert len(support) > 0
        # 确保返回了情感支持内容
        assert "开心" in support or "高兴" in support
    
    def test_process_request_with_emotion_type(self):
        """测试带指定情绪类型的请求处理"""
        agent = EmotionAgent()
        
        request = {
            "content": "我很难过",
            "emotion_type": "难过"
        }
        
        result = agent.process_request(request)
        
        assert result["agent"] == "emotion"
        assert result["content"] == "我很难过"
        assert result["emotion_analysis"]["emotion"] == "难过"
        assert result["status"] == "processed"
        assert "response" in result
        assert isinstance(result["response"], str)
        assert len(result["response"]) > 0
    
    def test_process_request_without_emotion_type(self):
        """测试不带指定情绪类型的请求处理"""
        agent = EmotionAgent()
        
        request = {
            "content": "我今天考试得了满分，太高兴了！",
            "user_id": 123
        }
        
        result = agent.process_request(request)
        
        assert result["agent"] == "emotion"
        assert result["content"] == "我今天考试得了满分，太高兴了！"
        assert result["status"] == "processed"
        assert "emotion_analysis" in result
        assert "response" in result
        assert isinstance(result["emotion_analysis"], dict)
        assert isinstance(result["response"], str)
        assert len(result["response"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])