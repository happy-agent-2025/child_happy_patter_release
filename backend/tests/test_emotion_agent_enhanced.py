import pytest
from unittest.mock import patch, MagicMock
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
    
    @patch('utils.openai_client.openai_client')
    def test_analyze_emotion(self, mock_openai):
        """测试情绪分析功能"""
        agent = EmotionAgent()
        
        # 模拟OpenAI响应
        mock_openai.chat_completion.return_value = """情绪类型: 开心
情绪强度: 高
分析理由: 孩子明确表达了"太高兴了"，并使用感叹号强调情绪强度，满分成绩带来强烈的积极情绪体验。
应对建议: 及时给予肯定和表扬，分享孩子的喜悦，同时鼓励继续保持努力，强化积极行为。"""
        
        content = "我今天考试得了满分，太高兴了！"
        result = agent.analyze_emotion(content)
        
        assert result["emotion"] == "开心"
        assert result["intensity"] == "高"
        assert "太高兴了" in result["reason"] or "满分" in result["reason"]
        # 修改断言以匹配实际响应
        assert "肯定和表扬" in result["suggestion"] or "分享" in result["suggestion"]
    
    @patch('utils.openai_client.openai_client')
    def test_provide_emotional_support(self, mock_openai):
        """测试情感支持功能"""
        agent = EmotionAgent()
        
        # 模拟OpenAI响应
        mock_openai.chat_completion.return_value = "我能理解你的开心，继续保持这种积极的心态哦！"
        
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
    
    def test_process_request_with_emotion_type(self):
        """测试带指定情绪类型的请求处理"""
        agent = EmotionAgent()
        
        with patch.object(agent, 'provide_emotional_support') as mock_support:
            mock_support.return_value = "情感支持响应"
            
            request = {
                "content": "我很难过",
                "emotion_type": "难过"
            }
            
            result = agent.process_request(request)
            
            assert result["agent"] == "emotion"
            assert result["content"] == "我很难过"
            assert result["emotion_analysis"]["emotion"] == "难过"
            assert result["response"] == "情感支持响应"
            assert result["status"] == "processed"
    
    def test_process_request_without_emotion_type(self):
        """测试不带指定情绪类型的请求处理"""
        agent = EmotionAgent()
        
        with patch.object(agent, 'analyze_emotion') as mock_analyze:
            mock_analyze.return_value = {
                "emotion": "难过",
                "intensity": "中",
                "reason": "表达了负面情感",
                "suggestion": "给予安慰"
            }
            
            with patch.object(agent, 'provide_emotional_support') as mock_support:
                mock_support.return_value = "情感支持响应"
                
                request = {
                    "content": "我很难过",
                    "user_id": 123
                }
                
                result = agent.process_request(request)
                
                assert result["agent"] == "emotion"
                assert result["user_id"] == 123
                assert result["content"] == "我很难过"
                assert result["emotion_analysis"]["emotion"] == "难过"
                assert result["response"] == "情感支持响应"
                assert result["status"] == "processed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])