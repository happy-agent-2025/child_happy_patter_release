import pytest
from agents.edu_agent import EduAgent


class TestEduAgent:
    """测试EduAgent类"""
    
    def test_init(self):
        """测试EduAgent初始化"""
        agent = EduAgent()
        assert agent is not None
        assert isinstance(agent.knowledge_base, dict)
    
    def test_answer_question(self):
        """测试问题回答功能"""
        agent = EduAgent()
        
        # 测试已知问题
        math_question = "什么是数学？"
        answer = agent.answer_question(math_question)
        print(answer)
        assert "数学是研究数量、结构、空间以及变化等概念的一门学科" in answer
        
        # 测试未知问题
        unknown_question = "什么是物理？"
        answer = agent.answer_question(unknown_question)
        print(answer)
        assert "我还在学习中" in answer
    
    def test_process_request(self):
        """测试请求处理功能"""
        agent = EduAgent()
        request = {"content": "什么是语文？"}
        result = agent.process_request(request)
        print(result)
        
        assert result["agent"] == "edu"
        assert result["question"] == "什么是语文？"
        assert result["status"] == "processed"
        assert "answer" in result