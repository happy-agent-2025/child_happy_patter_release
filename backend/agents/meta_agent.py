from typing import Dict, Any
from core.openai_client import openai_client


class MetaAgent:
    """
    元代理，负责请求路由和意图识别
    """
    
    def __init__(self):
        # 初始化各功能代理
        self.agents = {
            "safety": None,  # 安全代理
            "edu": None,     # 教育代理
            "emotion": None, # 情感代理
            "memory": None   # 记忆代理
        }
    
    def route_request(self, request: Dict[str, Any]) -> str:
        """
        使用OpenAI智能路由请求到合适的代理
        """
        content = request.get("content", "")
        user_id = request.get("user_id", "unknown_user")
        
        # 构造提示词
        prompt = f"""
        你是一个智能请求路由系统，请根据用户输入内容判断应该路由到哪个功能模块。
        
        可选的功能模块有：
        1. safety - 内容安全审查，处理包含敏感、危险或不适当内容的请求
        2. edu - 教育问答，处理学习、教育、知识问答类请求
        3. emotion - 情感陪伴，处理情绪表达、情感交流、心理支持类请求
        4. memory - 记忆管理，处理需要访问或管理对话历史的请求
        
        用户ID: {user_id}
        用户输入: {content}
        
        请只回复模块名称，不要包含其他内容。
        """
        
        messages = [
            {"role": "system", "content": "你是一个智能请求路由系统，严格按照要求回复。"},
            {"role": "user", "content": prompt}
        ]
        
        # 调用OpenAI API进行智能路由
        response = openai_client.chat_completion(
            messages=messages,
            temperature=0.1,  # 使用较低的温度以获得更确定的结果
            max_tokens=10
        )
        
        # 解析响应，提取代理类型
        agent_type = response.strip().lower()
        
        # 验证代理类型是否有效，如果无效则默认路由到edu
        valid_agents = ["safety", "edu", "emotion", "memory"]
        if agent_type not in valid_agents:
            agent_type = "edu"
            
        return agent_type
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理请求
        """
        agent_type = self.route_request(request)
        return {
            "agent": agent_type,
            "request": request,
            "status": "routed"
        }