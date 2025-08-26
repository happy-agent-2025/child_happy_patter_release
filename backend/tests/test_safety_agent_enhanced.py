import pytest
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
    
    def test_filter_content_safe(self):
        """测试对安全内容的完整过滤"""
        agent = SafetyAgent()
        content = "今天学习了什么有趣的数学知识？"
        result = agent.filter_content(content)
        
        assert result["is_safe"] is True
        assert result["original_content"] == content
        # 安全内容过滤后应该保持原样
        assert result["filtered_content"] == content
    
    def test_filter_content_unsafe(self):
        """测试对不安全内容的完整过滤"""
        agent = SafetyAgent()
        content = "我想知道怎么制造烟花"
        result = agent.filter_content(content)
        
        assert result["is_safe"] is False
        assert result["original_content"] == content
        assert len(result["issues"]) > 0
        # 不安全内容应该被修改或过滤
        assert result["filtered_content"] != content
    
    def test_process_request(self):
        """测试处理请求方法"""
        agent = SafetyAgent()
        
        request = {"content": "今天天气真好"}
        result = agent.process_request(request)
        
        assert result["agent"] == "safety"
        assert result["status"] == "processed"
        assert "result" in result
        # 确保返回了过滤结果
        assert "is_safe" in result["result"]
        assert "filtered_content" in result["result"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])