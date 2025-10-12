"""
mem0集成模块 - 故事记忆管理系统

扩展现有mem0集成，专门支持故事世界的记忆存储、
检索和管理功能，优化性能并支持长期记忆管理。
"""

from typing import Dict, Any, List, Optional, TypedDict
from enum import Enum
import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging

# 导入mem0客户端
try:
    from mem0 import Memory
except ImportError:
    Memory = None

from config.settings import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryType(str, Enum):
    """记忆类型枚举"""

    WORLD_SETTING = "world_setting"  # 世界观设定
    CHARACTER_INFO = "role_info"  # 角色信息
    STORY_PROGRESS = "story_progress"  # 故事进度
    USER_PREFERENCE = "user_preference"  # 用户偏好
    INTERACTION_HISTORY = "interaction_history"  # 互动历史
    LEARNING_OUTCOME = "learning_outcome"  # 学习成果


@dataclass
class MemoryMetadata:
    """记忆元数据"""

    memory_id: str
    memory_type: MemoryType
    user_id: str
    story_id: Optional[str] = None
    chapter_id: Optional[str] = None
    role_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    importance_score: float = 0.5  # 0-1的重要性评分
    expiration_days: Optional[int] = None  # 过期天数，None表示永不过期


@dataclass
class MemorySearchResult:
    """记忆搜索结果"""

    memory_id: str
    content: str
    memory_type: MemoryType
    metadata: MemoryMetadata
    relevance_score: float
    context_summary: Optional[str] = None


class StoryMemoryManager:
    """
    故事记忆管理器

    基于mem0的增强记忆管理，专门支持：
    1. 世界观数据存储
    2. 角色记忆维护
    3. 故事进度跟踪
    4. 用户偏好学习
    5. 性能优化检索
    """

    def __init__(self):
        self.memory_client = self._init_memory_client()
        self.memory_cache: Dict[str, Dict[str, Any]] = {}  # 简单的内存缓存
        self.cache_ttl = 300  # 缓存5分钟
        self.performance_stats = {
            "total_searches": 0,
            "cache_hits": 0,
            "avg_search_time": 0.0,
            "memory_count": 0,
        }

        logger.info("故事记忆管理器初始化完成")

    def _init_memory_client(self) -> Optional[Memory]:
        """初始化mem0客户端"""
        if Memory is None:
            logger.warning("mem0 not available, running without persistent memory")
            return None

        try:
            # 使用Qdrant本地模式（Windows兼容，无需服务器）
            config = {
                "vector_store": {
                    "provider": "qdrant",
                    "config": {
                        "path": "./qdrant_db",  # 本地文件存储，无需服务器
                        "collection_name": "happy_partner",
                    },
                },
                "llm": {
                    "provider": "openai",
                    "config": {
                        "model": "qwen-turbo",
                        "temperature": 0.7,
                        "max_tokens": 2000,
                        "api_key": settings.openai_api_key,
                        "openai_base_url": settings.openai_base_url,
                    },
                },
                "embedder": {
                    "provider": "openai",
                    "config": {
                        "model": "text-embedding-3-small",
                        "api_key": settings.openai_api_key,
                        "openai_base_url": settings.openai_base_url,
                        "embedding_dims": 1536,
                    },
                },
            }
            logger.info("使用Qdrant本地模式初始化mem0客户端")
            return Memory.from_config(config_dict=config)
        except Exception as e:
            logger.error(f"初始化mem0客户端失败: {e}")
            # 尝试使用内存模式作为降级方案
            try:
                config = {
                    "llm": {
                        "provider": "openai",
                        "config": {
                            "model": "qwen-turbo",
                            "temperature": 0.7,
                            "max_tokens": 2000,
                            "api_key": settings.openai_api_key,
                            "openai_base_url": settings.openai_base_url,
                        },
                    },
                    "embedder": {
                        "provider": "openai",
                        "config": {
                            "model": "text-embedding-3-small",
                            "api_key": settings.openai_api_key,
                            "openai_base_url": settings.openai_base_url,
                            "embedding_dims": 1536,
                        },
                    },
                }
                logger.info("使用内存模式初始化mem0客户端")
                return Memory.from_config(config_dict=config)
            except Exception as e2:
                logger.error(f"内存模式也初始化失败: {e2}")
                return None

    def store_world_memory(
        self, world_data: Dict[str, Any], user_id: str, story_id: str
    ) -> str:
        """
        存储世界观记忆

        Args:
            world_data: 世界观数据
            user_id: 用户ID
            story_id: 故事ID

        Returns:
            记忆ID
        """
        try:
            # 构建记忆内容
            memory_content = f"""
故事世界观设定：
- 世界名称: {world_data.get('world_name', '未命名')}
- 世界类型: {world_data.get('world_type', '通用')}
- 背景设定: {world_data.get('background', '')}
- 世界规则: {world_data.get('rules', '')}
- 特色: {', '.join(world_data.get('features', []))}
- 推荐角色: {', '.join(world_data.get('roles', []))}
- 教育主题: {', '.join(world_data.get('themes', []))}
            """

            # 存储到mem0
            result = self.memory_client.add(
                messages=[{"role": "system", "content": memory_content}],
                user_id=user_id,
                metadata={
                    "memory_type": MemoryType.WORLD_SETTING.value,
                    "story_id": story_id,
                    "world_data": world_data,
                    "created_at": datetime.now().isoformat(),
                    "importance_score": 0.9,  # 世界观设定很重要
                },
            )

            memory_id = result.get("id", f"world_{story_id}_{int(time.time())}")

            # 更新缓存
            self._update_cache(
                memory_id,
                {
                    "content": memory_content,
                    "memory_type": MemoryType.WORLD_SETTING,
                    "metadata": {
                        "user_id": user_id,
                        "story_id": story_id,
                        "created_at": datetime.now().isoformat(),
                    },
                },
            )

            logger.info(f"存储世界观记忆: {memory_id}")
            return memory_id

        except Exception as e:
            logger.error(f"存储世界观记忆失败: {e}")
            return f"error_{int(time.time())}"

    def store_role_memory(
        self,
        role_data: Dict[str, Any],
        user_id: str,
        story_id: str,
        chapter_id: Optional[str] = None,
    ) -> str:
        """存储角色记忆"""
        try:
            memory_content = f"""
角色信息：
- 角色名称: {role_data.get('name', '')}
- 角色类型: {role_data.get('role', '')}
- 性格特点: {role_data.get('personality', '')}
- 背景故事: {role_data.get('background', '')}
- 特殊能力: {', '.join(role_data.get('special_abilities', []))}
- 安全规则: {', '.join(role_data.get('safety_rules', []))}
            """

            result = self.memory_client.add(
                messages=[{"role": "system", "content": memory_content}],
                user_id=user_id,
                metadata={
                    "memory_type": MemoryType.CHARACTER_INFO.value,
                    "story_id": story_id,
                    "chapter_id": chapter_id,
                    "role_data": role_data,
                    "created_at": datetime.now().isoformat(),
                    "importance_score": 0.8,
                },
            )

            memory_id = result.get(
                "id", f"char_{role_data.get('name', 'unknown')}_{int(time.time())}"
            )

            self._update_cache(
                memory_id,
                {
                    "content": memory_content,
                    "memory_type": MemoryType.CHARACTER_INFO,
                    "metadata": {
                        "user_id": user_id,
                        "story_id": story_id,
                        "chapter_id": chapter_id,
                    },
                },
            )

            logger.info(f"存储角色记忆: {memory_id}")
            return memory_id

        except Exception as e:
            logger.error(f"存储角色记忆失败: {e}")
            return f"error_{int(time.time())}"

    def store_story_progress(
        self,
        progress_data: Dict[str, Any],
        user_id: str,
        story_id: str,
        chapter_id: str,
    ) -> str:
        """存储故事进度"""
        try:
            memory_content = f"""
故事进度更新：
- 章节标题: {progress_data.get('chapter_title', '')}
- 当前进度: {progress_data.get('current_step', 0)}/{progress_data.get('total_steps', 0)}
- 完成度: {progress_data.get('completion_percentage', 0)}%
- 用户参与度: {progress_data.get('engagement_score', 0)}
- 用时: {progress_data.get('time_spent_minutes', 0)}分钟
- 重要事件: {progress_data.get('key_events', '无')}
            """

            result = self.memory_client.add(
                messages=[{"role": "system", "content": memory_content}],
                user_id=user_id,
                metadata={
                    "memory_type": MemoryType.STORY_PROGRESS.value,
                    "story_id": story_id,
                    "chapter_id": chapter_id,
                    "progress_data": progress_data,
                    "created_at": datetime.now().isoformat(),
                    "importance_score": 0.6,
                },
            )

            memory_id = result.get("id", f"progress_{chapter_id}_{int(time.time())}")

            self._update_cache(
                memory_id,
                {
                    "content": memory_content,
                    "memory_type": MemoryType.STORY_PROGRESS,
                    "metadata": {
                        "user_id": user_id,
                        "story_id": story_id,
                        "chapter_id": chapter_id,
                    },
                },
            )

            logger.info(f"存储故事进度: {memory_id}")
            return memory_id

        except Exception as e:
            logger.error(f"存储故事进度失败: {e}")
            return f"error_{int(time.time())}"

    def store_interaction_history(
        self,
        interaction_data: Dict[str, Any],
        user_id: str,
        story_id: str,
        chapter_id: str,
    ) -> str:
        """存储互动历史"""
        try:
            memory_content = f"""
故事互动记录：
- 角色: {interaction_data.get('role_name', '')}
- 用户输入: {interaction_data.get('user_message', '')}
- 角色回应: {interaction_data.get('role_response', '')[:200]}...
- 情感状态: {interaction_data.get('emotion', '')}
- 学习价值: {interaction_data.get('learning_point', '')}
            """

            result = self.memory_client.add(
                messages=[{"role": "system", "content": memory_content}],
                user_id=user_id,
                metadata={
                    "memory_type": MemoryType.INTERACTION_HISTORY.value,
                    "story_id": story_id,
                    "chapter_id": chapter_id,
                    "interaction_data": interaction_data,
                    "created_at": datetime.now().isoformat(),
                    "importance_score": 0.4,
                },
            )

            memory_id = result.get("id", f"interaction_{chapter_id}_{int(time.time())}")

            logger.info(f"存储互动历史: {memory_id}")
            return memory_id

        except Exception as e:
            logger.error(f"存储互动历史失败: {e}")
            return f"error_{int(time.time())}"

    def search_relevant_memories(
        self,
        query: str,
        user_id: str,
        story_id: Optional[str] = None,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 5,
    ) -> List[MemorySearchResult]:
        """
        搜索相关记忆

        Args:
            query: 搜索查询
            user_id: 用户ID
            story_id: 故事ID（可选）
            memory_types: 记忆类型过滤
            limit: 结果数量限制

        Returns:
            搜索结果列表
        """
        start_time = time.time()
        self.performance_stats["total_searches"] += 1

        try:
            # 检查缓存
            cache_key = f"{user_id}_{query}_{story_id or 'all'}"
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                self.performance_stats["cache_hits"] += 1
                return cached_result

            if not self.memory_client:
                return []

            # 构建搜索过滤器
            filters = {"user_id": user_id}
            if story_id:
                filters["story_id"] = story_id
            if memory_types:
                # mem0不支持多个memory_type过滤，使用第一个
                if len(memory_types) > 0:
                    filters["memory_type"] = memory_types[0].value

            # 执行搜索
            search_results = self.memory_client.search(
                query=query, user_id=user_id, limit=limit, filters=filters
            )

            # 处理搜索结果
            memories = []
            if isinstance(search_results, dict) and "results" in search_results:
                for result in search_results["results"]:
                    memory = self._convert_to_memory_result(result)
                    memories.append(memory)

            # 更新缓存
            self._update_cache(cache_key, memories)

            # 更新性能统计
            search_time = time.time() - start_time
            self.performance_stats["avg_search_time"] = (
                self.performance_stats["avg_search_time"]
                * (self.performance_stats["total_searches"] - 1)
                + search_time
            ) / self.performance_stats["total_searches"]

            logger.debug(
                f"记忆搜索完成: {len(memories)}个结果, 耗时{search_time:.3f}秒"
            )
            return memories

        except Exception as e:
            logger.error(f"记忆搜索失败: {e}")
            return []

    def _convert_to_memory_result(
        self, raw_result: Dict[str, Any]
    ) -> MemorySearchResult:
        """转换原始搜索结果为标准格式"""
        try:
            metadata = raw_result.get("metadata", {})
            memory_type = MemoryType(metadata.get("memory_type", "interaction_history"))

            return MemorySearchResult(
                memory_id=raw_result.get("id", ""),
                content=raw_result.get("memory", ""),
                memory_type=memory_type,
                metadata=MemoryMetadata(
                    memory_id=raw_result.get("id", ""),
                    memory_type=memory_type,
                    user_id=metadata.get("user_id", ""),
                    story_id=metadata.get("story_id"),
                    chapter_id=metadata.get("chapter_id"),
                    role_id=metadata.get("role_id"),
                    created_at=datetime.fromisoformat(
                        metadata.get("created_at", datetime.now().isoformat())
                    ),
                    importance_score=metadata.get("importance_score", 0.5),
                    access_count=metadata.get("access_count", 0),
                    last_accessed=(
                        datetime.fromisoformat(
                            metadata.get("last_accessed", datetime.now().isoformat())
                        )
                        if metadata.get("last_accessed")
                        else None
                    ),
                ),
                relevance_score=raw_result.get("score", 0.0),
                context_summary=raw_result.get("context_summary"),
            )
        except Exception as e:
            logger.error(f"转换记忆结果失败: {e}")
            # 返回默认结果
            return MemorySearchResult(
                memory_id=raw_result.get("id", "error"),
                content=raw_result.get("memory", "内容解析错误"),
                memory_type=MemoryType.INTERACTION_HISTORY,
                metadata=MemoryMetadata(
                    memory_id=raw_result.get("id", "error"),
                    memory_type=MemoryType.INTERACTION_HISTORY,
                    user_id="unknown",
                ),
                relevance_score=0.0,
            )

    def get_story_context(
        self, user_id: str, story_id: str, chapter_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取故事上下文信息

        Args:
            user_id: 用户ID
            story_id: 故事ID
            chapter_id: 章节ID（可选）

        Returns:
            故事上下文字典
        """
        try:
            # 搜索相关记忆
            world_memories = self.search_relevant_memories(
                query=f"故事 {story_id} 世界观设定",
                user_id=user_id,
                story_id=story_id,
                memory_types=[MemoryType.WORLD_SETTING],
                limit=3,
            )

            role_memories = self.search_relevant_memories(
                query=f"故事 {story_id} 角色信息",
                user_id=user_id,
                story_id=story_id,
                memory_types=[MemoryType.CHARACTER_INFO],
                limit=5,
            )

            progress_memories = self.search_relevant_memories(
                query=f"故事 {story_id} 进度",
                user_id=user_id,
                story_id=story_id,
                memory_types=[MemoryType.STORY_PROGRESS],
                limit=3,
            )

            # 构建上下文
            context = {
                "story_id": story_id,
                "user_id": user_id,
                "chapter_id": chapter_id,
                "world_settings": [mem.content for mem in world_memories],
                "role_info": [mem.content for mem in role_memories],
                "recent_progress": [mem.content for mem in progress_memories],
                "memory_summary": {
                    "total_memories": len(world_memories)
                    + len(role_memories)
                    + len(progress_memories),
                    "world_memory_count": len(world_memories),
                    "role_memory_count": len(role_memories),
                    "progress_memory_count": len(progress_memories),
                },
            }

            return context

        except Exception as e:
            logger.error(f"获取故事上下文失败: {e}")
            return {"story_id": story_id, "user_id": user_id, "error": str(e)}

    def update_user_preferences(
        self, user_id: str, preferences: Dict[str, Any]
    ) -> bool:
        """更新用户偏好"""
        try:
            preference_content = f"""
用户偏好更新：
- 偏好类型: {preferences.get('type', '')}
- 偏好内容: {preferences.get('content', '')}
- 偏好值: {preferences.get('value', '')}
- 更新时间: {datetime.now().isoformat()}
            """

            self.memory_client.add(
                messages=[{"role": "system", "content": preference_content}],
                user_id=user_id,
                metadata={
                    "memory_type": MemoryType.USER_PREFERENCE.value,
                    "preferences": preferences,
                    "created_at": datetime.now().isoformat(),
                    "importance_score": 0.7,
                },
            )

            logger.info(f"更新用户偏好: {user_id}")
            return True

        except Exception as e:
            logger.error(f"更新用户偏好失败: {e}")
            return False

    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """获取用户偏好"""
        try:
            preference_memories = self.search_relevant_memories(
                query="用户偏好",
                user_id=user_id,
                memory_types=[MemoryType.USER_PREFERENCE],
                limit=10,
            )

            preferences = {}
            for memory in preference_memories:
                if memory.metadata and "preferences" in memory.metadata:
                    pref_data = memory.metadata["preferences"]
                    preferences[pref_data.get("type", "unknown")] = pref_data.get(
                        "value", ""
                    )

            return preferences

        except Exception as e:
            logger.error(f"获取用户偏好失败: {e}")
            return {}

    def cleanup_expired_memories(self, days_threshold: int = 30) -> int:
        """清理过期记忆"""
        try:
            # 这里需要根据mem0的实际API来实现
            # 目前返回模拟结果
            logger.info(f"清理 {days_threshold} 天前的过期记忆")
            return 0  # 返回清理的记忆数量

        except Exception as e:
            logger.error(f"清理过期记忆失败: {e}")
            return 0

    def get_memory_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """获取记忆统计信息"""
        try:
            stats = {
                "performance": self.performance_stats.copy(),
                "cache_size": len(self.memory_cache),
                "memory_types": {},
                "user_memories": {},
            }

            if user_id:
                # 获取特定用户的记忆统计
                user_stats = {}
                for memory_type in MemoryType:
                    memories = self.search_relevant_memories(
                        query="", user_id=user_id, memory_types=[memory_type], limit=100
                    )
                    user_stats[memory_type.value] = len(memories)

                stats["user_memories"][user_id] = user_stats

            return stats

        except Exception as e:
            logger.error(f"获取记忆统计失败: {e}")
            return {"error": str(e)}

    def _update_cache(self, key: str, data: Any) -> None:
        """更新缓存"""
        self.memory_cache[key] = {"data": data, "timestamp": time.time()}

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """从缓存获取数据"""
        cached_item = self.memory_cache.get(key)
        if cached_item and time.time() - cached_item["timestamp"] < self.cache_ttl:
            return cached_item["data"]
        return None

    def clear_cache(self) -> None:
        """清理缓存"""
        self.memory_cache.clear()
        logger.info("记忆缓存已清理")


# 创建全局记忆管理器实例
story_memory_manager = StoryMemoryManager()
