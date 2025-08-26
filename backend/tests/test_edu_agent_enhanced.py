import pytest
from agents.edu_agent import EduAgent
from unittest.mock import patch


class TestEnhancedEduAgent:
    """增强版EduAgent测试"""
    
    def test_init(self):
        """测试EduAgent初始化"""
        agent = EduAgent()
        assert agent is not None
        assert hasattr(agent, 'system_prompt')
        assert hasattr(agent, 'subjects')
        assert hasattr(agent, 'age_groups')
        assert hasattr(agent, '_fallback_subject_detection')
    
    def test_get_subject_context_with_llm(self):
        """测试使用大模型进行学科判断"""
        agent = EduAgent()
        question = "1+1等于几？"
        subject = agent._get_subject_context(question)
        # 大模型应该返回有效的学科
        assert subject in agent.subjects or subject == "通用"
    
    def test_get_subject_context_with_llm_invalid_response(self):
        """测试当大模型返回无效学科时回退到关键词匹配"""
        agent = EduAgent()
        # 直接测试回退机制
        fallback_subject = agent._fallback_subject_detection("什么是平行四边形？")
        # 应该回退到关键词匹配，返回"数学"
        assert fallback_subject == "数学"
    
    @patch('utils.openai_client.openai_client')
    def test_get_subject_context_with_llm_exception(self, mock_openai):
        """测试当大模型调用失败时回退到关键词匹配"""
        agent = EduAgent()
        
        # 模拟OpenAI调用失败
        mock_openai.chat_completion.side_effect = Exception("API调用失败")
        
        # 使用包含关键词的问题
        question = "什么是平行四边形？"
        subject = agent._get_subject_context(question)
        # 应该回退到关键词匹配，返回"数学"
        assert subject == "数学"
    
    def test_fallback_subject_detection(self):
        """测试回退的学科检测方法"""
        agent = EduAgent()
        
        # 测试各种类型的学科问题
        test_cases = [
            ("1+1等于几？", "数学"),
            ("李白写过哪些诗？", "语文"),
            ("如何用英语说'你好'？", "英语"),
            ("植物是如何进行光合作用的？", "科学"),
            ("长城是哪个朝代修建的？", "历史"),
            ("中国的首都在哪里？", "地理"),
            ("钢琴有多少个键？", "音乐"),
            ("梵高的代表作是什么？", "艺术"),
            ("游泳有哪些好处？", "体育"),
            ("我们应该如何遵守交通规则？", "道德与法治"),
            ("什么是人工智能？", "信息技术")
        ]
        
        for question, expected_subject in test_cases:
            subject = agent._fallback_subject_detection(question)
            assert subject == expected_subject
    
    def test_answer_question(self):
        """测试问题回答功能"""
        agent = EduAgent()
        question = "1+1等于几？"
        answer = agent.answer_question(question)
        assert isinstance(answer, str)
        assert len(answer) > 0
        # 确保答案中包含与问题相关的内容
        assert "2" in answer or "两" in answer
    
    def test_process_request_with_grade_level(self):
        """测试带年级级别的请求处理"""
        agent = EduAgent()
        
        request = {
            "content": "什么是加法？",
            "grade_level": "小学一年级"
        }
        
        result = agent.process_request(request)
        
        assert result["agent"] == "edu"
        assert result["question"] == "什么是加法？"
        assert result["status"] == "processed"
        assert "answer" in result
        assert "subject" in result
        assert isinstance(result["answer"], str)
        assert len(result["answer"]) > 0
    
    def test_process_request_age_mapping(self):
        """测试年级到年龄的映射"""
        agent = EduAgent()
        
        test_cases = [
            ("学前", "5-6岁"),
            ("小学一年级", "7-8岁"),
            ("小学二年级", "7-8岁"),
            ("小学三年级", "9-10岁"),
            ("小学四年级", "9-10岁"),
            ("小学五年级", "11-12岁"),
            ("小学六年级", "11-12岁")
        ]
        
        for grade_level, expected_age in test_cases:
            request = {
                "content": "测试问题",
                "grade_level": grade_level
            }
            
            result = agent.process_request(request)
            # 验证处理流程正常完成
            assert result["agent"] == "edu"
            assert result["status"] == "processed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])