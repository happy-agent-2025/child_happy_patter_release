from typing import Dict, Any, List, Optional, TypedDict, Annotated, Tuple
from langgraph.graph import StateGraph, END
from dataclasses import dataclass
import json
from datetime import datetime
import threading

# 定义全局状态模式
class AgentState(TypedDict):
    """全局状态定义"""
    user_id: str
    session_id: Optional[str]
    content: str
    original_content: str

    # 安全状态
    safety_check_passed: bool
    safety_issues: List[str]
    filtered_content: Optional[str]

    # 路由信息
    intent: str
    confidence: float
    target_agent: str

    # 专业agent处理结果
    agent_results: Dict[str, Any]

    # 记忆和上下文 - LangGraph增强版
    conversation_history: List[Dict[str, Any]]      # 短期记忆（最近对话）
    long_term_context: Dict[str, Any]             # 长期记忆（用户画像）
    relevant_context: List[Dict[str, Any]]         # 当前相关上下文
    conversation_summary: Optional[str]             # 对话摘要
    session_memory: Dict[str, Any]                 # 会话级记忆

    # 最终响应
    final_response: str
    response_metadata: Dict[str, Any]

    # 错误处理
    error_message: Optional[str]
    retry_count: int

@dataclass
class HappyPartnerGraph:
    """Happy Partner LangGraph 工作流管理器"""

    def __init__(self):
        self.graph = StateGraph(AgentState)
        self._build_graph()

    def _build_graph(self):
        """构建LangGraph工作流 - 包含记忆管理"""
        # 添加节点
        self.graph.add_node("input_processing", self._process_input)
        self.graph.add_node("context_enrichment", self._enrich_context)    # 上下文增强
        self.graph.add_node("safety_check", self._safety_check)
        self.graph.add_node("intent_analysis", self._analyze_intent)
        self.graph.add_node("route_agent", self._route_agent)

        # 专业agent节点
        self.graph.add_node("edu_agent", self._edu_agent_process)
        self.graph.add_node("emotion_agent", self._emotion_agent_process)

        # 记忆管理节点
        self.graph.add_node("memory_update", self._update_memory)           # 记忆更新
        self.graph.add_node("context_summary", self._summarize_context)    # 上下文总结

        # 后处理节点
        self.graph.add_node("generate_response", self._generate_response)
        self.graph.add_node("error_handler", self._handle_error)

        # 定义边和条件路由
        self.graph.set_entry_point("input_processing")

        # 线性流程边
        self.graph.add_edge("input_processing", "context_enrichment")
        self.graph.add_edge("context_enrichment", "safety_check")
        self.graph.add_edge("safety_check", "intent_analysis")
        self.graph.add_edge("intent_analysis", "route_agent")

        # 条件路由边
        self.graph.add_conditional_edges(
            "route_agent",
            self._determine_agent_path,
            {
                "edu": "edu_agent",
                "emotion": "emotion_agent",
                "error": "error_handler"
            }
        )

        # 专业agent处理完成后更新记忆
        self.graph.add_edge("edu_agent", "memory_update")
        self.graph.add_edge("emotion_agent", "memory_update")

        # 记忆更新后，判断是否需要总结（每5轮对话总结一次）
        self.graph.add_conditional_edges(
            "memory_update",
            self._should_summarize,
            {
                "summarize": "context_summary",
                "continue": "generate_response"
            }
        )

        # 最终流程
        self.graph.add_edge("context_summary", "generate_response")
        self.graph.add_edge("generate_response", END)
        self.graph.add_edge("error_handler", END)

        # 编译图
        self.compiled_graph = self.graph.compile()

    def _process_input(self, state: AgentState) -> AgentState:
        """输入预处理节点"""
        try:
            # 标准化输入
            content = state.get("content", "").strip()
            if not content:
                state["error_message"] = "输入内容不能为空"
                return state

            state["original_content"] = content
            state["content"] = content
            state["retry_count"] = 0

            # 初始化状态
            state["safety_check_passed"] = False
            state["safety_issues"] = []
            state["agent_results"] = {}

            # 初始化记忆相关字段
            if "conversation_history" not in state:
                state["conversation_history"] = []
            if "long_term_context" not in state:
                state["long_term_context"] = {}
            if "relevant_context" not in state:
                state["relevant_context"] = []
            if "conversation_summary" not in state:
                state["conversation_summary"] = None
            if "session_memory" not in state:
                state["session_memory"] = {}

            state["response_metadata"] = {}

            return state

        except Exception as e:
            state["error_message"] = f"输入处理失败: {str(e)}"
            return state

    def _enrich_context(self, state: AgentState) -> AgentState:
        """智能上下文注入节点"""
        try:
            # 从历史中提取相关上下文
            relevant_history = self._retrieve_relevant_history(
                state["content"],
                state["conversation_history"]
            )

            # 构建用户画像（长期上下文）
            user_profile = self._build_user_profile(
                state["user_id"],
                state["conversation_history"],
                state["long_term_context"]
            )

            # 注入到状态中
            state["relevant_context"] = relevant_history
            state["long_term_context"] = user_profile

            # 为专业agent准备增强的请求
            state["user_context"] = {
                "recent_history": relevant_history,
                "user_profile": user_profile,
                "session_info": state["session_memory"],
                "conversation_summary": state["conversation_summary"]
            }

            return state

        except Exception as e:
            state["error_message"] = f"上下文注入失败: {str(e)}"
            return state

    def _retrieve_relevant_history(self, current_content: str, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从历史对话中检索相关内容"""
        if not history:
            return []

        # 简单的相关性计算（基于关键词重叠）
        relevant_history = []
        current_words = set(current_content.lower().split())

        # 获取最近5轮对话
        recent_history = history[-5:] if len(history) > 5 else history

        for conv in recent_history:
            conv_content = conv.get("original_content", conv.get("content", "")).lower()
            conv_words = set(conv_content.split())

            # 计算关键词重叠度
            overlap = len(current_words & conv_words)
            if overlap > 0 or len(recent_history) <= 2:  # 有重叠或是最近的对话
                relevant_history.append(conv)

        # 限制返回数量
        return relevant_history[-3:]

    def _build_user_profile(self, user_id: str, history: List[Dict[str, Any]], existing_profile: Dict[str, Any]) -> Dict[str, Any]:
        """构建用户画像"""
        profile = existing_profile.copy() if existing_profile else {}

        # 分析对话模式
        if history:
            # 统计agent使用偏好
            agent_usage = {}
            topic_keywords = {}

            for conv in history[-10:]:  # 分析最近10轮对话
                agent = conv.get("target_agent", conv.get("agent", "unknown"))
                agent_usage[agent] = agent_usage.get(agent, 0) + 1

                # 提取关键词
                content = conv.get("original_content", conv.get("content", ""))
                words = content.lower().split()
                for word in words:
                    if len(word) > 1:  # 过滤单字符
                        topic_keywords[word] = topic_keywords.get(word, 0) + 1

            # 更新用户画像
            profile.update({
                "user_id": user_id,
                "preferred_agents": agent_usage,
                "interest_keywords": dict(sorted(topic_keywords.items(), key=lambda x: x[1], reverse=True)[:10]),
                "conversation_count": len(history),
                "last_activity": datetime.now().isoformat()
            })

        return profile

    def _safety_check(self, state: AgentState) -> AgentState:
        """安全检查节点 - 优化版本，结合关键词过滤和智能分析"""
        try:
            from agents.safety_agent import SafetyAgent

            safety_agent = SafetyAgent()

            # 第一步：快速关键词预过滤
            is_pre_safe, pre_issues = self._quick_keyword_filter(state["content"])

            if is_pre_safe and not pre_issues:
                # 预过滤通过，直接判定为安全，跳过大模型调用
                state["safety_check_passed"] = True
                state["safety_issues"] = []
                state["filtered_content"] = None
                print(f"安全检查：内容 '{state['content']}' 通过预过滤")
                return state

            # 第二步：对于有潜在风险的内容，使用精确的大模型分析
            safety_result = safety_agent.filter_content(state["content"])

            state["safety_check_passed"] = safety_result.get("is_safe", True)
            state["safety_issues"] = safety_result.get("issues", [])
            state["filtered_content"] = safety_result.get("filtered_content")

            print(f"安全检查：内容 '{state['content']}' - 安全状态: {state['safety_check_passed']}")

            # 如果内容不安全，更新内容为过滤后的内容
            if not state["safety_check_passed"] and state["filtered_content"]:
                state["content"] = state["filtered_content"]

            return state

        except Exception as e:
            print(f"安全检查异常: {e}")
            state["error_message"] = f"安全检查失败: {str(e)}"
            return state

    def _quick_keyword_filter(self, content: str) -> Tuple[bool, List[str]]:
        """快速关键词预过滤 - 提升性能"""
        if not content or len(content.strip()) < 2:
            return True, []

        # 定义高风险关键词（更精确的匹配）
        high_risk_keywords = {
            # 暴力相关
            '暴力', '杀人', '死亡', '打斗', '伤害', '武器', '刀', '枪', '炸弹',
            # 成人内容
            '色情', '性爱', '裸体', '成人', '性暗示', '性行为',
            # 危险行为
            '自杀', '自残', '毒品', '酗酒', '抽烟', '爆炸',
            # 隐私信息
            '身份证', '密码', '银行卡', '手机号', '地址',
            # 仇恨言论
            '傻逼', '废物', '去死', '他妈的'
        }

        content_lower = content.lower()
        found_issues = []

        # 检查高风险关键词 - 使用更精确的匹配
        for keyword in high_risk_keywords:
            if keyword in content_lower:
                found_issues.append(f"检测到敏感词: {keyword}")

        # 对于教育、情感等正常内容，直接通过
        educational_keywords = {'学习', '教育', '数学', '科学', '语文', '英语', '问题', '帮助', '难过', '开心', '考试'}
        if any(keyword in content_lower for keyword in educational_keywords):
            return True, []

        # 如果没有发现高风险关键词，认为是安全的
        return len(found_issues) == 0, found_issues

    def _analyze_intent(self, state: AgentState) -> AgentState:
        """意图分析节点"""
        try:
            from agents.meta_agent import MetaAgent

            meta_agent = MetaAgent()
            request = {
                "content": state["content"],
                "user_id": state["user_id"]
            }

            # 使用MetaAgent进行意图识别
            agent_type = meta_agent.route_request(request)
            state["intent"] = agent_type
            state["confidence"] = 0.8  # 默认置信度

            return state

        except Exception as e:
            state["error_message"] = f"意图分析失败: {str(e)}"
            return state

    def _route_agent(self, state: AgentState) -> AgentState:
        """路由决策节点"""
        try:
            intent = state.get("intent", "edu")

            # 根据意图确定目标agent
            if intent == "safety" and not state["safety_check_passed"]:
                # 如果是安全问题且内容不安全，路由到错误处理
                state["target_agent"] = "error"
            elif intent in ["edu", "emotion"]:
                state["target_agent"] = intent
            else:
                # 默认路由到教育agent
                state["target_agent"] = "edu"
                state["intent"] = "edu"

            return state

        except Exception as e:
            state["error_message"] = f"路由决策失败: {str(e)}"
            state["target_agent"] = "error"
            return state

    def _determine_agent_path(self, state: AgentState) -> str:
        """确定agent路径的条件函数"""
        target_agent = state.get("target_agent", "edu")
        return target_agent

    def _edu_agent_process(self, state: AgentState) -> AgentState:
        """教育agent处理节点"""
        try:
            from agents.edu_agent import EduAgent

            edu_agent = EduAgent()
            # 安全地获取user_context，如果不存在则使用默认值
            user_context = state.get("user_context", {})
            request = {
                "content": state["content"],
                "user_id": state["user_id"],
                "grade_level": user_context.get("grade_level", "小学低年级")
            }

            print(f"教育agent处理请求: {request}")
            result = edu_agent.process_request(request)
            print(f"教育agent返回结果: {result}")

            state["agent_results"]["edu"] = result

            return state

        except Exception as e:
            print(f"教育agent处理异常: {e}")
            state["error_message"] = f"教育agent处理失败: {str(e)}"
            return state

    def _emotion_agent_process(self, state: AgentState) -> AgentState:
        """情感agent处理节点"""
        try:
            from agents.emotion_agent import EmotionAgent

            emotion_agent = EmotionAgent()
            request = {
                "content": state["content"],
                "user_id": state["user_id"]
            }

            result = emotion_agent.process_request(request)
            state["agent_results"]["emotion"] = result

            return state

        except Exception as e:
            state["error_message"] = f"情感agent处理失败: {str(e)}"
            return state

    
    def _update_memory(self, state: AgentState) -> AgentState:
        """LangGraph记忆更新节点"""
        try:
            # 构建对话记录
            conversation_record = {
                "user_id": state["user_id"],
                "session_id": state["session_id"],
                "original_content": state["original_content"],
                "content": state["content"],
                "filtered_content": state["filtered_content"],
                "intent": state["intent"],
                "target_agent": state["target_agent"],
                "safety_check_passed": state["safety_check_passed"],
                "agent_results": state["agent_results"],
                "relevant_context": state["relevant_context"],
                "timestamp": datetime.now().isoformat(),
                "metadata": state["response_metadata"]
            }

            # 添加到LangGraph管理的对话历史中
            state["conversation_history"].append(conversation_record)

            # 更新会话记忆
            self._update_session_memory(state)

            # 异步持久化到数据库（不阻塞主流程）
            self._async_persist_to_db(state, conversation_record)

            return state

        except Exception as e:
            state["error_message"] = f"记忆更新失败: {str(e)}"
            return state

    def _update_session_memory(self, state: AgentState) -> None:
        """更新会话级记忆"""
        session_memory = state["session_memory"]

        # 更新会话统计
        session_memory.update({
            "total_conversations": len(state["conversation_history"]),
            "recent_agents": session_memory.get("recent_agents", [])[-4:] + [state["target_agent"]],
            "session_start": session_memory.get("session_start", datetime.now().isoformat()),
            "last_activity": datetime.now().isoformat()
        })

        # 记录会话中的关键话题
        if state["conversation_summary"]:
            session_memory["key_topics"] = session_memory.get("key_topics", [])
            # 简单的关键词提取
            content_words = state["original_content"].lower().split()
            important_words = [w for w in content_words if len(w) > 2][:3]
            session_memory["key_topics"].extend(important_words)

    def _async_persist_to_db(self, state: AgentState, conversation_record: Dict[str, Any]) -> None:
        """异步持久化到数据库"""
        try:
            from utils.db.database_service import DatabaseService
            from utils.db.database import SessionLocal

            # 使用线程池异步执行，避免阻塞主流程
            def persist_task():
                try:
                    db_session = SessionLocal()
                    if db_session:
                        # 存储对话记录
                        DatabaseService.create_conversation(
                            db=db_session,
                            user_id=int(state["user_id"]) if state["user_id"].isdigit() else 1,
                            session_id=state["session_id"],
                            agent_type=state["target_agent"],
                            user_input=conversation_record["original_content"],
                            agent_response=json.dumps({
                                "response": state.get("final_response", ""),
                                "metadata": state["response_metadata"],
                                "agent_results": state["agent_results"]
                            }, ensure_ascii=False)
                        )

                        # 更新用户画像到数据库
                        if state["long_term_context"]:
                            self._persist_user_profile(db_session, state["user_id"], state["long_term_context"])

                        db_session.close()
                except Exception as e:
                    print(f"数据库持久化失败: {e}")

            # 启动异步线程
            thread = threading.Thread(target=persist_task)
            thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
            thread.start()

        except Exception as e:
            print(f"异步持久化启动失败: {e}")  # 不影响主流程

    def _persist_user_profile(self, db_session, user_id: str, profile: Dict[str, Any]) -> None:
        """持久化用户画像到数据库"""
        try:
            # 这里可以将用户画像存储到用户表或单独的用户画像表
            # 暂时打印日志，实际项目中需要实现数据库存储
            print(f"保存用户画像 {user_id}: {profile}")
        except Exception as e:
            print(f"用户画像持久化失败: {e}")

    def _should_summarize(self, state: AgentState) -> str:
        """判断是否需要总结上下文"""
        # 每5轮对话总结一次，或者对话历史过长时总结
        conversation_count = len(state["conversation_history"])

        if conversation_count > 0 and conversation_count % 5 == 0:
            return "summarize"

        # 如果上下文过长，也需要总结
        total_length = sum(len(str(conv)) for conv in state["conversation_history"])
        if total_length > 5000:  # 超过5000字符
            return "summarize"

        return "continue"

    def _summarize_context(self, state: AgentState) -> AgentState:
        """上下文总结节点"""
        try:
            # 如果没有足够的历史，跳过总结
            if len(state["conversation_history"]) < 3:
                return state

            # 构建需要总结的历史文本
            history_to_summarize = state["conversation_history"][-5:]  # 总结最近5轮

            summary_text = self._generate_summary(history_to_summarize)

            if summary_text:
                # 更新对话摘要
                if state["conversation_summary"]:
                    # 累积式摘要
                    state["conversation_summary"] = f"{state['conversation_summary']}\n\n最新摘要: {summary_text}"
                else:
                    state["conversation_summary"] = summary_text

                # 清理早期的对话历史，保留关键信息
                if len(state["conversation_history"]) > 10:
                    # 保留最近5轮和重要的早期对话
                    important_convs = [conv for conv in state["conversation_history"][:-5]
                                     if conv.get("target_agent") in ["edu", "emotion"]]
                    state["conversation_history"] = important_convs[-3:] + state["conversation_history"][-5:]

            return state

        except Exception as e:
            state["error_message"] = f"上下文总结失败: {str(e)}"
            return state

    def _generate_summary(self, history: List[Dict[str, Any]]) -> str:
        """生成对话摘要"""
        try:
            from core.openai_client import openai_client

            # 构建历史文本
            history_text = ""
            for i, conv in enumerate(history, 1):
                user_content = conv.get("original_content", "无内容")
                agent_response = conv.get("final_response", conv.get("response", "无回应"))
                agent_type = conv.get("target_agent", "unknown")

                history_text += f"{i}. 用户: {user_content}\n"
                history_text += f"   {agent_type}助手: {agent_response[:100]}...\n\n"

            if not history_text.strip():
                return ""

            prompt = f"""
            请为以下儿童对话历史生成一个简洁摘要（50-100字）：

            {history_text}

            摘要要求：
            1. 突出孩子关心的主要话题
            2. 总结互动特点
            3. 用简洁友好的语言
            """

            messages = [
                {"role": "system", "content": "你是一个专业的对话总结助手。"},
                {"role": "user", "content": prompt}
            ]

            response = openai_client.chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=150
            )

            return response.strip()

        except Exception as e:
            print(f"生成摘要失败: {e}")
            return ""

    def _generate_response(self, state: AgentState) -> AgentState:
        """生成最终响应节点"""
        try:
            target_agent = state["target_agent"]
            agent_result = state["agent_results"].get(target_agent, {})

            # 根据不同的agent类型生成响应
            if target_agent == "edu":
                response = agent_result.get("answer", "抱歉，我无法回答这个问题。")
                metadata = {
                    "type": "educational",
                    "subject": agent_result.get("subject", "通用"),
                    "agent": "edu"
                }
            elif target_agent == "emotion":
                response = agent_result.get("response", "感谢你分享你的感受。")
                emotion_analysis = agent_result.get("emotion_analysis", {})
                metadata = {
                    "type": "emotional",
                    "emotion": emotion_analysis.get("emotion", "未知"),
                    "intensity": emotion_analysis.get("intensity", "中"),
                    "agent": "emotion"
                }
            elif target_agent == "memory":
                response = agent_result.get("message", "记忆操作已完成。")
                metadata = {
                    "type": "memory",
                    "action": agent_result.get("action", "unknown"),
                    "agent": "memory"
                }
            else:
                response = "我理解你的问题，让我来帮助你。"
                metadata = {"type": "general", "agent": "default"}

            # 添加安全提示（如果有）
            if not state["safety_check_passed"]:
                response += "\n\n（温馨提示：你的问题已经经过安全处理）"

            state["final_response"] = response
            state["response_metadata"] = metadata

            return state

        except Exception as e:
            state["error_message"] = f"响应生成失败: {str(e)}"
            state["final_response"] = "抱歉，处理你的请求时出现了问题。"
            return state

    def _handle_error(self, state: AgentState) -> AgentState:
        """错误处理节点"""
        error_message = state.get("error_message", "未知错误")

        # 根据错误类型提供不同的错误响应
        if "安全" in error_message:
            response = "抱歉，我无法处理包含不当内容的请求。"
        elif "输入" in error_message:
            response = "请提供有效的输入内容。"
        else:
            response = "抱歉，系统暂时出现问题，请稍后再试。"

        state["final_response"] = response
        state["response_metadata"] = {
            "type": "error",
            "error": error_message,
            "agent": "error_handler"
        }

        return state

    async def process_message(self, user_id: str, content: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """处理用户消息的主要入口"""
        initial_state = AgentState(
            user_id=user_id,
            session_id=session_id,
            content=content,
            original_content="",
            safety_check_passed=False,
            safety_issues=[],
            filtered_content=None,
            intent="",
            confidence=0.0,
            target_agent="",
            agent_results={},
            # LangGraph增强的记忆字段
            conversation_history=[],
            long_term_context={},
            relevant_context=[],
            conversation_summary=None,
            session_memory={},
            user_context={},
            final_response="",
            response_metadata={},
            error_message=None,
            retry_count=0
        )

        # 执行LangGraph工作流
        final_state = self.compiled_graph.invoke(initial_state)

        return {
            "response": final_state.get("final_response", ""),
            "metadata": final_state.get("response_metadata", {}),
            "agent_results": final_state.get("agent_results", {}),
            "safety_info": {
                "passed": final_state.get("safety_check_passed", True),
                "issues": final_state.get("safety_issues", []),
                "filtered": final_state.get("filtered_content") is not None
            },
            # LangGraph记忆信息
            "memory_info": {
                "conversation_summary": final_state.get("conversation_summary"),
                "relevant_context_count": len(final_state.get("relevant_context", [])),
                "total_conversations": len(final_state.get("conversation_history", [])),
                "user_profile": final_state.get("long_term_context", {}),
                "session_info": final_state.get("session_memory", {})
            },
            "conversation_history": final_state.get("conversation_history", [])
        }

# 创建全局工作流实例
happy_partner_graph = HappyPartnerGraph()