from typing import Dict, Any


class EduAgent:
    """
    教育代理，负责教育内容问答
    """
    
    def __init__(self):
        # 初始化教育知识库
        self.knowledge_base = {
            "数学": "数学是研究数量、结构、空间以及变化等概念的一门学科。",
            "语文": "语文是学习语言文字运用的综合性、实践性课程。",
            "英语": "英语是世界上使用最广泛的语言之一。"
        }
    
    def answer_question(self, question: str) -> str:
        """
        回答教育相关问题
        """
        # 简单的关键词匹配回答逻辑
        for subject, answer in self.knowledge_base.items():
            if subject in question:
                return answer
        
        return "我还在学习中，稍后为您解答这个问题。"
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理教育问答请求
        """
        question = request.get("content", "")
        answer = self.answer_question(question)
        
        return {
            "agent": "edu",
            "question": question,
            "answer": answer,
            "status": "processed"
        }