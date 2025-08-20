from typing import Dict, Any, List


class SafetyAgent:
    """
    安全代理，负责内容过滤和安全审查
    """
    
    def __init__(self):
        # 初始化敏感词列表
        self.sensitive_words = [
            "暴力", "色情", "危险", "伤害", "自杀"
        ]
    
    def filter_content(self, content: str) -> Dict[str, Any]:
        """
        过滤内容中的敏感信息
        """
        filtered_content = content
        detected_words = []
        
        for word in self.sensitive_words:
            if word in content:
                detected_words.append(word)
                # 简单替换敏感词
                filtered_content = filtered_content.replace(word, "*" * len(word))
        
        return {
            "original_content": content,
            "filtered_content": filtered_content,
            "detected_words": detected_words,
            "is_safe": len(detected_words) == 0
        }
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理安全审查请求
        """
        content = request.get("content", "")
        filter_result = self.filter_content(content)
        
        return {
            "agent": "safety",
            "result": filter_result,
            "status": "processed"
        }