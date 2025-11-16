"""
意图识别智能体 - 增强版元代理，支持故事模式检测和情感分析

基于现有meta_agent.py扩展，添加专门的故事模式检测逻辑、
情感分析功能和语音唤醒词识别。
"""

from typing import Dict, Any, List, Optional, TypedDict
from enum import Enum
import re
import json
from datetime import datetime

from core.openai_client import openai_client
from agents.meta_agent import MetaAgent
from agents.safety_agent import SafetyAgent
from agents.emotion_agent import EmotionAgent
from agents.world_agent import world_agent


class IntentType(str, Enum):
    """意图类型枚举"""

    CHAT = "chat"  # 聊天模式
    STORY = "story"  # 故事模式


class IntentResult(TypedDict):
    """意图识别结果"""

    intent: IntentType
    confidence: float  # 置信度 0-1
    wakeup_detected: bool  # 是否检测到唤醒词
    emotion_type: Optional[str]  # 情感类型
    entities: List[str]  # 提取的实体
    reasoning: str  # 推理过程
    metadata: Dict[str, Any]  # 额外元数据


class IntentAgent(MetaAgent):
    """
    增强版意图识别智能体

    扩展原有MetaAgent功能，添加：
    1. 专门的故事模式检测逻辑
    2. 情感分析功能集成
    3. 语音唤醒词识别
    4. 多维度意图分析
    """

    def __init__(self):
        super().__init__()

        # 唤醒词配置
        self.wakeup_words = [
            "贝贝你好",
            "小贝贝",
            "讲故事",
            "贝贝",
            "开始游戏",
            "我们来玩游戏",
            "我想听故事",
            "开始讲故事",
            "你好贝贝",
        ]

        # 故事模式关键词
        self.story_keywords = [
            "故事",
            "创建",
            "世界观",
            "角色",
            "扮演",
            "魔法",
            "冒险",
            "太空",
            "海洋",
            "森林",
            "恐龙",
            "公主",
            "城堡",
            "开始",
            "讲故事",
            "游戏",
            "扮演",
            "虚构",
            "想象",
            "童话",
        ]

        # 简单聊天关键词
        self.chat_keywords = [
            "你好",
            "嗨",
            "早上好",
            "晚上好",
            "再见",
            "谢谢",
            "今天",
            "明天",
            "昨天",
            "现在",
            "怎么样",
            "如何",
            "开心",
            "难过",
            "生气",
            "害怕",
            "喜欢",
            "爱",
            "朋友",
            "学校",
            "家庭",
            "学习",
            "帮助",
        ]

        # 初始化其他智能体
        self.safety_agent = SafetyAgent()
        self.emotion_agent = EmotionAgent()

    def detect_intent(
        self, content: str, user_id: str, session_id: Optional[str] = None
    ) -> IntentResult:
        """
        增强的意图检测方法

        Args:
            content: 用户输入内容
            user_id: 用户ID
            session_id: 会话ID（可选）

        Returns:
            IntentResult: 意图识别结果
        """
        try:
            # 1. 基础预处理
            content_clean = self._preprocess_content(content)

            # 2. 检测唤醒词
            wakeup_detected = self._check_wakeup_words(content_clean)

            # 3. 提取实体和关键词
            entities = self._extract_entities(content_clean)

            # 4. 基于关键词的初步意图分类
            keyword_intent = self._classify_by_keywords(content_clean)

            # 5. AI模型增强分析
            ai_analysis = self._ai_intent_analysis(content_clean, user_id, session_id)

            # 6. 情感分析
            emotion_result = self._analyze_emotion(content_clean, user_id)

            # 7. 综合判断最终意图
            final_intent = self._determine_final_intent(
                keyword_intent, ai_analysis, entities, wakeup_detected
            )

            # 8. 计算置信度
            confidence = self._calculate_confidence(
                final_intent, keyword_intent, ai_analysis, entities
            )

            return {
                "intent": final_intent,
                "confidence": confidence,
                "wakeup_detected": wakeup_detected,
                "emotion_type": emotion_result.get("emotion_type"),
                "entities": entities,
                "reasoning": self._generate_reasoning(
                    final_intent, keyword_intent, ai_analysis, entities
                ),
                "metadata": {
                    "keyword_intent": keyword_intent,
                    "ai_analysis": ai_analysis,
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            # 错误处理，返回安全的默认结果
            return {
                "intent": IntentType.CHAT,
                "confidence": 0.5,
                "wakeup_detected": False,
                "emotion_type": None,
                "entities": [],
                "reasoning": f"分析过程中出现错误: {str(e)}",
                "metadata": {"error": str(e), "timestamp": datetime.now().isoformat()},
            }

    def _preprocess_content(self, content: str) -> str:
        """预处理用户输入内容"""
        # 去除多余空格和标点
        content = re.sub(r"\s+", " ", content.strip())
        # 转换为小写进行分析
        return content.lower()

    def _check_wakeup_words(self, content: str) -> bool:
        """检测是否包含唤醒词"""
        for wakeup_word in self.wakeup_words:
            if wakeup_word.lower() in content:
                return True
        return False

    def _extract_entities(self, content: str) -> List[str]:
        """提取内容中的实体（简单实现）"""
        entities = []

        # 提取故事类型
        story_types = ["魔法", "太空", "海洋", "森林", "恐龙", "公主", "动物"]
        for story_type in story_types:
            if story_type in content:
                entities.append(f"story_type:{story_type}")

        # 提取故事模式相关
        if any(word in content for word in self.story_keywords):
            entities.append("story_intention")

        # 提取聊天相关
        if any(word in content for word in self.chat_keywords):
            entities.append("chat_intention")

        return entities

    def _classify_by_keywords(self, content: str) -> IntentType:
        """基于关键词的初步意图分类"""
        story_score = sum(1 for keyword in self.story_keywords if keyword in content)
        chat_score = sum(1 for keyword in self.chat_keywords if keyword in content)

        # 如果有故事关键词且分数更高，选择故事模式
        if story_score > chat_score:
            return IntentType.STORY
        elif chat_score > 0:
            return IntentType.CHAT
        else:
            # 没有明确关键词，默认为聊天
            return IntentType.CHAT

    def _ai_intent_analysis(
        self, content: str, user_id: str, session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """使用AI模型进行意图分析"""
        try:
            prompt = f"""
            你是一个专业的意图识别系统。请分析用户输入的意图，并返回JSON格式的分析结果。

            用户输入: "{content}"
            用户ID: {user_id}
            会话ID: {session_id or '无'}

            请识别以下两种意图类型:
            1. chat - 聊天：日常对话、问候、情感交流等
            2. story - 故事：创建故事、角色扮演、世界观设定等

            判断标准：
            - 如果用户想要听故事、创作故事、扮演角色、创建虚构世界，选择story
            - 如果用户只是日常聊天、问候、表达情感、询问日常信息，选择chat

            请以JSON格式回复，包含以下字段:
            {{
                "primary_intent": "chat 或 story",
                "confidence": 0.0-1.0之间的置信度,
                "explanation": "分析解释",
                "context_clues": ["上下文线索"]
            }}
            """

            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的意图识别助手，严格按照JSON格式回复。",
                },
                {"role": "user", "content": prompt},
            ]

            response = openai_client.chat_completion(
                messages=messages,
                temperature=0.1,  # 降低温度以获得更确定的结果
                max_tokens=500,
            )

            # 解析JSON响应
            try:
                result = json.loads(response.strip())
                return {
                    "primary_intent": result.get("primary_intent", "chat"),
                    "confidence": float(result.get("confidence", 0.5)),
                    "explanation": result.get("explanation", ""),
                    "context_clues": result.get("context_clues", []),
                }
            except (json.JSONDecodeError, ValueError):
                # JSON解析失败，返回默认结果
                return {
                    "primary_intent": "chat",
                    "confidence": 0.5,
                    "explanation": "AI分析失败，使用默认结果",
                    "context_clues": [],
                }

        except Exception as e:
            # AI调用失败，返回默认结果
            return {
                "primary_intent": "chat",
                "confidence": 0.3,
                "explanation": f"AI分析出错: {str(e)}",
                "context_clues": [],
            }

    def _analyze_emotion(self, content: str, user_id: str) -> Dict[str, Any]:
        """分析内容的情感倾向"""
        try:
            # 使用现有情感智能体
            emotion_request = {"content": content, "user_id": user_id}
            return self.emotion_agent.analyze_emotion(emotion_request)
        except Exception as e:
            return {"emotion_type": None, "confidence": 0.0, "error": str(e)}

    def _determine_final_intent(
        self,
        keyword_intent: IntentType,
        ai_analysis: Dict[str, Any],
        entities: List[str],
        wakeup_detected: bool,
    ) -> IntentType:
        """综合判断最终意图"""
        # 获取AI分析的主要意图
        ai_primary = ai_analysis.get("primary_intent", "chat")
        ai_confidence = ai_analysis.get("confidence", 0.5)

        # 如果AI置信度很高，优先使用AI结果
        if ai_confidence >= 0.8:
            try:
                return IntentType(ai_primary)
            except ValueError:
                pass

        # 如果检测到唤醒词，偏向故事模式
        if wakeup_detected:
            return IntentType.STORY

        # 基于实体信息调整
        if "story_type:魔法" in entities or "story_type:太空" in entities:
            return IntentType.STORY

        if "story_intention" in entities:
            return IntentType.STORY

        if "chat_intention" in entities:
            return IntentType.CHAT

        # 默认使用关键词分类结果
        return keyword_intent

    def _calculate_confidence(
        self,
        final_intent: IntentType,
        keyword_intent: IntentType,
        ai_analysis: Dict[str, Any],
        entities: List[str],
    ) -> float:
        """计算意图识别的置信度"""
        base_confidence = 0.5

        # 如果AI分析和关键词分类一致，增加置信度
        if final_intent == keyword_intent:
            base_confidence += 0.2

        # AI置信度权重
        ai_confidence = ai_analysis.get("confidence", 0.5)
        base_confidence = (base_confidence + ai_confidence) / 2

        # 实体匹配增加置信度
        entity_bonus = min(len(entities) * 0.1, 0.3)
        base_confidence += entity_bonus

        # 确保置信度在0-1之间
        return min(max(base_confidence, 0.1), 1.0)

    def _generate_reasoning(
        self,
        final_intent: IntentType,
        keyword_intent: IntentType,
        ai_analysis: Dict[str, Any],
        entities: List[str],
    ) -> str:
        """生成意图识别的推理过程"""
        reasoning_parts = []

        reasoning_parts.append(f"关键词分类结果: {keyword_intent.value}")
        reasoning_parts.append(
            f"AI分析结果: {ai_analysis.get('primary_intent', 'unknown')}"
        )
        reasoning_parts.append(f"提取实体: {', '.join(entities)}")

        if final_intent == keyword_intent:
            reasoning_parts.append("关键词分类与最终结果一致")
        else:
            reasoning_parts.append("基于AI分析和实体信息调整了结果")

        return "；".join(reasoning_parts)

    def route_request_with_context(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        带上下文的智能路由方法（扩展原有方法）

        Args:
            request: 包含content, user_id, session_id等的请求字典

        Returns:
            包含路由结果和详细分析信息的字典
        """
        content = request.get("content", "")
        user_id = request.get("user_id", "unknown_user")
        session_id = request.get("session_id")

        # 使用增强的意图检测
        intent_result = self.detect_intent(content, user_id, session_id)

        # 安全检查
        safety_check = self.safety_agent.validate_content(content)

        # 构建响应
        response = {
            "agent": intent_result["intent"].value,
            "request": request,
            "status": "routed",
            "intent_analysis": intent_result,
            "safety_check": safety_check,
            "timestamp": datetime.now().isoformat(),
        }

        return response

    def get_intent_statistics(self, user_id: str, limit: int = 100) -> Dict[str, Any]:
        """
        获取用户的意图统计信息（用于个性化优化）

        Args:
            user_id: 用户ID
            limit: 查询的历史记录数量限制

        Returns:
            意图统计信息
        """
        # 这里可以集成mem0记忆系统来分析用户的历史意图模式
        # 暂时返回示例数据
        return {
            "user_id": user_id,
            "total_intents": 0,
            "intent_distribution": {"chat": 0, "story": 0},
            "common_entities": [],
            "preferred_interaction_time": None,
        }


# 创建全局意图识别智能体实例
intent_agent = IntentAgent()
