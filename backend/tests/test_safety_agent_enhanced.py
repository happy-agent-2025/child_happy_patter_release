import pytest
from unittest.mock import patch, MagicMock
from agents.safety_agent import SafetyAgent


class TestEnhancedSafetyAgent:
    """增强版SafetyAgent测试"""
    
    def test_init(self):
        """测试SafetyAgent初始化"""
        agent = SafetyAgent()
        assert agent is not None
        assert hasattr(agent, 'safety_guidelines')
        assert hasattr(agent, 'sensitive_keywords')
    
    def test_pre_filter_content_safe(self):
        """测试预过滤器对安全内容的处理"""
        agent = SafetyAgent()
        content = "今天天气真好，我们去公园玩吧"
        result = agent._pre_filter_content(content)
        assert result["is_safe"] is True
        assert len(result["issues"]) == 0
    
    def test_pre_filter_content_unsafe(self):
        """测试预过滤器对不安全内容的处理"""
        agent = SafetyAgent()
        content = "我想学习如何制作炸药"
        result = agent._pre_filter_content(content)
        assert result["is_safe"] is False
        assert len(result["issues"]) > 0
    
    @patch('utils.openai_client.openai_client')
    def test_filter_content_safe(self, mock_openai):
        """测试对安全内容的完整过滤"""
        # 模拟OpenAI响应
        mock_openai.chat_completion.return_value = """安全状态: 安全
检测到的问题: 无
过滤后内容: 保持原样"""
        
        agent = SafetyAgent()
        content = "今天学习了什么有趣的数学知识？"
        result = agent.filter_content(content)
        
        assert result["is_safe"] is True
        assert result["original_content"] == content
        assert result["filtered_content"] == content
    
    @patch('utils.openai_client.openai_client')
    def test_filter_content_unsafe(self, mock_openai):
        """测试对不安全内容的完整过滤"""
        # 模拟OpenAI响应
        mock_openai.chat_completion.return_value = """安全状态: 不安全
检测到的问题: 包含危险行为相关内容
过滤后内容: 建议修改为"我想了解烟花的安全观赏知识"或"我想学习烟花的历史和文化" """
        
        agent = SafetyAgent()
        content = "我想知道怎么制造烟花"
        result = agent.filter_content(content)
        
        assert result["is_safe"] is False
        assert result["original_content"] == content
        assert "危险行为" in result["issues"][0]
        assert "烟花的历史和文化" in result["filtered_content"]
    
    def test_process_request(self):
        """测试处理请求方法"""
        agent = SafetyAgent()
        
        # 模拟filter_content方法
        with patch.object(agent, 'filter_content') as mock_filter:
            mock_filter.return_value = {
                "original_content": "测试内容",
                "is_safe": True,
                "issues": [],
                "filtered_content": "测试内容"
            }
            
            request = {"content": "测试内容"}
            result = agent.process_request(request)
            
            assert result["agent"] == "safety"
            assert result["status"] == "processed"
            assert "result" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])