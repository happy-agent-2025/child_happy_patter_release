from typing import Dict, Any
from utils.openai_client import openai_client


class EduAgent:
    """
    教育代理，负责教育内容问答
    """
    
    def __init__(self):
        # 定义教育场景的系统提示
        self.system_prompt = """
        你是一个专门为儿童设计的教育AI助手，你的职责是：
        1. 用简单易懂的语言回答问题
        2. 耐心、友好地与孩子交流
        3. 根据孩子的年龄调整回答的复杂程度
        4. 鼓励孩子思考和探索
        5. 在回答中加入趣味性元素
        6. 确保内容准确、科学
        7. 避免使用复杂术语，必要时进行解释
        """
    
    def answer_question(self, question: str, user_info: Dict[str, Any] = None) -> str:
        """
        使用OpenAI智能回答教育相关问题
        """
        if user_info is None:
            user_info = {}
            
        user_age = user_info.get("age", "6-12岁")
        user_grade = user_info.get("grade", "小学")
        
        # 构造提示词
        prompt = f"""
        用户是一个{user_age}的孩子，正在{user_grade}学习。
        他提出了一个问题: "{question}"
        
        请根据以下要求回答：
        1. 使用适合该年龄段的语言和例子
        2. 回答要准确、科学
        3. 可以适当增加趣味性
        4. 鼓励孩子继续探索和学习
        5. 如果问题不清晰，可以询问更多细节
        """
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # 调用OpenAI API进行教育问答
        response = openai_client.chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理教育问答请求
        """
        question = request.get("content", "")
        user_info = {
            "user_id": request.get("user_id", "unknown_user"),
            "age": request.get("age", "6-12岁"),
            "grade": request.get("grade", "小学")
        }
        
        answer = self.answer_question(question, user_info)
        
        return {
            "agent": "edu",
            "question": question,
            "answer": answer,
            "status": "processed"
        }