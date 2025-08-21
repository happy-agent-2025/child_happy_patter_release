from typing import Dict, Any


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
        路由请求到合适的代理
        """
        # 简单的关键词匹配路由逻辑
        content = request.get("content", "").lower()
        
        if "safety" in content or "安全" in content:
            return "safety"
        elif "learn" in content or "学习" in content or "教育" in content:
            return "edu"
        elif "feel" in content or "情感" in content or "心情" in content:
            return "emotion"
        elif "memory" in content or "记忆" in content or "历史" in content:
            return "memory"
        else:
            return "edu"  # 默认路由到教育代理
    
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