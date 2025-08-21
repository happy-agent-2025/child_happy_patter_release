from typing import Dict, Any, List


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
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理记忆相关的请求
        
        Args:
            request: 请求信息
            
        Returns:
            处理结果
        """
        action = request.get("action", "get_context")
        
        if action == "store":
            conversation = request.get("conversation", {})
            self.store_conversation(conversation)
            return {
                "agent": "memory",
                "action": "store",
                "status": "success",
                "message": "对话已存储"
            }
        elif action == "get_history":
            limit = request.get("limit", 10)
            history = self.get_conversation_history(limit)
            return {
                "agent": "memory",
                "action": "get_history",
                "status": "success",
                "history": history
            }
        elif action == "clear":
            self.clear_conversation_history()
            return {
                "agent": "memory",
                "action": "clear",
                "status": "success",
                "message": "对话历史已清空"
            }
        else:  # 默认获取上下文
            context = self.get_context()
            return {
                "agent": "memory",
                "action": "get_context",
                "status": "success",
                "context": context
            }