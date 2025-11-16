"""
角色智能体 - 专门的角色扮演和互动智能体

基于智能体工厂创建的角色智能体，提供专门的角色扮演功能，
支持个性化回应、情感表达和故事互动。
"""

from typing import Dict, Any, List, Optional, TypedDict
from enum import Enum
import json
import asyncio
from datetime import datetime
from dataclasses import dataclass, field

from core.openai_client import openai_client
from agents.safety_agent import SafetyAgent
from agents.emotion_agent import EmotionAgent


class TypesOfRole(str, Enum):
    """角色类型枚举"""

    HERO = "英雄"  # 主角类
    MENTOR = "导师"  # 指导类
    COMPANION = "伙伴"  # 伙伴类
    VILLAIN = "反派"  # 反派类（儿童友好版）
    NEUTRAL = "中立"  # 中立类


class RoleEmotion(str, Enum):
    """角色情感状态"""

    HAPPY = "开心"
    EXCITED = "兴奋"
    CURIOUS = "好奇"
    WORRIED = "担心"
    CONFUSED = "困惑"
    BRAVE = "勇敢"
    KIND = "友善"
    NEUTRAL = "平静"


@dataclass
class RoleMemory:
    """角色记忆"""

    role_id: str
    user_id: str
    world_id: str
    personal_memories: List[Dict[str, Any]] = field(default_factory=list)
    relationship_history: List[Dict[str, Any]] = field(default_factory=list)
    story_context: Dict[str, Any] = field(default_factory=dict)
    learned_lessons: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


class RoleResponse(TypedDict):
    """角色回应结构"""

    success: bool
    response: str
    role_name: str
    emotion: RoleEmotion
    action_suggestion: Optional[str]
    learning_point: Optional[str]
    safety_check: Dict[str, Any]
    metadata: Dict[str, Any]


class RoleAgent:
    """
    角色智能体

    专门的角色扮演智能体，提供：
    1. 保持角色性格一致性
    2. 情感表达和互动
    3. 故事情节推进
    4. 教育价值传递
    5. 安全内容生成
    """

    def __init__(
        self,
        role_id: str,
        name: str,
        role: TypesOfRole,
        personality: str,
        background: str,
        world_id: str,
        user_id: str,
    ):
        self.role_id = role_id
        self.name = name
        self.role = role
        self.personality = personality
        self.background = background
        self.world_id = world_id
        self.user_id = user_id

        # 情感状态
        self.current_emotion = RoleEmotion.NEUTRAL
        self.emotion_intensity = 0.5  # 0-1之间

        # 记忆系统
        self.memory = RoleMemory(role_id=role_id, user_id=user_id, world_id=world_id)

        # 异步锁
        self.lock = asyncio.Lock()

        # 依赖组件
        self.safety_agent = SafetyAgent()
        self.emotion_agent = EmotionAgent()

        # 生成角色提示
        self.role_prompt = self._generate_role_prompt()

    def _generate_role_prompt(self) -> str:
        """生成角色提示模板"""
        role_roleistics = {
            TypesOfRole.HERO: "勇敢、正义、帮助他人、面对困难不退缩",
            TypesOfRole.MENTOR: "智慧、慈祥、善于指导、富有经验",
            TypesOfRole.COMPANION: "友善、忠诚、有趣、支持朋友",
            TypesOfRole.VILLAIN: "调皮、有点固执但内心善良、最终会改正错误",
            TypesOfRole.NEUTRAL: "平和、观察者、提供帮助但不主动干涉",
        }

        return f"""
你是{name}，一个儿童故事角色。

角色信息：
- 姓名：{self.name}
- 角色：{self.role.value}
- 性格：{self.personality}
- 背景：{self.background}
- 角色特点：{role_roleistics[self.role]}

互动原则：
1. 始终保持{name}的性格特点
2. 根据故事情节表达适当的情感
3. 使用适合儿童的语言表达
4. 在互动中传递正面价值观
5. 鼓励用户思考和参与
6. 保持故事有趣且引人入胜

当前情感状态：{self.current_emotion.value} (强度: {self.emotion_intensity})
"""

    async def interact(
        self, user_message: str, context: Optional[Dict[str, Any]] = None
    ) -> RoleResponse:
        """
        与用户互动

        Args:
            user_message: 用户消息
            context: 上下文信息

        Returns:
            角色回应
        """
        async with self.lock:
            try:
                # 1. 安全检查
                safety_result = self.safety_agent.validate_content(user_message)
                if not safety_result.get("is_safe", False):
                    return await self._create_safe_response(
                        "让我们聊点别的有趣的话题吧！"
                    )

                # 2. 更新情感状态
                await self._update_emotional_state(user_message)

                # 3. 构建互动上下文
                interaction_context = await self._build_interaction_context(
                    user_message, context
                )

                # 4. 生成角色回应
                response_content = await self._generate_role_response(
                    interaction_context
                )

                # 5. 安全检查回应内容
                response_safety = self.safety_agent.validate_content(response_content)
                if not response_safety.get("is_safe", False):
                    response_content = "我觉得我们需要用更好的方式来交流..."

                # 6. 提取教育价值
                learning_point = await self._extract_learning_point(response_content)

                # 7. 更新记忆
                self._update_memory(user_message, response_content, context)

                return {
                    "success": True,
                    "response": response_content,
                    "role_name": self.name,
                    "emotion": self.current_emotion,
                    "action_suggestion": await self._suggest_action(),
                    "learning_point": learning_point,
                    "safety_check": response_safety,
                    "metadata": {
                        "role_id": self.role_id,
                        "interaction_time": datetime.now().isoformat(),
                        "emotion_intensity": self.emotion_intensity,
                    },
                }

            except Exception as e:
                return await self._create_error_response(f"互动时出现错误: {str(e)}")

    async def _update_emotional_state(self, user_message: str) -> None:
        """更新情感状态"""
        try:
            # 分析用户消息的情感倾向
            emotion_request = {"content": user_message, "user_id": self.user_id}
            emotion_analysis = self.emotion_agent.analyze_emotion(emotion_request)

            # 根据角色性格和用户情感调整角色情感
            user_emotion = emotion_analysis.get("emotion_type", "neutral")

            # 简单的情感映射逻辑
            emotion_mapping = {
                "happy": RoleEmotion.HAPPY,
                "excited": RoleEmotion.EXCITED,
                "curious": RoleEmotion.CURIOUS,
                "worried": RoleEmotion.WORRIED,
                "confused": RoleEmotion.CONFUSED,
            }

            if user_emotion in emotion_mapping:
                # 英雄角色会根据用户情感调整
                if self.role == TypesOfRole.HERO:
                    self.current_emotion = emotion_mapping[user_emotion]
                    self.emotion_intensity = min(1.0, self.emotion_intensity + 0.1)
                # 伙伴角色会回应积极情感
                elif self.role == TypesOfRole.COMPANION and user_emotion == "happy":
                    self.current_emotion = RoleEmotion.HAPPY
                    self.emotion_intensity = 0.8

        except Exception as e:
            # 保持默认情感状态
            pass

    async def _build_interaction_context(
        self, user_message: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """构建互动上下文"""
        # 获取相关记忆
        relevant_memories = self._get_relevant_memories(user_message)

        # 构建上下文
        interaction_context = {
            "role_prompt": self.role_prompt,
            "current_emotion": self.current_emotion.value,
            "emotion_intensity": self.emotion_intensity,
            "user_message": user_message,
            "relevant_memories": relevant_memories,
            "story_context": context or {},
            "role_background": self.background,
        }

        return interaction_context

    async def _generate_role_response(self, context: Dict[str, Any]) -> str:
        """生成角色回应"""
        try:
            # 构建提示
            prompt = f"""
{context['role_prompt']}

当前情感状态：{context['current_emotion']} (强度: {context['emotion_intensity']})

相关记忆：
{self._format_memories(context['relevant_memories'])}

故事背景：{context['role_background']}

用户说：{context['user_message']}

请以{self.name}的身份回应，要求：
1. 保持角色性格特点
2. 表达当前的情感状态
3. 回应要有趣且引人入胜
4. 鼓励用户继续互动
5. 传递正面价值观
6. 使用适合儿童的语言

回应内容：
"""

            messages = [
                {
                    "role": "system",
                    "content": "你是一个儿童故事角色，始终保持角色设定并表达适当的情感。",
                },
                {"role": "user", "content": prompt},
            ]

            response = openai_client.chat_completion(
                messages=messages,
                temperature=0.8,  # 稍高的温度增加创造性
                max_tokens=400,
            )

            return response.strip()

        except Exception as e:
            return "我很想回应你，但让我想想怎么说..."

    def _format_memories(self, memories: List[Dict[str, Any]]) -> str:
        """格式化记忆内容"""
        if not memories:
            return "这是我们互动的新开始。"

        formatted = []
        for memory in memories[-3:]:  # 最近3条记忆
            formatted.append(f"记得{memory.get('description', '一些有趣的事情')}")

        return "\n".join(formatted)

    def _get_relevant_memories(self, user_message: str) -> List[Dict[str, Any]]:
        """获取相关记忆"""
        # 简单的关键词匹配
        relevant = []
        keywords = ["朋友", "帮助", "勇敢", "学习", "游戏", "故事", "冒险"]

        for memory in self.memory.personal_memories:
            if any(keyword in user_message for keyword in keywords):
                relevant.append(memory)

        return relevant[-3:]  # 返回最近3条相关记忆

    def _update_memory(
        self,
        user_message: str,
        agent_response: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """更新记忆"""
        # 添加个人记忆
        memory_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "agent_response": agent_response,
            "emotion": self.current_emotion.value,
            "context": context or {},
        }

        self.memory.personal_memories.append(memory_entry)

        # 限制记忆数量
        if len(self.memory.personal_memories) > 100:
            self.memory.personal_memories = self.memory.personal_memories[-50:]

        self.memory.last_updated = datetime.now()

    async def _extract_learning_point(self, response: str) -> Optional[str]:
        """提取教育价值"""
        try:
            prompt = f"""
从下面的角色回应中提取一个简单的教育价值或学习点：

回应内容：{response}

要求：
1. 提取一个适合儿童的教育价值
2. 语言简单易懂
3. 价值观正面积极
4. 长度不超过20个字

学习点：
"""

            messages = [
                {
                    "role": "system",
                    "content": "你是一个教育专家，专门提取儿童内容中的教育价值。",
                },
                {"role": "user", "content": prompt},
            ]

            response = openai_client.chat_completion(
                messages=messages, temperature=0.3, max_tokens=50
            )

            learning_point = response.strip()
            return (
                learning_point if learning_point and len(learning_point) <= 20 else None
            )

        except Exception:
            return None

    async def _suggest_action(self) -> Optional[str]:
        """建议下一个行动"""
        try:
            # 根据角色类型和情感状态建议行动
            if (
                self.role == TypesOfRole.HERO
                and self.current_emotion == RoleEmotion.EXCITED
            ):
                return "让我们开始一次新的冒险吧！"
            elif self.role == TypesOfRole.MENTOR:
                return "你想学习什么新知识呢？"
            elif self.role == TypesOfRole.COMPANION:
                return "我们一起玩游戏怎么样？"
            elif self.current_emotion == RoleEmotion.CURIOUS:
                return "让我们探索一些有趣的事情！"

            return None

        except Exception:
            return None

    async def _create_safe_response(self, message: str) -> RoleResponse:
        """创建安全回应"""
        return {
            "success": True,
            "response": message,
            "role_name": self.name,
            "emotion": RoleEmotion.KIND,
            "action_suggestion": None,
            "learning_point": "安全和友善很重要",
            "safety_check": {"is_safe": True, "reasons": []},
            "metadata": {
                "role_id": self.role_id,
                "interaction_time": datetime.now().isoformat(),
                "safe_response": True,
            },
        }

    async def _create_error_response(self, error_message: str) -> RoleResponse:
        """创建错误回应"""
        return {
            "success": False,
            "response": "抱歉，我现在有点困惑，能再说一遍吗？",
            "role_name": self.name,
            "emotion": RoleEmotion.CONFUSED,
            "action_suggestion": None,
            "learning_point": None,
            "safety_check": {"is_safe": True, "reasons": []},
            "metadata": {
                "role_id": self.role_id,
                "interaction_time": datetime.now().isoformat(),
                "error": error_message,
            },
        }

    def get_role_summary(self) -> Dict[str, Any]:
        """获取角色摘要"""
        return {
            "role_id": self.role_id,
            "name": self.name,
            "role": self.role.value,
            "personality": self.personality,
            "current_emotion": self.current_emotion.value,
            "emotion_intensity": self.emotion_intensity,
            "total_memories": len(self.memory.personal_memories),
            "world_id": self.world_id,
            "user_id": self.user_id,
        }

    def set_emotion(self, emotion: RoleEmotion, intensity: float = 0.5) -> None:
        """设置情感状态"""
        self.current_emotion = emotion
        self.emotion_intensity = max(0.0, min(1.0, intensity))

    def add_learned_lesson(self, lesson: str) -> None:
        """添加学习经验"""
        if lesson and lesson not in self.memory.learned_lessons:
            self.memory.learned_lessons.append(lesson)
            self.memory.last_updated = datetime.now()

    def get_memory_summary(self) -> Dict[str, Any]:
        """获取记忆摘要"""
        return {
            "total_memories": len(self.memory.personal_memories),
            "learned_lessons": self.memory.learned_lessons[-5:],  # 最近5个
            "last_updated": self.memory.last_updated.isoformat(),
            "story_context": self.memory.story_context,
        }


# 创建角色智能体的工厂函数
def create_role_agent(
    name: str,
    role: TypesOfRole,
    personality: str,
    background: str,
    world_id: str,
    user_id: str,
) -> RoleAgent:
    """创建角色智能体的工厂函数"""
    role_id = f"char_{name}_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    return RoleAgent(
        role_id=role_id,
        name=name,
        role=role,
        personality=personality,
        background=background,
        world_id=world_id,
        user_id=user_id,
    )
