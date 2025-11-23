"""
Agent模型管理器

管理每个agent的独立模型配置，提供统一的调用接口
"""

from typing import List, Dict, Any, Optional
from utils.util import Util
from ai_core.llm_client import llm_client


class AgentModelManager:
    """
    Agent模型管理器，负责管理每个agent的模型配置
    """

    _instance: Optional['AgentModelManager'] = None

    def __new__(cls) -> 'AgentModelManager':
        if cls._instance is None:
            cls._instance = super(AgentModelManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # 延迟加载配置
        self.config = None
        self._initialized = True

    def _ensure_config_loaded(self):
        """确保配置已加载"""
        if self.config is None:
            self.config = Util.get_config()

    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        获取指定agent的模型配置

        Args:
            agent_name: agent名称

        Returns:
            agent配置字典
        """
        self._ensure_config_loaded()

        # 获取agents配置节
        agents_config = self.config.get("agents", {})

        # 获取默认配置
        default_config = agents_config.get("default", {
            "provider": "openai",
            "model": "deepseek-chat",
            "temperature": 0.7,
            "max_tokens": 500
        })

        # 获取指定agent的配置，如果没有则使用默认配置
        agent_config = agents_config.get(agent_name, default_config)

        # 确保配置包含所有必要字段
        base_config = {
            "provider": agent_config.get("provider", default_config["provider"]),
            "model": agent_config.get("model", default_config["model"]),
            "temperature": agent_config.get("temperature", default_config["temperature"]),
            "max_tokens": agent_config.get("max_tokens", default_config["max_tokens"])
        }

        # 获取provider的完整配置信息
        provider_name = base_config["provider"]
        llm_config = self.config.get("LLM", {})
        provider_config = llm_config.get(provider_name, {})

        # 合并配置，提供完整的LLM调用信息
        return {
            **base_config,
            "api_key": provider_config.get("api_key", ""),
            "base_url": provider_config.get("base_url", ""),
            "provider_type": provider_config.get("type", "")
        }

    def chat_completion(
        self,
        agent_name: str,
        messages: List[Dict[str, str]]
    ) -> str:
        """
        为指定agent调用聊天补全

        Args:
            agent_name: agent名称
            messages: 消息列表

        Returns:
            模型回复内容
        """
        # 获取agent配置
        agent_config = self.get_agent_config(agent_name)

        # 使用配置调用LLM客户端
        return llm_client.chat_completion(
            messages=messages,
            provider=agent_config["provider"],
            model=agent_config["model"],
            temperature=agent_config["temperature"],
            max_tokens=agent_config["max_tokens"]
        )


# 全局Agent模型管理器实例
agent_model_manager = AgentModelManager()