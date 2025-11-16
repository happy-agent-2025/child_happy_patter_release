import openai
from config.settings import settings
from typing import List, Dict, Any, Optional
from core.ollama_client import ollama_client


class OpenAIClient:
    """
    OpenAI客户端封装类，支持Ollama本地模型
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
            
        # 检查是否使用Ollama
        self.use_ollama = getattr(settings, 'use_ollama', False)
        
        if self.use_ollama:
            # 使用Ollama客户端
            self.ollama_client = ollama_client
        else:
            # 使用OpenAI客户端
            self.client = openai.OpenAI(
                api_key=settings.openai_api_key or "sk-xxx",  # 默认值避免报错
                base_url=settings.openai_base_url
            )
        
        self._initialized = True
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "qwen-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        调用聊天接口，支持OpenAI和Ollama
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大令牌数
            
        Returns:
            模型回复内容
        """
        try:
            if self.use_ollama:
                # 使用Ollama客户端
                ollama_model = getattr(settings, 'ollama_default_model', 'emotion_lora')
                return self.ollama_client.chat_completion(
                    messages=messages,
                    model=ollama_model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            else:
                # 使用OpenAI客户端
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content or ""
        except Exception as e:
            if self.use_ollama:
                return f"调用Ollama API时出错: {str(e)}"
            else:
                return f"调用OpenAI API时出错: {str(e)}"


# 全局OpenAI客户端实例
openai_client = OpenAIClient()