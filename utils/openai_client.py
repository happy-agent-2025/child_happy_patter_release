import openai
from config.settings import settings
from typing import List, Dict, Any, Optional


class OpenAIClient:
    """
    OpenAI客户端封装类
    """
    
    _instance: Optional['OpenAIClient'] = None
    
    def __new__(cls) -> 'OpenAIClient':
        if cls._instance is None:
            cls._instance = super(OpenAIClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # 初始化OpenAI客户端
        self.client = openai.OpenAI(
            api_key=settings.openai_api_key or "sk-xxx",  # 默认值避免报错
            base_url=settings.openai_base_url
        )
        self._initialized = True
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        调用OpenAI聊天接口
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大令牌数
            
        Returns:
            模型回复内容
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"调用OpenAI API时出错: {str(e)}"


# 全局OpenAI客户端实例
openai_client = OpenAIClient()