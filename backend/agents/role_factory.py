"""
智能体工厂系统 - 动态智能体创建和管理

支持动态创建角色智能体、管理智能体生命周期、
集成mem0记忆系统，并处理并发和资源管理。
"""

from typing import Dict, Any, List, Optional, Type, Callable
from enum import Enum
import asyncio
import time
import uuid
import json
from datetime import datetime
from dataclasses import dataclass, field
import logging

from core.openai_client import openai_client
from agents.safety_agent import SafetyAgent
from agents.world_agent import world_agent
from agents.emotion_agent import EmotionAgent

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(str, Enum):
    """智能体状态枚举"""

    CREATED = "created"  # 已创建
    INITIALIZING = "initializing"  # 初始化中
    ACTIVE = "active"  # 活跃
    PAUSED = "paused"  # 暂停
    TERMINATED = "terminated"  # 已终止


@dataclass
class RoleConfig:
    """角色配置"""

    name: str
    personality: str
    background: str
    age_group: str  # 幼儿(3-6), 儿童(7-12), 少年(13+)
    prompt_template: str
    world_id: str
    voice_id: Optional[str] = None
    special_abilities: List[str] = field(default_factory=list)
    safety_rules: List[str] = field(default_factory=list)


@dataclass
class AgentInstance:
    """智能体实例"""

    agent_id: str
    role_config: RoleConfig
    state: AgentState
    created_at: datetime
    last_activity: datetime
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    memory_context: Dict[str, Any] = field(default_factory=dict)
    thread_lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class DynamicRoleAgent:
    """
    动态角色智能体

    根据角色配置动态创建的智能体实例，
    具有个性化的回应能力和记忆功能。
    """

    def __init__(self, config: RoleConfig):
        self.config = config
        self.role_id = f"role_{config.name}_{uuid.uuid4().hex[:8]}"
        self.state = AgentState.CREATED
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.conversation_history = []
        self.memory_context = {}
        self.thread_lock = asyncio.Lock()

        # 初始化依赖组件
        self.safety_agent = SafetyAgent()
        self.emotion_agent = EmotionAgent()

        # 生成个性化提示模板
        self.personalized_prompt = self._generate_personalized_prompt()

        logger.info(f"创建角色智能体: {config.name} (ID: {self.role_id})")

    def _generate_personalized_prompt(self) -> str:
        """生成个性化提示模板"""
        base_prompt = f"""
你是{self.config.name}，一个儿童故事角色。

角色设定：
- 性格：{self.config.personality}
- 背景：{self.config.background}
- 年龄组：{self.config.age_group}
- 特殊能力：{', '.join(self.config.special_abilities) if self.config.special_abilities else '无'}

互动规则：
1. 始终保持角色性格特点
2. 使用适合{self.config.age_group}儿童的语言
3. 内容积极向上，有教育意义
4. 互动要有趣且引人入胜
5. 遵循安全规则：{', '.join(self.config.safety_rules) if self.config.safety_rules else '保持友善和积极'}

请以{self.config.name}的身份回应用户。
"""
        return base_prompt

    async def respond_to_message(
        self, message: str, user_id: str, session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        回应用户消息

        Args:
            message: 用户消息
            user_id: 用户ID
            session_id: 会话ID

        Returns:
            响应结果字典
        """
        async with self.thread_lock:
            try:
                self.last_activity = datetime.now()

                # 1. 安全检查
                safety_result = await self._check_safety(message)
                if not safety_result["is_safe"]:
                    return {
                        "success": False,
                        "response": "抱歉，我无法回应这个内容。让我们聊点别的吧！",
                        "safety_check": safety_result,
                        "role_id": self.role_id,
                    }

                # 2. 情感分析
                emotion_result = await self._analyze_emotion(message, user_id)

                # 3. 构建对话上下文
                context = await self._build_conversation_context(
                    message, user_id, session_id
                )

                # 4. 生成回应
                response_content = await self._generate_response(context)

                # 5. 安全检查生成的内容
                response_safety = await self._check_safety(response_content)
                if not response_safety["is_safe"]:
                    response_content = "让我想想怎么说会更合适..."

                # 6. 更新对话历史
                self._update_conversation_history(message, response_content, user_id)

                return {
                    "success": True,
                    "response": response_content,
                    "role_name": self.config.name,
                    "role_id": self.role_id,
                    "emotion_analysis": emotion_result,
                    "safety_check": response_safety,
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                logger.error(f"智能体响应错误: {str(e)}")
                return {
                    "success": False,
                    "response": "抱歉，我现在有点困惑，能再说一遍吗？",
                    "error": str(e),
                    "role_id": self.role_id,
                }

    async def _check_safety(self, content: str) -> Dict[str, Any]:
        """安全检查"""
        try:
            return self.safety_agent.validate_content(content)
        except Exception as e:
            logger.warning(f"安全检查失败: {str(e)}")
            return {"is_safe": False, "reasons": [f"安全检查错误: {str(e)}"]}

    async def _analyze_emotion(self, content: str, user_id: str) -> Dict[str, Any]:
        """情感分析"""
        try:
            request = {"content": content, "user_id": user_id}
            return self.emotion_agent.analyze_emotion(request)
        except Exception as e:
            logger.warning(f"情感分析失败: {str(e)}")
            return {"emotion_type": "neutral", "confidence": 0.5}

    async def _build_conversation_context(
        self, message: str, user_id: str, session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """构建对话上下文"""
        # 获取最近的对话历史
        recent_history = self.conversation_history[-5:]  # 最近5轮对话

        # 构建上下文
        context = {
            "role_config": self.config.__dict__,
            "personalized_prompt": self.personalized_prompt,
            "current_message": message,
            "conversation_history": recent_history,
            "memory_context": self.memory_context,
            "user_id": user_id,
            "session_id": session_id,
        }

        return context

    async def _generate_response(self, context: Dict[str, Any]) -> str:
        """生成回应内容"""
        try:
            # 构建提示
            prompt = f"""
{context['personalized_prompt']}

当前对话历史：
{self._format_conversation_history(context['conversation_history'])}

用户说：{context['current_message']}

请以{self.config.name}的身份回应：
"""

            messages = [
                {
                    "role": "system",
                    "content": "你是一个儿童故事角色，始终保持角色设定。",
                },
                {"role": "user", "content": prompt},
            ]

            # 调用AI模型
            response = openai_client.chat_completion(
                messages=messages, temperature=0.7, max_tokens=500
            )

            return response.strip()

        except Exception as e:
            logger.error(f"AI回应生成失败: {str(e)}")
            return "我很想回应你，但让我想想怎么说..."

    def _format_conversation_history(self, history: List[Dict[str, Any]]) -> str:
        """格式化对话历史"""
        if not history:
            return "这是我们的第一次对话。"

        formatted = []
        for entry in history[-3:]:  # 最近3轮
            formatted.append(f"用户: {entry['user_message']}")
            formatted.append(f"{self.config.name}: {entry['agent_response']}")

        return "\n".join(formatted)

    def _update_conversation_history(
        self, user_message: str, agent_response: str, user_id: str
    ) -> None:
        """更新对话历史"""
        self.conversation_history.append(
            {
                "user_message": user_message,
                "agent_response": agent_response,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # 限制历史记录长度
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-30:]

    async def update_memory_context(self, new_context: Dict[str, Any]) -> None:
        """更新记忆上下文"""
        async with self.thread_lock:
            self.memory_context.update(new_context)
            logger.info(f"更新角色智能体 {self.role_id} 的记忆上下文")

    def get_conversation_summary(self) -> Dict[str, Any]:
        """获取对话摘要"""
        return {
            "role_id": self.role_id,
            "role_name": self.config.name,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "total_conversations": len(self.conversation_history),
            "memory_context_size": len(self.memory_context),
        }

    async def pause(self) -> None:
        """暂停角色智能体"""
        async with self.thread_lock:
            self.state = AgentState.PAUSED
            logger.info(f"角色智能体 {self.role_id} 已暂停")

    async def resume(self) -> None:
        """恢复角色智能体"""
        async with self.thread_lock:
            self.state = AgentState.ACTIVE
            logger.info(f"角色智能体 {self.role_id} 已恢复")

    async def terminate(self) -> None:
        """终止角色智能体"""
        async with self.thread_lock:
            self.state = AgentState.TERMINATED
            self.conversation_history.clear()
            self.memory_context.clear()
            logger.info(f"角色智能体 {self.role_id} 已终止")


class RoleFactory:
    """
    智能体工厂

    负责动态创建、管理和销毁智能体实例，
    提供线程安全的智能体生命周期管理。
    """

    def __init__(self):
        self.active_roles: Dict[str, roleInstance] = {}
        self.role_configs: Dict[str, RoleConfig] = {}
        self.factory_lock = asyncio.Lock()
        self.cleanup_interval = 300  # 5分钟清理一次
        self.last_cleanup = datetime.now()

        logger.info("智能体工厂初始化完成")

    async def create_role_agent(self, config: RoleConfig) -> str:
        """
        创建角色智能体

        Args:
            config: 角色配置

        Returns:
            角色智能体ID
        """
        async with self.factory_lock:
            try:
                # 创建角色智能体实例
                role = DynamicRoleAgent(config)

                # 包装为实例对象
                instance = AgentInstance(
                    agent_id=role.role_id,
                    role_config=config,
                    state=AgentState.CREATED,
                    created_at=datetime.now(),
                    last_activity=datetime.now(),
                )

                # 存储角色智能体
                self.active_roles[role.role_id] = instance
                self.role_configs[role.role_id] = config

                logger.info(f"成功创建角色智能体: {config.name} (ID: {role.role_id})")

                return role.role_id

            except Exception as e:
                logger.error(f"创建角色智能体失败: {str(e)}")
                raise RuntimeError(f"角色智能体创建失败: {str(e)}")

    async def get_role(self, role_id: str) -> Optional[DynamicRoleAgent]:
        """获取角色智能体实例"""
        async with self.factory_lock:
            instance = self.active_roles.get(role_id)
            if instance and instance.state != AgentState.TERMINATED:
                # 返回实际的角色智能体对象
                return DynamicRoleAgent(instance.role_config)
            return None

    async def get_role_info(self, role_id: str) -> Optional[Dict[str, Any]]:
        """获取角色智能体信息"""
        async with self.factory_lock:
            instance = self.active_roles.get(role_id)
            if instance:
                return {
                    "role_id": instance.agent_id,
                    "name": instance.role_config.name,
                    "state": instance.state.value,
                    "created_at": instance.created_at.isoformat(),
                    "last_activity": instance.last_activity.isoformat(),
                    "total_conversations": len(instance.conversation_history),
                }
            return None

    async def list_active_roles(self) -> List[Dict[str, Any]]:
        """列出所有活跃角色智能体"""
        async with self.factory_lock:
            roles = []
            for role_id, instance in self.active_roles.items():
                if instance.state in [AgentState.CREATED, AgentState.ACTIVE]:
                    role_info = await self.get_role_info(role_id)
                    if role_info:
                        roles.append(role_info)
            return roles

    async def pause_role(self, role_id: str) -> bool:
        """暂停角色智能体"""
        async with self.factory_lock:
            instance = self.active_roles.get(role_id)
            if instance:
                instance.state = AgentState.PAUSED
                logger.info(f"角色智能体 {role_id} 已暂停")
                return True
            return False

    async def resume_role(self, role_id: str) -> bool:
        """恢复角色智能体"""
        async with self.factory_lock:
            instance = self.active_roles.get(role_id)
            if instance:
                instance.state = AgentState.ACTIVE
                logger.info(f"角色智能体 {role_id} 已恢复")
                return True
            return False

    async def terminate_role(self, role_id: str) -> bool:
        """终止角色智能体"""
        async with self.factory_lock:
            instance = self.active_roles.get(role_id)
            if instance:
                instance.state = AgentState.TERMINATED
                instance.conversation_history.clear()
                instance.memory_context.clear()

                # 从活跃列表中移除
                del self.active_roles[role_id]
                del self.role_configs[role_id]

                logger.info(f"角色智能体 {role_id} 已终止并清理")
                return True
            return False

    async def cleanup_inactive_roles(self, max_inactive_minutes: int = 30) -> int:
        """清理不活跃的角色智能体"""
        async with self.factory_lock:
            now = datetime.now()
            terminated_count = 0

            roles_to_remove = []
            for role_id, instance in self.active_roles.items():
                inactive_time = (now - instance.last_activity).total_seconds()
                if inactive_time > max_inactive_minutes * 60:
                    roles_to_remove.append(role_id)

            for role_id in roles_to_remove:
                self.terminate_role(role_id)
                terminated_count += 1

            if terminated_count > 0:
                logger.info(f"清理了 {terminated_count} 个不活跃的角色智能体")

            return terminated_count

    async def get_factory_statistics(self) -> Dict[str, Any]:
        """获取工厂统计信息"""
        async with self.factory_lock:
            state_counts = {}
            for instance in self.active_roles.values():
                state = instance.state.value
                state_counts[state] = state_counts.get(state, 0) + 1

            return {
                "total_roles": len(self.active_roles),
                "state_distribution": state_counts,
                "last_cleanup": self.last_cleanup.isoformat(),
                "factory_uptime": (datetime.now() - self.last_cleanup).total_seconds(),
            }

    async def create_default_roles(self, world_id: str) -> List[str]:
        """为指定世界创建默认角色"""
        default_configs = [
            RoleConfig(
                name="小魔法师",
                personality="勇敢而好奇，喜欢帮助别人",
                background="魔法学校的年轻学生，正在学习各种神奇的魔法",
                age_group="7-12",
                prompt_template="魔法学生模板",
                world_id=world_id,
                special_abilities=["简单魔法", "动物沟通"],
                safety_rules=["不使用攻击性魔法", "帮助他人"],
            ),
            RoleConfig(
                name="智慧老者",
                personality="慈祥而睿智，喜欢讲故事和给予指导",
                background="在森林深处居住的老智者，拥有丰富的知识和经验",
                age_group="所有年龄",
                prompt_template="智者模板",
                world_id=world_id,
                special_abilities=["讲故事", "解答问题"],
                safety_rules=["给出安全建议", "鼓励独立思考"],
            ),
        ]

        role_ids = []
        for config in default_configs:
            try:
                role_id = await self.create_role_agent(config)
                role_ids.append(role_id)
            except Exception as e:
                logger.error(f"创建默认角色失败 {config.name}: {str(e)}")

        return role_ids


# 创建全局角色智能体工厂实例
role_factory = RoleFactory()
