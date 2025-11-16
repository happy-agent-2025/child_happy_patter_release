from typing import Dict, Any, List
from core.openai_client import openai_client


class MemoryAgent:
    """
    记忆代理，负责对话历史存储和上下文管理
    """
    
    def __init__(self):
        # 初始化对话历史存储
        self.conversation_history: List[Dict[str, Any]] = []
    
    def store_conversation(self, conversation: Dict[str, Any]) -> None:
        """
        存储对话历史
        
        Args:
            conversation: 包含对话信息的字典
        """
        self.conversation_history.append(conversation)
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的对话历史
        
        Args:
            limit: 返回的对话历史条数限制
            
        Returns:
            最近的对话历史列表
        """
        # 返回最近的对话历史，最多limit条
        return self.conversation_history[-limit:] if self.conversation_history else []
    
    def clear_conversation_history(self) -> None:
        """
        清空对话历史
        """
        self.conversation_history.clear()
    
    def get_context(self) -> Dict[str, Any]:
        """
        获取当前对话上下文
        
        Returns:
            包含上下文信息的字典
        """
        return {
            "history_count": len(self.conversation_history),
            "recent_history": self.get_conversation_history(3)
        }
    
    def summarize_conversation_history(self, user_id: str) -> str:
        """
        使用OpenAI总结对话历史
        
        Args:
            user_id: 用户ID
            
        Returns:
            对话历史摘要
        """
        # 获取最近的对话历史
        history = self.get_conversation_history(10)
        
        if not history:
            return "暂无对话历史"
        
        # 构造对话历史文本
        history_text = ""
        for i, conv in enumerate(history, 1):
            agent = conv.get("agent", "unknown")
            content = conv.get("content", conv.get("question", "无内容"))
            response = conv.get("response", conv.get("answer", "无回应"))
            history_text += f"{i}. 用户与{agent}代理对话:\n"
            history_text += f"   用户: {content}\n"
            history_text += f"   回应: {response}\n\n"
        
        # 构造提示词
        prompt = f"""
        请为以下儿童用户(ID: {user_id})的对话历史生成一个简洁摘要：
        
        {history_text}
        
        摘要要求：
        1. 突出孩子关心的主要话题
        2. 总结孩子的兴趣点
        3. 保持积极正面的语调
        4. 用易于理解的语言
        5. 控制在100字以内
        """
        
        messages = [
            {"role": "system", "content": "你是一个专业的对话历史总结助手。"},
            {"role": "user", "content": prompt}
        ]
        
        # 调用OpenAI API生成摘要
        response = openai_client.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=150
        )
        
        return response
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理记忆相关的请求
        
        Args:
            request: 请求信息
            
        Returns:
            处理结果
        """
        action = request.get("action", "get_context")
        user_id = request.get("user_id", "unknown_user")
        
        if action == "store":
            conversation = request.get("conversation", {})
            conversation["user_id"] = user_id
            self.store_conversation(conversation)
            return {
                "agent": "memory",
                "action": "store",
                "status": "processed",
                "message": "对话已存储"
            }
        elif action == "get_history":
            limit = request.get("limit", 10)
            history = self.get_conversation_history(limit)
            return {
                "agent": "memory",
                "action": "get_history",
                "status": "processed",
                "history": history
            }
        elif action == "get_summary":
            summary = self.summarize_conversation_history(user_id)
            return {
                "agent": "memory",
                "action": "get_summary",
                "status": "processed",
                "summary": summary
            }
        elif action == "clear":
            self.clear_conversation_history()
            return {
                "agent": "memory",
                "action": "clear",
                "status": "processed",
                "message": "对话历史已清空"
            }
        else:  # 默认获取上下文
            context = self.get_context()
            return {
                "agent": "memory",
                "action": "get_context",
                "status": "processed",
                "context": context
            }