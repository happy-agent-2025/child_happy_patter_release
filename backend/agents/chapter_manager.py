"""
章节管理中心 - 故事章节管理智能体

负责管理故事章节的创建、推进和协调多个角色智能体，
维护故事进度和状态，集成记忆存储功能。
"""

from typing import Dict, Any, List, Optional, TypedDict
from enum import Enum
import json
import uuid
import asyncio
from datetime import datetime
from dataclasses import dataclass, field

from agents.role_agent import RoleAgent, TypesOfRole, RoleEmotion
from agents.role_factory import role_factory, RoleConfig
from utils.openai_client import openai_client
from agents.safety_agent import SafetyAgent


class ChapterState(str, Enum):
    """章节状态"""

    PLANNING = "planning"  # 规划中
    ACTIVE = "active"  # 活跃中
    PAUSED = "paused"  # 暂停
    COMPLETED = "completed"  # 已完成
    ARCHIVED = "archived"  # 已归档


class ChapterType(str, Enum):
    """章节类型"""

    INTRODUCTION = "introduction"  # 介绍章节
    ADVENTURE = "adventure"  # 冒险章节
    CHALLENGE = "challenge"  # 挑战章节
    RESOLUTION = "resolution"  # 解决章节
    CONCLUSION = "conclusion"  # 总结章节


@dataclass
class ChapterObjective:
    """章节目标"""

    description: str
    success_criteria: List[str]
    educational_goals: List[str]
    difficulty_level: int  # 1-5


@dataclass
class ChapterProgress:
    """章节进度"""

    current_step: int
    total_steps: int
    completed_objectives: List[str]
    active_roles: List[str]
    user_engagement_score: float  # 0-1
    time_spent_minutes: float


@dataclass
class Chapter:
    """故事章节"""

    chapter_id: str
    story_id: str
    title: str
    chapter_type: ChapterType
    state: ChapterState
    objectives: List[ChapterObjective]
    progress: ChapterProgress
    content_summary: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ChapterManager:
    """
    章节管理中心

    功能：
    1. 章节创建和规划
    2. 多角色智能体协调
    3. 章节进度管理
    4. 用户参与度跟踪
    5. 故事连贯性维护
    6. 记忆系统集成
    """

    def __init__(self):
        self.active_chapters: Dict[str, Chapter] = {}
        self.story_roles: Dict[str, List[str]] = {}  # story_id -> [role_agent_ids]
        self.chapter_lock = asyncio.Lock()
        self.safety_agent = SafetyAgent()

    async def create_chapter(
        self,
        story_id: str,
        title: str,
        chapter_type: ChapterType,
        world_description: str,
        role_configs: List[RoleConfig],
        educational_goals: List[str] = None,
    ) -> str:
        """
        创建新章节

        Args:
            story_id: 故事ID
            title: 章节标题
            chapter_type: 章节类型
            world_description: 世界描述
            role_configs: 角色配置列表
            educational_goals: 教育目标

        Returns:
            章节ID
        """
        async with self.chapter_lock:
            try:
                chapter_id = f"chapter_{story_id}_{uuid.uuid4().hex[:8]}"

                # 为章节创建角色智能体
                role_ids = []
                for config in role_configs:
                    try:
                        role_id = await role_factory.create_role_agent(config)
                        role_ids.append(role_id)
                    except Exception as e:
                        print(f"创建角色失败 {config.name}: {e}")

                # 生成章节目标
                objectives = self._generate_chapter_objectives(
                    chapter_type, educational_goals or []
                )

                # 创建章节
                chapter = Chapter(
                    chapter_id=chapter_id,
                    story_id=story_id,
                    title=title,
                    chapter_type=chapter_type,
                    state=ChapterState.PLANNING,
                    objectives=objectives,
                    progress=ChapterProgress(
                        current_step=0,
                        total_steps=len(objectives),
                        completed_objectives=[],
                        active_roles=role_ids,
                        user_engagement_score=0.0,
                        time_spent_minutes=0.0,
                    ),
                    content_summary="",
                    created_at=datetime.now(),
                    metadata={
                        "world_description": world_description,
                        "planning_completed": False,
                    },
                )

                self.active_chapters[chapter_id] = chapter
                self.story_roles[story_id] = role_ids

                print(f"创建章节: {title} (ID: {chapter_id})")
                return chapter_id

            except Exception as e:
                print(f"创建章节失败: {e}")
                raise RuntimeError(f"章节创建失败: {e}")

    async def start_chapter(self, chapter_id: str) -> bool:
        """启动章节"""
        async with self.chapter_lock:
            chapter = self.active_chapters.get(chapter_id)
            if not chapter:
                return False

            if chapter.state == ChapterState.PLANNING:
                chapter.state = ChapterState.ACTIVE
                chapter.started_at = datetime.now()
                print(f"章节 {chapter.title} 已启动")
                return True

            return False

    async def advance_chapter(
        self, chapter_id: str, user_action: str, user_id: str
    ) -> Dict[str, Any]:
        """
        推进章节

        Args:
            chapter_id: 章节ID
            user_action: 用户行动
            user_id: 用户ID

        Returns:
            章节推进结果
        """
        async with self.chapter_lock:
            chapter = self.active_chapters.get(chapter_id)
            if not chapter or chapter.state != ChapterState.ACTIVE:
                return {"success": False, "error": "章节不存在或未激活"}

            try:
                # 1. 安全检查
                safety_result = self.safety_agent.validate_content(user_action)
                if not safety_result.get("is_safe", False):
                    return {
                        "success": False,
                        "error": "内容不安全",
                        "safety_check": safety_result,
                    }

                # 2. 获取相关角色智能体
                role_agents = await self._get_active_role_agents(chapter)

                # 3. 协调角色回应
                role_responses = []
                for agent in role_agents:
                    try:
                        response = await agent.interact(
                            user_action,
                            context={
                                "chapter_id": chapter_id,
                                "chapter_title": chapter.title,
                                "progress": chapter.progress.current_step,
                            },
                        )
                        role_responses.append(response)
                    except Exception as e:
                        print(f"角色回应失败: {e}")

                # 4. 更新章节进度
                progress_update = self._update_chapter_progress(
                    chapter, user_action, role_responses
                )

                # 5. 生成章节内容摘要
                content_summary = self._generate_content_summary(
                    chapter, user_action, role_responses
                )

                # 6. 检查章节是否完成
                completion_status = self._check_chapter_completion(chapter)

                # 7. 更新参与度评分
                engagement_score = self._calculate_engagement_score(
                    chapter, user_action, role_responses
                )

                return {
                    "success": True,
                    "chapter_id": chapter_id,
                    "chapter_title": chapter.title,
                    "role_responses": role_responses,
                    "progress_update": progress_update,
                    "content_summary": content_summary,
                    "completion_status": completion_status,
                    "engagement_score": engagement_score,
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"章节推进失败: {str(e)}",
                    "chapter_id": chapter_id,
                }

    async def _get_active_role_agents(self, chapter: Chapter) -> List[RoleAgent]:
        """获取活跃的角色智能体"""
        agents = []
        for role_id in chapter.progress.active_roles:
            role = await role_factory.get_role(role_id)
            if role:
                agents.append(role)
        return agents

    def _update_chapter_progress(
        self, chapter: Chapter, user_action: str, role_responses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """更新章节进度"""
        # 简单的进度更新逻辑
        if chapter.progress.current_step < chapter.progress.total_steps:
            chapter.progress.current_step += 1

        # 更新时间
        if chapter.started_at:
            time_spent = (datetime.now() - chapter.started_at).total_seconds() / 60
            chapter.progress.time_spent_minutes = time_spent

        return {
            "current_step": chapter.progress.current_step,
            "total_steps": chapter.progress.total_steps,
            "completion_percentage": (
                chapter.progress.current_step / chapter.progress.total_steps
            )
            * 100,
            "time_spent_minutes": chapter.progress.time_spent_minutes,
        }

    def _generate_content_summary(
        self, chapter: Chapter, user_action: str, role_responses: List[Dict[str, Any]]
    ) -> str:
        """生成章节内容摘要"""
        try:
            # 构建摘要提示
            prompt = f"""
为下面的故事互动生成一个简短的摘要：

章节标题：{chapter.title}
用户行动：{user_action}

角色回应：
{self._format_responses_for_summary(role_responses)}

要求：
1. 摘要长度在50-100字之间
2. 保持故事连贯性
3. 突出重要事件和情感
4. 适合儿童理解

摘要：
"""

            messages = [
                {
                    "role": "system",
                    "content": "你是一个故事摘要助手，擅长简洁地总结故事情节。",
                },
                {"role": "user", "content": prompt},
            ]

            response = openai_client.chat_completion(
                messages=messages, temperature=0.5, max_tokens=200
            )

            return response.strip()

        except Exception as e:
            return "故事继续发展..."

    def _format_responses_for_summary(self, responses: List[Dict[str, Any]]) -> str:
        """格式化回应用于摘要生成"""
        formatted = []
        for response in responses:
            if response.get("success"):
                formatted.append(
                    f"{response.get('role_name', '角色')}: {response.get('response', '')}"
                )
        return "\n".join(formatted)

    def _check_chapter_completion(self, chapter: Chapter) -> Dict[str, Any]:
        """检查章节完成状态"""
        is_completed = False
        completion_reason = ""

        # 检查进度
        if chapter.progress.current_step >= chapter.progress.total_steps:
            is_completed = True
            completion_reason = "所有目标已完成"

        # 检查参与度
        elif chapter.progress.user_engagement_score > 0.8:
            is_completed = True
            completion_reason = "用户高度参与，可以提前完成"

        if is_completed:
            chapter.state = ChapterState.COMPLETED
            chapter.completed_at = datetime.now()

        return {
            "is_completed": is_completed,
            "completion_reason": completion_reason,
            "final_state": chapter.state.value,
        }

    def _calculate_engagement_score(
        self, chapter: Chapter, user_action: str, role_responses: List[Dict[str, Any]]
    ) -> float:
        """计算用户参与度评分"""
        try:
            # 简单的参与度计算逻辑
            base_score = 0.5

            # 用户输入长度（较长的输入通常表示更多参与）
            if len(user_action) > 20:
                base_score += 0.1

            # 角色回应数量和质量
            if role_responses:
                base_score += 0.2

                # 检查是否有情感表达
                for response in role_responses:
                    if (
                        response.get("emotion")
                        and response["emotion"] != RoleEmotion.NEUTRAL
                    ):
                        base_score += 0.1

            # 进度完成度
            progress_ratio = (
                chapter.progress.current_step / chapter.progress.total_steps
            )
            base_score += progress_ratio * 0.1

            chapter.progress.user_engagement_score = min(1.0, base_score)
            return chapter.progress.user_engagement_score

        except Exception:
            return 0.5

    async def pause_chapter(self, chapter_id: str) -> bool:
        """暂停章节"""
        async with self.chapter_lock:
            chapter = self.active_chapters.get(chapter_id)
            if chapter and chapter.state == ChapterState.ACTIVE:
                chapter.state = ChapterState.PAUSED

                # 暂停相关角色智能体
                for role_id in chapter.progress.active_roles:
                    await role_factory.pause_role(role_id)

                return True
            return False

    async def resume_chapter(self, chapter_id: str) -> bool:
        """恢复章节"""
        async with self.chapter_lock:
            chapter = self.active_chapters.get(chapter_id)
            if chapter and chapter.state == ChapterState.PAUSED:
                chapter.state = ChapterState.ACTIVE

                # 恢复相关角色智能体
                for role_id in chapter.progress.active_roles:
                    await role_factory.resume_role(role_id)

                return True
            return False

    async def get_chapter_summary(self, chapter_id: str) -> Optional[Dict[str, Any]]:
        """获取章节摘要"""
        async with self.chapter_lock:
            chapter = self.active_chapters.get(chapter_id)
            if not chapter:
                return None

            # 获取角色状态
            role_summaries = []
            for role_id in chapter.progress.active_roles:
                role_info = await role_factory.get_role_info(role_id)
                if role_info:
                    role_summaries.append(role_info)

            return {
                "chapter_id": chapter.chapter_id,
                "title": chapter.title,
                "chapter_type": chapter.chapter_type.value,
                "state": chapter.state.value,
                "progress": {
                    "current_step": chapter.progress.current_step,
                    "total_steps": chapter.progress.total_steps,
                    "completion_percentage": (
                        chapter.progress.current_step / chapter.progress.total_steps
                    )
                    * 100,
                    "engagement_score": chapter.progress.user_engagement_score,
                    "time_spent_minutes": chapter.progress.time_spent_minutes,
                },
                "objectives_count": len(chapter.objectives),
                "active_roles": role_summaries,
                "created_at": chapter.created_at.isoformat(),
                "started_at": (
                    chapter.started_at.isoformat() if chapter.started_at else None
                ),
                "completed_at": (
                    chapter.completed_at.isoformat() if chapter.completed_at else None
                ),
            }

    async def list_story_chapters(self, story_id: str) -> List[Dict[str, Any]]:
        """列出故事的所有章节"""
        async with self.chapter_lock:
            chapters = []
            for chapter_id, chapter in self.active_chapters.items():
                if chapter.story_id == story_id:
                    summary = await self.get_chapter_summary(chapter_id)
                    if summary:
                        chapters.append(summary)
            return chapters

    async def complete_chapter(self, chapter_id: str) -> bool:
        """完成章节"""
        async with self.chapter_lock:
            chapter = self.active_chapters.get(chapter_id)
            if chapter and chapter.state in [ChapterState.ACTIVE, ChapterState.PAUSED]:
                chapter.state = ChapterState.COMPLETED
                chapter.completed_at = datetime.now()

                # 终止相关角色智能体
                for role_id in chapter.progress.active_roles:
                    await role_factory.terminate_role(role_id)

                return True
            return False

    async def archive_chapter(self, chapter_id: str) -> bool:
        """归档章节"""
        async with self.chapter_lock:
            chapter = self.active_chapters.get(chapter_id)
            if chapter and chapter.state == ChapterState.COMPLETED:
                chapter.state = ChapterState.ARCHIVED

                # 从活跃章节中移除，但保留数据
                # 这里可以添加持久化存储逻辑

                return True
            return False

    def _generate_chapter_objectives(
        self, chapter_type: ChapterType, educational_goals: List[str]
    ) -> List[ChapterObjective]:
        """生成章节目标"""
        base_objectives = {
            ChapterType.INTRODUCTION: [
                ChapterObjective(
                    description="认识角色和世界",
                    success_criteria=["用户能说出至少一个角色名字", "用户理解基本设定"],
                    educational_goals=["认识新朋友", "了解环境"],
                    difficulty_level=1,
                )
            ],
            ChapterType.ADVENTURE: [
                ChapterObjective(
                    description="探索新区域",
                    success_criteria=["用户描述探索过程", "发现有趣的事物"],
                    educational_goals=["探索精神", "观察力"],
                    difficulty_level=2,
                )
            ],
            ChapterType.CHALLENGE: [
                ChapterObjective(
                    description="面对并解决问题",
                    success_criteria=["识别问题", "尝试解决方案"],
                    educational_goals=["解决问题", "坚持不懈"],
                    difficulty_level=3,
                )
            ],
            ChapterType.RESOLUTION: [
                ChapterObjective(
                    description="解决冲突或困难",
                    success_criteria=["理解问题本质", "参与解决过程"],
                    educational_goals=["和平解决", "团队合作"],
                    difficulty_level=2,
                )
            ],
            ChapterType.CONCLUSION: [
                ChapterObjective(
                    description="总结故事经验",
                    success_criteria=["回顾故事", "表达感受"],
                    educational_goals=["总结经验", "情感表达"],
                    difficulty_level=1,
                )
            ],
        }

        objectives = base_objectives.get(chapter_type, []).copy()

        # 添加教育目标
        if educational_goals:
            for goal in educational_goals:
                objectives.append(
                    ChapterObjective(
                        description=f"学习{goal}",
                        success_criteria=["理解概念", "能够应用"],
                        educational_goals=[goal],
                        difficulty_level=2,
                    )
                )

        return objectives


# 创建全局章节管理器实例
chapter_manager = ChapterManager()
