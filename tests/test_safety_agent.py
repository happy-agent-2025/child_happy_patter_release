import pytest
from agents.safety_agent import SafetyAgent


class TestSafetyAgent:
    """测试SafetyAgent类"""
    
    def test_init(self):
        """测试SafetyAgent初始化"""
        agent = SafetyAgent()
        assert agent is not None
        assert isinstance(agent.sensitive_words, list)
    
    def test_filter_content_safe(self):
        """测试安全内容过滤"""
        agent = SafetyAgent()
        content = "今天天气真好"
        result = agent.filter_content(content)
        
        assert result["original_content"] == content
        assert result["filtered_content"] == content
        assert result["detected_words"] == []
        assert result["is_safe"] is True
    
    def test_filter_content_unsafe(self):
        """测试不安全内容过滤"""
        agent = SafetyAgent()
        content = "包含暴力和危险的内容"
        result = agent.filter_content(content)
        
        assert result["original_content"] == content
        assert result["filtered_content"] == "包含**和**的内容"
        assert "暴力" in result["detected_words"]
        assert "危险" in result["detected_words"]
        assert result["is_safe"] is False
    
    def test_process_request(self):
        """测试请求处理功能"""
        agent = SafetyAgent()
        request = {"content": "包含暴力的内容"}
        result = agent.process_request(request)
        
        assert result["agent"] == "safety"
        assert result["status"] == "processed"
        assert "result" in result