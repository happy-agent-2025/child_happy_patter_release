"""
状态图多代理系统 - 儿童教育AI助手

基于LangGraph实现的多代理状态图系统，支持：
1. 智能意图识别和路由
2. 简单聊天模式（情感智能+安全检查）
3. 故事模式（动态创作+角色扮演）
4. 语音输入输出处理（集成到所有模式）
5. mem0持久化记忆系统
"""

from typing import Dict, Any, List, Optional, TypedDict, Annotated
from enum import Enum
import json
import uuid
import asyncio
import logging
from datetime import datetime
from dataclasses import dataclass, field

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from agents.intent_agent import intent_agent, IntentType
from agents.world_agent import world_agent
from agents.role_factory import role_factory
from agents.role_agent import RoleAgent, TypesOfRole
from agents.safety_agent import SafetyAgent
from agents.emotion_agent import EmotionAgent
from memory.mem0 import story_memory_manager, MemoryType
from utils.openai_client import openai_client
# 语音服务引用（保留接口）
try:
    from services.stt_service import STTService
    from services.tts_service import TTSService
    STT_AVAILABLE = True
except ImportError:
    STTService = None
    TTSService = None
    STT_AVAILABLE = False

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InteractionMode(str, Enum):
    """交互模式枚举"""

    CHAT = "chat"  # 简单聊天模式
    STORY = "story"  # 故事模式


class InputType(str, Enum):
    """输入类型枚举"""

    TEXT = "text"  # 文本输入
    VOICE = "voice"  # 语音输入
    MIXED = "mixed"  # 混合输入


class GraphState(TypedDict):
    """状态图状态定义"""

    messages: Annotated[List[BaseMessage], "对话消息列表"]
    user_id: str
    session_id: str
    current_mode: InteractionMode
    input_type: InputType
    intent_result: Optional[Dict[str, Any]]
    world_context: Optional[Dict[str, Any]]
    role_context: Optional[Dict[str, Any]]
    memory_context: Optional[Dict[str, Any]]
    safety_check: Optional[Dict[str, Any]]
    emotion_analysis: Optional[Dict[str, Any]]
    voice_metadata: Optional[Dict[str, Any]]
    response_ready: bool
    next_agent: str


@dataclass
class StorySession:
    """故事会话"""

    session_id: str
    user_id: str
    world_id: str
    current_chapter: int = 0
    total_chapters: int = 1
    active_roles: List[str] = field(default_factory=list)
    story_progress: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


class MultiAgent:
    """
    多代理状态图系统

    主要功能：
    1. 意图识别和智能路由
    2. 多模式交互支持
    3. 代理协调和状态管理
    4. 记忆系统集成
    5. 安全和情感智能
    """

    def __init__(self):
        # 初始化核心组件
        self.safety_agent = SafetyAgent()
        self.emotion_agent = EmotionAgent()

        # 初始化语音服务（如果可用）
        self.stt_service = STTService() if STT_AVAILABLE and STTService else None
        self.tts_service = TTSService() if STT_AVAILABLE and TTSService else None

        # 故事会话管理
        self.active_story_sessions: Dict[str, StorySession] = {}

        # 构建状态图
        self.graph = self._build_graph()

        logger.info("多代理状态图系统初始化完成")
        if STT_AVAILABLE:
            logger.info("语音服务已启用")
        else:
            logger.info("语音服务未启用，将使用文本模式")

    def _build_graph(self) -> StateGraph:
        """构建状态图"""
        # 创建状态图
        workflow = StateGraph(GraphState)

        # 添加节点
        workflow.add_node("input_processor", self.input_processor_node)
        workflow.add_node("intent_router", self.intent_router_node)
        workflow.add_node("safety_checker", self.safety_checker_node)
        workflow.add_node("emotion_analyzer", self.emotion_analyzer_node)
        workflow.add_node("chat_handler", self.chat_handler_node)
        workflow.add_node("story_world_builder", self.story_world_builder_node)
        workflow.add_node("story_role_manager", self.story_role_manager_node)
        workflow.add_node("story_interactive", self.story_interactive_node)
        workflow.add_node("memory_updater", self.memory_updater_node)
        workflow.add_node("response_formatter", self.response_formatter_node)
        workflow.add_node("voice_output_processor", self.voice_output_processor_node)

        # 设置入口点
        workflow.add_edge(START, "input_processor")

        # 添加条件路由
        workflow.add_conditional_edges(
            "intent_router",
            lambda x: x.get("next_agent", "safety_checker"),
            {
                "safety_checker": "safety_checker",
                "chat_handler": "chat_handler",
                "story_world_builder": "story_world_builder",
                "__end__": END,
            },
        )

        # 添加安全检查后的路由
        workflow.add_conditional_edges(
            "safety_checker",
            lambda x: (
                "emotion_analyzer"
                if x.get("safety_check", {}).get("is_safe", True)
                else "response_formatter"
            ),
            {
                "emotion_analyzer": "emotion_analyzer",
                "response_formatter": "response_formatter",
            },
        )

        # 添加情感分析后的路由
        workflow.add_conditional_edges(
            "emotion_analyzer",
            lambda x: x.get("current_mode", InteractionMode.CHAT),
            {
                InteractionMode.CHAT: "chat_handler",
                InteractionMode.STORY: "story_world_builder",
            },
        )

        # 故事模式的路由
        workflow.add_edge("story_world_builder", "story_role_manager")
        workflow.add_edge("story_role_manager", "story_interactive")

        # 汇聚到记忆更新
        workflow.add_edge("chat_handler", "memory_updater")
        workflow.add_edge("story_interactive", "memory_updater")

        # 最终响应格式化
        workflow.add_edge("memory_updater", "response_formatter")

        # 响应格式化后到语音处理（如果需要）
        workflow.add_conditional_edges(
            "response_formatter",
            lambda x: "voice_output_processor" if x.get("input_type") == InputType.VOICE else "__end__",
            {
                "voice_output_processor": "voice_output_processor",
                "__end__": END
            }
        )

        workflow.add_edge("voice_output_processor", END)

        # 添加从输入处理器到意图路由器的连接
        workflow.add_edge("input_processor", "intent_router")

        # 编译图
        return workflow.compile()

    async def input_processor_node(self, state: GraphState) -> GraphState:
        """输入处理器节点 - 处理不同类型的输入"""
        try:
            user_message = state["messages"][-1].content
            input_type = state.get("input_type", InputType.TEXT)

            # 如果是语音输入，这里会进行语音转文本处理
            # 现在只保留接口，实际处理由外部服务完成
            if input_type == InputType.VOICE and self.stt_service:
                # 语音元数据
                voice_metadata = {
                    "input_type": "voice",
                    "processing_attempted": True,
                    "stt_available": True,
                    "timestamp": datetime.now().isoformat()
                }
                state.update({
                    "voice_metadata": voice_metadata,
                    "next_agent": "intent_router"
                })
            else:
                # 文本输入或语音服务不可用
                voice_metadata = {
                    "input_type": input_type.value,
                    "processing_attempted": False,
                    "stt_available": STT_AVAILABLE,
                    "timestamp": datetime.now().isoformat()
                }
                state.update({
                    "voice_metadata": voice_metadata,
                    "next_agent": "intent_router"
                })

            return state

        except Exception as e:
            logger.error(f"输入处理失败: {e}")
            state.update({
                "voice_metadata": {
                    "input_type": "text",
                    "processing_attempted": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                },
                "next_agent": "intent_router"
            })
            return state

    async def voice_output_processor_node(self, state: GraphState) -> GraphState:
        """语音输出处理器节点 - 处理文本转语音输出"""
        try:
            # 获取最后一条AI消息
            if state["messages"] and isinstance(state["messages"][-1], AIMessage):
                response_text = state["messages"][-1].content

                if self.tts_service:
                    # 语音输出元数据
                    voice_output_metadata = {
                        "output_type": "voice",
                        "text_length": len(response_text),
                        "tts_available": True,
                        "processing_attempted": True,
                        "timestamp": datetime.now().isoformat()
                    }

                    # 更新语音元数据
                    updated_voice_metadata = state.get("voice_metadata", {})
                    updated_voice_metadata.update(voice_output_metadata)

                    state.update({
                        "voice_metadata": updated_voice_metadata,
                        "next_agent": END
                    })
                else:
                    # TTS服务不可用
                    voice_output_metadata = {
                        "output_type": "text",
                        "text_length": len(response_text),
                        "tts_available": False,
                        "processing_attempted": False,
                        "timestamp": datetime.now().isoformat()
                    }

                    updated_voice_metadata = state.get("voice_metadata", {})
                    updated_voice_metadata.update(voice_output_metadata)

                    state.update({
                        "voice_metadata": updated_voice_metadata,
                        "next_agent": END
                    })

            return state

        except Exception as e:
            logger.error(f"语音输出处理失败: {e}")

            # 更新元数据记录错误
            updated_voice_metadata = state.get("voice_metadata", {})
            updated_voice_metadata.update({
                "output_type": "text",
                "processing_attempted": True,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

            state.update({
                "voice_metadata": updated_voice_metadata,
                "next_agent": END
            })
            return state

    async def intent_router_node(self, state: GraphState) -> GraphState:
        """意图识别和路由节点"""
        try:
            user_message = state["messages"][-1].content
            user_id = state["user_id"]

            # 使用意图识别智能体
            intent_result = intent_agent.detect_intent(
                user_message, user_id, state["session_id"]
            )

            # 确定交互模式
            if intent_result["intent"] == IntentType.STORY:
                current_mode = InteractionMode.STORY
                next_agent = "safety_checker"
            elif intent_result["intent"] == IntentType.CHAT:
                current_mode = InteractionMode.CHAT
                next_agent = "safety_checker"
            else:  # 其他情况都默认为聊天模式
                # 语音命令现在根据内容路由到相应的模式
                if any(keyword in user_message.lower() for keyword in ["故事", "创建", "角色", "扮演"]):
                    current_mode = InteractionMode.STORY
                else:
                    current_mode = InteractionMode.CHAT
                next_agent = "safety_checker"

            # 更新状态
            state.update(
                {
                    "intent_result": intent_result,
                    "current_mode": current_mode,
                    "next_agent": next_agent,
                }
            )

            logger.info(
                f"意图识别结果: {intent_result['intent']}, 模式: {current_mode}"
            )
            return state

        except Exception as e:
            logger.error(f"意图识别失败: {e}")
            state.update(
                {
                    "intent_result": {
                        "intent": IntentType.CHAT,
                        "confidence": 0.5,
                    },
                    "current_mode": InteractionMode.CHAT,
                    "next_agent": "safety_checker",
                }
            )
            return state

    async def safety_checker_node(self, state: GraphState) -> GraphState:
        """安全检查节点"""
        try:
            user_message = state["messages"][-1].content

            # 执行安全检查
            safety_result = self.safety_agent.filter_content(user_message)

            state.update(
                {
                    "safety_check": safety_result,
                    "next_agent": (
                        "emotion_analyzer"
                        if safety_result.get("is_safe", True)
                        else "response_formatter"
                    ),
                }
            )

            if not safety_result.get("is_safe", True):
                logger.warning(f"内容安全检查失败: {safety_result.get('reasons', [])}")

            return state

        except Exception as e:
            logger.error(f"安全检查失败: {e}")
            state.update(
                {
                    "safety_check": {"is_safe": True, "reasons": []},
                    "next_agent": "emotion_analyzer",
                }
            )
            return state

    async def emotion_analyzer_node(self, state: GraphState) -> GraphState:
        """情感分析节点"""
        try:
            user_message = state["messages"][-1].content
            user_id = state["user_id"]

            # 执行情感分析
            emotion_request = {"content": user_message, "user_id": user_id}
            emotion_result = self.emotion_agent.analyze_emotion(emotion_request)

            state.update(
                {
                    "emotion_analysis": emotion_result,
                    "next_agent": state["current_mode"],  # 根据当前模式路由到下一个节点
                }
            )

            return state

        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            state.update(
                {
                    "emotion_analysis": {"emotion_type": "neutral", "confidence": 0.5},
                    "next_agent": state["current_mode"],
                }
            )
            return state

    async def chat_handler_node(self, state: GraphState) -> GraphState:
        """简单聊天模式处理器"""
        try:
            user_message = state["messages"][-1].content
            user_id = state["user_id"]
            emotion_context = state.get("emotion_analysis", {})

            # 获取相关记忆
            relevant_memories = story_memory_manager.search_relevant_memories(
                query=user_message,
                user_id=user_id,
                memory_types=[
                    MemoryType.INTERACTION_HISTORY,
                    MemoryType.USER_PREFERENCE,
                ],
                limit=3,
            )

            # 构建聊天上下文
            chat_context = {
                "user_message": user_message,
                "emotion_context": emotion_context,
                "relevant_memories": relevant_memories,
                "interaction_mode": "chat",
            }

            # 生成聊天回应
            response_content = await self._generate_chat_response(chat_context)

            # 添加回应到消息列表
            state["messages"].append(AIMessage(content=response_content))
            state.update({"response_ready": True, "next_agent": "memory_updater"})

            return state

        except Exception as e:
            logger.error(f"聊天处理失败: {e}")
            state["messages"].append(
                AIMessage(content="抱歉，我现在有点困惑，能再说一遍吗？")
            )
            state.update({"response_ready": True, "next_agent": "memory_updater"})
            return state

    async def story_world_builder_node(self, state: GraphState) -> GraphState:
        """故事世界观构建节点"""
        try:
            user_message = state["messages"][-1].content
            user_id = state["user_id"]
            session_id = state["session_id"]

            # 检查是否已有故事会话
            if session_id not in self.active_story_sessions:
                # 创建新的故事世界
                world_result = world_agent.create_world(user_message, user_id)

                if world_result["success"]:
                    world_data = world_result["world"]
                    world_id = world_data["world_id"]

                    # 创建故事会话
                    story_session = StorySession(
                        session_id=session_id, user_id=user_id, world_id=world_id
                    )
                    self.active_story_sessions[session_id] = story_session

                    # 存储世界观记忆
                    story_memory_manager.store_world_memory(
                        world_data, user_id, session_id
                    )

                    # 为世界创建默认角色
                    role_ids = await role_factory.create_default_roles(world_id)
                    story_session.active_roles.extend(role_ids)

                    state.update(
                        {
                            "world_context": world_data,
                            "next_agent": "story_role_manager",
                        }
                    )

                    logger.info(f"创建故事世界: {world_data['world_name']}")
                else:
                    # 世界创建失败，返回错误
                    state["messages"].append(
                        AIMessage(
                            content="抱歉，我无法创建这个故事世界。让我们尝试其他话题吧！"
                        )
                    )
                    state.update(
                        {"response_ready": True, "next_agent": "memory_updater"}
                    )
            else:
                # 已有故事会话，直接进入角色管理
                state.update({"next_agent": "story_role_manager"})

            return state

        except Exception as e:
            logger.error(f"故事世界构建失败: {e}")
            state["messages"].append(
                AIMessage(content="创建故事世界时出现了问题，我们换个话题聊聊吧！")
            )
            state.update({"response_ready": True, "next_agent": "memory_updater"})
            return state

    async def story_role_manager_node(self, state: GraphState) -> GraphState:
        """故事角色管理节点"""
        try:
            session_id = state["session_id"]
            story_session = self.active_story_sessions.get(session_id)

            if not story_session:
                state.update({"next_agent": "story_interactive"})
                return state

            # 获取活跃角色信息
            active_role_info = []
            for role_id in story_session.active_roles:
                role_info = await role_factory.get_role_info(role_id)
                if role_info:
                    active_role_info.append(role_info)

            state.update(
                {
                    "role_context": {
                        "active_roles": active_role_info,
                        "session_info": {
                            "current_chapter": story_session.current_chapter,
                            "total_chapters": story_session.total_chapters,
                        },
                    },
                    "next_agent": "story_interactive",
                }
            )

            return state

        except Exception as e:
            logger.error(f"角色管理失败: {e}")
            state.update({"next_agent": "story_interactive"})
            return state

    async def story_interactive_node(self, state: GraphState) -> GraphState:
        """故事互动节点"""
        try:
            user_message = state["messages"][-1].content
            user_id = state["user_id"]
            session_id = state["session_id"]
            story_session = self.active_story_sessions.get(session_id)
            role_context = state.get("role_context", {})

            if not story_session or not role_context.get("active_roles"):
                # 没有活跃角色，提供故事引导
                response_content = "欢迎来到故事世界！你想让哪个角色和你一起冒险呢？"
            else:
                # 选择第一个活跃角色进行互动
                active_role = role_context["active_roles"][0]
                role_id = active_role["role_id"]
                role_name = active_role["name"]

                # 获取角色智能体
                role_agent_instance = await role_factory.get_role(role_id)
                if role_agent_instance:
                    # 使用角色智能体生成回应
                    response = await role_agent_instance.respond_to_message(
                        user_message, user_id, session_id
                    )

                    if response["success"]:
                        response_content = response["response"]

                        # 存储互动记忆
                        interaction_data = {
                            "role_name": role_name,
                            "user_message": user_message,
                            "role_response": response_content,
                            "emotion": response.get("emotion_analysis", {}).get(
                                "emotion_type", "neutral"
                            ),
                            "learning_point": response.get("learning_point"),
                        }

                        story_memory_manager.store_interaction_history(
                            interaction_data,
                            user_id,
                            session_id,
                            f"chapter_{story_session.current_chapter}",
                        )
                    else:
                        response_content = (
                            f"{role_name}似乎在想别的事情，我们稍后再聊吧！"
                        )
                else:
                    response_content = f"让{role_name}来回应你的问题..."

            # 添加回应到消息列表
            state["messages"].append(AIMessage(content=response_content))
            state.update({"response_ready": True, "next_agent": "memory_updater"})

            return state

        except Exception as e:
            logger.error(f"故事互动失败: {e}")
            state["messages"].append(
                AIMessage(content="故事互动时出现了问题，我们继续聊天吧！")
            )
            state.update({"response_ready": True, "next_agent": "memory_updater"})
            return state

    async def memory_updater_node(self, state: GraphState) -> GraphState:
        """记忆更新节点"""
        try:
            user_id = state["user_id"]
            session_id = state["session_id"]
            current_mode = state["current_mode"]

            # 更新用户互动历史
            if len(state["messages"]) >= 2:
                user_message = state["messages"][-2].content
                ai_response = state["messages"][-1].content

                interaction_data = {
                    "user_message": user_message,
                    "ai_response": ai_response,
                    "mode": current_mode.value,
                    "timestamp": datetime.now().isoformat(),
                }

                story_memory_manager.store_interaction_history(
                    interaction_data, user_id, session_id, f"session_{session_id}"
                )

            state.update({"next_agent": "response_formatter"})

            return state

        except Exception as e:
            logger.error(f"记忆更新失败: {e}")
            state.update({"next_agent": "response_formatter"})
            return state

    async def response_formatter_node(self, state: GraphState) -> GraphState:
        """响应格式化节点"""
        try:
            # 如果内容不安全，提供安全回应
            safety_check = state.get("safety_check", {})
            if not safety_check.get("is_safe", True):
                safe_response = "抱歉，我无法回应这个内容。让我们聊点别的有趣的话题吧！"
                if state["messages"] and isinstance(
                    state["messages"][-1], HumanMessage
                ):
                    state["messages"].append(AIMessage(content=safe_response))

                state.update({"response_ready": True, "next_agent": END})
                return state

            # 如果响应已准备好，直接结束
            if state.get("response_ready", False):
                state.update({"next_agent": END})
                return state

            # 默认情况：如果没有生成响应，生成默认回应
            if not state["messages"] or not isinstance(
                state["messages"][-1], AIMessage
            ):
                default_response = "我理解你的意思，让我想想怎么回应比较好..."
                state["messages"].append(AIMessage(content=default_response))

            state.update({"response_ready": True, "next_agent": END})

            return state

        except Exception as e:
            logger.error(f"响应格式化失败: {e}")
            state.update({"next_agent": END})
            return state

    async def _generate_chat_response(self, context: Dict[str, Any]) -> str:
        """生成聊天回应"""
        try:
            user_message = context["user_message"]
            emotion_context = context.get("emotion_context", {})
            relevant_memories = context.get("relevant_memories", [])

            # 构建提示
            prompt = f"""
你是一个友好的儿童教育AI助手。请回应用户的消息。

用户消息：{user_message}

情感分析：{emotion_context.get('emotion_type', 'neutral')} (置信度: {emotion_context.get('confidence', 0.5)})

相关记忆：
{chr(10).join([mem.content for mem in relevant_memories[:2]]) if relevant_memories else '这是我们的第一次对话'}

请以友好、积极、适合儿童的方式回应。回应要求：
1. 使用简单的语言，适合儿童理解
2. 保持积极乐观的语调
3. 如果用户表达情感，给予适当的回应
4. 长度控制在100字以内
5. 可以提问来鼓励继续对话

回应内容：
"""

            messages = [
                {
                    "role": "system",
                    "content": "你是一个儿童教育AI助手，专门与儿童进行友好对话。",
                },
                {"role": "user", "content": prompt},
            ]

            response = openai_client.chat_completion(
                messages=messages, temperature=0.7, max_tokens=200
            )

            return response.strip()

        except Exception as e:
            logger.error(f"生成聊天回应失败: {e}")
            return "我很想和你聊天，让我想想怎么说..."

    async def process_message(
        self, user_message: str, user_id: str, session_id: Optional[str] = None,
        input_type: InputType = InputType.TEXT
    ) -> Dict[str, Any]:
        """
        处理用户消息的主入口

        Args:
            user_message: 用户消息
            user_id: 用户ID
            session_id: 会话ID（可选）
            input_type: 输入类型（文本/语音/混合）

        Returns:
            处理结果
        """
        try:
            # 生成会话ID（如果未提供）
            if not session_id:
                session_id = f"session_{user_id}_{uuid.uuid4().hex[:8]}"

            # 构建初始状态
            initial_state: GraphState = {
                "messages": [HumanMessage(content=user_message)],
                "user_id": user_id,
                "session_id": session_id,
                "current_mode": InteractionMode.CHAT,
                "input_type": input_type,
                "intent_result": None,
                "world_context": None,
                "role_context": None,
                "memory_context": None,
                "safety_check": None,
                "emotion_analysis": None,
                "voice_metadata": None,
                "response_ready": False,
                "next_agent": "intent_router",
            }

            # 执行状态图
            result = await self.graph.ainvoke(initial_state)

            # 提取最终回应
            final_response = None
            if result["messages"] and isinstance(result["messages"][-1], AIMessage):
                final_response = result["messages"][-1].content

            # 构建响应
            response = {
                "success": True,
                "response": final_response or "抱歉，我没有理解你的意思。",
                "session_id": session_id,
                "mode": result["current_mode"].value,
                "intent": result.get("intent_result", {}).get("intent", "unknown"),
                "safety_check": result.get("safety_check", {}),
                "emotion_analysis": result.get("emotion_analysis", {}),
                "world_context": result.get("world_context"),
                "role_context": result.get("role_context"),
                "voice_metadata": result.get("voice_metadata"),
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"消息处理完成: {result['current_mode']}")
            return response

        except Exception as e:
            logger.error(f"消息处理失败: {e}")
            return {
                "success": False,
                "response": "抱歉，系统出现了问题，请稍后再试。",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        story_session = self.active_story_sessions.get(session_id)
        if story_session:
            return {
                "session_id": story_session.session_id,
                "user_id": story_session.user_id,
                "world_id": story_session.world_id,
                "current_chapter": story_session.current_chapter,
                "total_chapters": story_session.total_chapters,
                "active_roles_count": len(story_session.active_roles),
                "created_at": story_session.created_at.isoformat(),
                "last_activity": story_session.last_activity.isoformat(),
            }
        return None

    async def end_story_session(self, session_id: str) -> bool:
        """结束故事会话"""
        try:
            if session_id in self.active_story_sessions:
                session = self.active_story_sessions[session_id]

                # 清理活跃角色
                for role_id in session.active_roles:
                    await role_factory.terminate_role(role_id)

                # 移除会话
                del self.active_story_sessions[session_id]

                logger.info(f"结束故事会话: {session_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"结束故事会话失败: {e}")
            return False

    async def get_system_statistics(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        return {
            "active_story_sessions": len(self.active_story_sessions),
            "memory_stats": story_memory_manager.get_memory_statistics(),
            "role_factory_stats": await role_factory.get_factory_statistics(),
            "total_sessions_processed": len(self.active_story_sessions),  # 简化统计
        }


# 创建全局多代理系统实例
multi_agent = MultiAgent()
