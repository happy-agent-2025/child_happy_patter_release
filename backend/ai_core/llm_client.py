"""
统一的LLM客户端接口

支持多种LLM提供商，包括OpenAI兼容API、Ollama等
提供统一的调用接口，支持每个agent独立配置
"""

import openai
import requests
import json
from typing import List, Dict, Any, Optional
from utils.util import Util


class LLMClient:
    """
    统一的LLM客户端，支持多种提供商
    """

    _instance: Optional['LLMClient'] = None

    def __new__(cls) -> 'LLMClient':
        if cls._instance is None:
            cls._instance = super(LLMClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # 延迟加载配置，避免模块导入时的命令行参数问题
        self.config = None
        self._initialized = True

    def _ensure_config_loaded(self):
        """确保配置已加载"""
        if self.config is None:
            self.config = Util.get_config()

    def _get_provider_config(self, provider: str) -> Dict[str, Any]:
        """获取指定提供商的配置"""
        self._ensure_config_loaded()
        llm_config = self.config.get("LLM", {})
        return llm_config.get(provider, {})

    def _call_openai(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ) -> str:
        """调用OpenAI兼容API"""
        provider_config = self._get_provider_config("openai")

        # 优先使用agent特定的配置，如果没有则使用provider默认配置
        final_api_key = api_key if api_key is not None else provider_config.get("api_key", "")
        final_base_url = base_url if base_url is not None else provider_config.get("base_url", "")

        client = openai.OpenAI(
            api_key=final_api_key,
            base_url=final_base_url
        )

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"调用OpenAI兼容API时出错: {str(e)}"

    def _call_ollama(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        base_url: Optional[str] = None
    ) -> str:
        """调用Ollama API"""
        provider_config = self._get_provider_config("ollama")
        # 优先使用agent特定的配置，如果没有则使用provider默认配置
        final_base_url = base_url if base_url is not None else provider_config.get("base_url", "http://localhost:11434")

        # 构建prompt
        prompt = ""
        system_message = None
        user_messages = []

        for message in messages:
            if message.get('role') == 'system':
                system_message = message.get('content', '')
            elif message.get('role') == 'user':
                user_messages.append(message.get('content', ''))
            elif message.get('role') == 'assistant':
                user_messages.append(message.get('content', ''))

        # 使用简单的对话格式
        if system_message:
            prompt += f"System: {system_message}\n\n"

        for i, content in enumerate(user_messages):
            if i % 2 == 0:  # 用户消息
                prompt += f"User: {content}\n\nAssistant: "
            else:  # 助手消息
                prompt += f"{content}\n\n"

        # 构建请求数据
        data = {
            'model': model,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': temperature
            }
        }

        if max_tokens:
            data['options']['num_predict'] = max_tokens

        try:
            url = f"{final_base_url}/api/generate"
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=data, headers=headers, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get('response', '')
        except Exception as e:
            return f"调用Ollama API时出错: {str(e)}"

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        provider: str = "openai",
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ) -> str:
        """
        统一的聊天补全接口

        Args:
            messages: 消息列表
            provider: 提供商名称 (openai, ollama)
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大令牌数
            api_key: 可选的API密钥（优先于provider配置）
            base_url: 可选的API基础URL（优先于provider配置）

        Returns:
            模型回复内容
        """
        try:
            if provider == "openai":
                return self._call_openai(messages, model, temperature, max_tokens, api_key, base_url)
            elif provider == "ollama":
                return self._call_ollama(messages, model, temperature, max_tokens, base_url)
            else:
                return f"不支持的LLM提供商: {provider}"
        except Exception as e:
            return f"调用{provider} API时出错: {str(e)}"


# 全局LLM客户端实例
llm_client = LLMClient()