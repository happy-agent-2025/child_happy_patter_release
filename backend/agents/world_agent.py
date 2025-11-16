"""
世界观生成智能体 - 儿童友好的故事世界创建系统

基于用户输入生成适合儿童的故事世界观，包含安全检查、模板匹配、
AI生成和内容验证功能。
"""

from typing import Dict, Any, List, Optional, TypedDict
from enum import Enum
import json
import re
from datetime import datetime
from dataclasses import dataclass

from core.openai_client import openai_client
from agents.safety_agent import SafetyAgent


class WorldType(str, Enum):
    """故事世界类型枚举"""

    MAGIC_FOREST = "魔法森林"
    OCEAN_ADVENTURE = "海洋探险"
    SPACE_ADVENTURE = "太空冒险"
    DINOSAUR_WORLD = "恐龙乐园"
    PRINCESS_CASTLE = "公主城堡"
    ANIMAL_FARM = "动物农场"
    CUSTOM = "自定义"


class SafetyLevel(str, Enum):
    """安全等级"""

    SAFE = "安全"
    WARNING = "需要警告"
    UNSAFE = "不安全"


@dataclass
class RoleTemplate:
    """角色模板"""

    name: str
    personality: str
    background: str
    age_group: str  # 幼儿(3-6), 儿童(7-12), 少年(13+)


class StoryWorld(TypedDict):
    """故事世界数据结构"""

    world_id: str  # 世界唯一ID
    world_name: str  # 世界名称
    world_type: str  # 世界类型
    background: str  # 背景设定
    rules: str  # 世界规则
    features: List[str]  # 世界特色
    roles: List[str]  # 推荐角色
    themes: List[str]  # 教育主题
    target_age: str  # 目标年龄
    safety_level: SafetyLevel  # 安全等级
    created_by: str  # 创建者用户ID
    created_at: str  # 创建时间
    metadata: Dict[str, Any]  # 额外元数据


class WorldBuilderResult(TypedDict):
    """世界观构建结果"""

    success: bool  # 是否成功
    world: Optional[StoryWorld]  # 生成的世界观
    safety_check: Dict[str, Any]  # 安全检查结果
    warnings: List[str]  # 警告信息
    error: Optional[str]  # 错误信息
    generation_time: float  # 生成耗时(秒)


class WorldAgent:
    """
    世界观生成智能体

    功能：
    1. 基于用户输入生成儿童友好的故事世界观
    2. 集成安全检查机制
    3. 支持多种预设模板和自定义生成
    4. 内容验证和优化
    """

    def __init__(self):
        self.safety_agent = SafetyAgent()

        # 儿童友好的预设世界模板
        self.world_templates = {
            WorldType.MAGIC_FOREST: {
                "name": "魔法森林",
                "description": "一个充满神奇动物的森林，小动物们都会魔法！",
                "features": [
                    "会说话的小动物",
                    "神奇的树木",
                    "闪闪发光的萤火虫",
                    "友善的小精灵",
                ],
                "roles": ["小魔法师", "勇敢的小兔子", "聪明的小狐狸", "会飞的小鸟"],
                "themes": ["友谊", "勇气", "帮助他人", "保护自然"],
                "rules": "在这里，魔法是用来帮助别人的，所有生物都是友善的朋友。",
                "target_age": "3-12岁",
            },
            WorldType.OCEAN_ADVENTURE: {
                "name": "海底世界",
                "description": "美丽的大海深处，有很多可爱的海洋朋友！",
                "features": [
                    "彩色的珊瑚",
                    "会唱歌的鱼",
                    "友好的海豚",
                    "神秘的海底城堡",
                ],
                "roles": ["小美人鱼", "勇敢的小海龟", "聪明的小章鱼", "友好的鲨鱼"],
                "themes": ["探索", "友谊", "保护海洋", "团队合作"],
                "rules": "海洋是一个奇妙的世界，我们要保护所有的海洋生物。",
                "target_age": "3-12岁",
            },
            WorldType.SPACE_ADVENTURE: {
                "name": "太空冒险",
                "description": "在星星之间旅行，和外星朋友一起玩耍！",
                "features": [
                    "闪闪的星星",
                    "彩色的星球",
                    "友好的外星人",
                    "神奇的太空船",
                ],
                "roles": ["小宇航员", "可爱的外星人", "聪明的机器人", "勇敢的太空猫"],
                "themes": ["探索", "友谊", "勇敢", "帮助他人"],
                "rules": "太空中充满了未知的奇迹，每个星球都有自己的特色。",
                "target_age": "5-12岁",
            },
            WorldType.DINOSAUR_WORLD: {
                "name": "恐龙乐园",
                "description": "和友善的小恐龙们一起在史前世界玩耍！",
                "features": ["绿色的草地", "高大的树木", "友好的恐龙", "古老的蛋"],
                "roles": ["小霸王龙", "温和的三角龙", "会飞的翼龙", "聪明的小人类"],
                "themes": ["友谊", "勇敢", "保护动物", "分享"],
                "rules": "虽然恐龙看起来很强大，但他们其实都很友善。",
                "target_age": "4-12岁",
            },
            WorldType.PRINCESS_CASTLE: {
                "name": "公主城堡",
                "description": "美丽的城堡里，有公主、王子和神奇的魔法！",
                "features": [
                    "高高的塔楼",
                    "美丽的花园",
                    "神奇的魔法棒",
                    "友善的独角兽",
                ],
                "roles": ["小公主", "勇敢的王子", "神奇的小仙女", "友好的小龙"],
                "themes": ["善良", "勇气", "友谊", "帮助他人"],
                "rules": "在城堡里，每个人都要互相帮助，用魔法做好事。",
                "target_age": "3-10岁",
            },
            WorldType.ANIMAL_FARM: {
                "name": "快乐农场",
                "description": "热闹的农场里，小动物们每天都过得很开心！",
                "features": ["绿色的草地", "红色的谷仓", "可爱的小动物", "新鲜的蔬菜"],
                "roles": ["农场小主人", "聪明的小猪", "可爱的小羊", "勤劳的小鸡"],
                "themes": ["勤劳", "友谊", "分享", "照顾动物"],
                "rules": "农场里每个动物都有自己的工作，大家一起努力让农场更美好。",
                "target_age": "3-8岁",
            },
        }

        # 教育主题库
        self.educational_themes = {
            "友谊": ["友爱", "合作", "分享", "理解", "帮助"],
            "勇气": ["勇敢", "坚强", "面对困难", "不怕挑战", "尝试新事物"],
            "善良": ["关心他人", "爱心", "同情心", "乐于助人", "慷慨"],
            "探索": ["好奇心", "发现", "学习", "观察", "提问"],
            "责任": ["承担任务", "守信", "照顾", "保护", "完成工作"],
            "诚实": ["说真话", "承认错误", "不欺骗", "坦率", "正直"],
        }

    def create_world(
        self,
        user_description: str,
        user_id: str,
        world_type: Optional[WorldType] = None,
        target_age: str = "3-12岁",
    ) -> WorldBuilderResult:
        """
        创建故事世界的主要入口

        Args:
            user_description: 用户的描述
            user_id: 用户ID
            world_type: 指定的世界类型（可选）
            target_age: 目标年龄

        Returns:
            WorldBuilderResult: 构建结果
        """
        start_time = datetime.now()

        try:
            # 1. 安全检查
            safety_result = self._safety_check_content(user_description, user_id)
            if safety_result["level"] == SafetyLevel.UNSAFE:
                return {
                    "success": False,
                    "world": None,
                    "safety_check": safety_result,
                    "warnings": [],
                    "error": "内容不安全，无法创建世界观",
                    "generation_time": (datetime.now() - start_time).total_seconds(),
                }

            # 2. 世界类型匹配
            matched_type = self._match_world_type(user_description, world_type)

            # 3. 生成世界观
            if matched_type in self.world_templates:
                world = self._create_from_template(
                    matched_type, user_description, user_id, target_age
                )
            else:
                world = self._create_custom_world(user_description, user_id, target_age)

            # 4. 内容优化和验证
            world = self._optimize_and_validate(world, safety_result)

            # 5. 生成唯一ID
            world["world_id"] = self._generate_world_id(user_id)

            generation_time = (datetime.now() - start_time).total_seconds()

            return {
                "success": True,
                "world": world,
                "safety_check": safety_result,
                "warnings": safety_result.get("warnings", []),
                "error": None,
                "generation_time": generation_time,
            }

        except Exception as e:
            return {
                "success": False,
                "world": None,
                "safety_check": {"level": SafetyLevel.UNSAFE, "reasons": [str(e)]},
                "warnings": [],
                "error": f"世界观创建失败: {str(e)}",
                "generation_time": (datetime.now() - start_time).total_seconds(),
            }

    def _safety_check_content(self, content: str, user_id: str) -> Dict[str, Any]:
        """内容安全检查"""
        try:
            # 使用现有安全代理
            safety_check = self.safety_agent.validate_content(content)

            # 扩展安全检查逻辑
            warnings = []
            dangerous_keywords = ["暴力", "武器", "战斗", "恐怖", "血腥", "死亡"]
            for keyword in dangerous_keywords:
                if keyword in content:
                    warnings.append(f"检测到可能不适宜的内容: {keyword}")

            # 确定安全等级
            if safety_check.get("is_safe", False) and not warnings:
                level = SafetyLevel.SAFE
            elif warnings:
                level = SafetyLevel.WARNING
            else:
                level = SafetyLevel.UNSAFE

            return {"level": level, "reasons": warnings, "original_check": safety_check}

        except Exception as e:
            return {
                "level": SafetyLevel.WARNING,
                "reasons": [f"安全检查失败: {str(e)}"],
                "original_check": None,
            }

    def _match_world_type(
        self, description: str, specified_type: Optional[WorldType]
    ) -> WorldType:
        """匹配世界类型"""
        if specified_type:
            return specified_type

        desc_lower = description.lower()

        # 关键词匹配
        type_keywords = {
            WorldType.MAGIC_FOREST: ["魔法", "森林", "精灵", "仙女", "巫师"],
            WorldType.OCEAN_ADVENTURE: ["海洋", "海底", "鱼", "海豚", "潜水"],
            WorldType.SPACE_ADVENTURE: ["太空", "星星", "宇宙", "外星人", "星球"],
            WorldType.DINOSAUR_WORLD: ["恐龙", "史前", "蛋", "远古"],
            WorldType.PRINCESS_CASTLE: ["公主", "王子", "城堡", "独角兽", "国王"],
            WorldType.ANIMAL_FARM: ["动物", "农场", "小鸡", "小猪", "小羊"],
        }

        # 计算每种类型的匹配分数
        best_type = WorldType.CUSTOM
        best_score = 0

        for world_type, keywords in type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in desc_lower)
            if score > best_score:
                best_score = score
                best_type = world_type

        return best_type

    def _create_from_template(
        self,
        world_type: WorldType,
        user_description: str,
        user_id: str,
        target_age: str,
    ) -> StoryWorld:
        """基于模板创建世界观"""
        template = self.world_templates[world_type]

        # 使用AI生成个性化内容
        personalized_content = self._generate_personalized_content(
            user_description, template, target_age
        )

        return {
            "world_name": personalized_content.get("world_name", template["name"]),
            "world_type": world_type.value,
            "background": personalized_content.get(
                "background", template["description"]
            ),
            "rules": personalized_content.get("rules", template["rules"]),
            "features": personalized_content.get("features", template["features"]),
            "roles": personalized_content.get("roles", template["roles"]),
            "themes": personalized_content.get("themes", template["themes"]),
            "target_age": target_age,
            "safety_level": SafetyLevel.SAFE,
            "created_by": user_id,
            "created_at": datetime.now().isoformat(),
            "metadata": {
                "template_used": world_type.value,
                "user_description": user_description,
                "personalization_score": personalized_content.get("score", 0.8),
            },
        }

    def _create_custom_world(
        self, user_description: str, user_id: str, target_age: str
    ) -> StoryWorld:
        """创建自定义世界观"""
        ai_result = self._generate_custom_world_ai(user_description, target_age)

        return {
            "world_name": ai_result.get("world_name", "自定义世界"),
            "world_type": WorldType.CUSTOM.value,
            "background": ai_result.get("background", user_description),
            "rules": ai_result.get("rules", "在这个世界中，我们要友善相处，互相帮助。"),
            "features": ai_result.get("features", ["神奇的冒险", "有趣的朋友"]),
            "roles": ai_result.get("roles", ["小英雄", "智慧导师"]),
            "themes": ai_result.get("themes", ["友谊", "勇气"]),
            "target_age": target_age,
            "safety_level": SafetyLevel.SAFE,
            "created_by": user_id,
            "created_at": datetime.now().isoformat(),
            "metadata": {
                "generation_method": "ai_custom",
                "user_description": user_description,
                "ai_confidence": ai_result.get("confidence", 0.7),
            },
        }

    def _generate_personalized_content(
        self, user_description: str, template: Dict[str, Any], target_age: str
    ) -> Dict[str, Any]:
        """生成个性化内容"""
        try:
            prompt = f"""
            请基于用户的描述，为儿童故事世界生成个性化的内容。

            模板世界: {template['name']}
            模板描述: {template['description']}
            用户描述: {user_description}
            目标年龄: {target_age}

            请生成JSON格式的个性化内容，包含：
            {{
                "world_name": "更适合用户描述的世界名称",
                "background": "结合用户描述的背景设定",
                "rules": "适合儿童的世界规则",
                "features": ["特色1", "特色2", "特色3", "特色4"],
                "roles": ["角色1", "角色2", "角色3", "角色4"],
                "themes": ["主题1", "主题2", "主题3", "主题4"],
                "score": 0.0-1.0之间的匹配度分数
            }}

            要求：
            1. 内容必须适合{target_age}的儿童
            2. 保持积极向上，有教育意义
            3. 融入用户的描述元素
            4. 确保内容安全、友善
            """

            response = self._call_ai_api(prompt)
            result = json.loads(response)

            # 验证和清理内容
            return self._validate_ai_content(result)

        except Exception as e:
            # AI生成失败，返回模板默认内容
            return {
                "world_name": template["name"],
                "background": template["description"],
                "rules": template["rules"],
                "features": template["features"],
                "roles": template["roles"],
                "themes": template["themes"],
                "score": 0.6,
            }

    def _generate_custom_world_ai(
        self, user_description: str, target_age: str
    ) -> Dict[str, Any]:
        """使用AI生成自定义世界观"""
        try:
            prompt = f"""
            请基于用户描述，创建一个全新的儿童友好故事世界。

            用户描述: {user_description}
            目标年龄: {target_age}

            请生成JSON格式的世界观设定：
            {{
                "world_name": "吸引儿童的世界名称",
                "background": "详细但简单的背景描述",
                "rules": "简单易懂的世界规则",
                "features": ["特色1", "特色2", "特色3", "特色4"],
                "roles": ["角色1", "角色2", "角色3", "角色4"],
                "themes": ["教育主题1", "教育主题2", "主题3", "主题4"],
                "confidence": 0.0-1.0之间的置信度
            }}

            要求：
            1. 内容必须积极向上，适合儿童
            2. 包含教育意义和正面价值观
            3. 想象力丰富但不过于复杂
            4. 确保内容安全、友善、适合{target_age}儿童
            """

            response = self._call_ai_api(prompt)
            result = json.loads(response)

            return self._validate_ai_content(result)

        except Exception as e:
            # AI生成失败，返回安全的默认内容
            return {
                "world_name": "奇妙世界",
                "background": "这是一个充满奇迹的世界，等待我们去探索。",
                "rules": "在这里，我们要友善相处，互相帮助。",
                "features": ["神奇的冒险", "有趣的朋友", "美丽的景色", "快乐的游戏"],
                "roles": ["小探索者", "智慧导师", "勇敢的朋友", "神奇的小动物"],
                "themes": ["友谊", "勇气", "学习", "分享"],
                "confidence": 0.5,
            }

    def _validate_ai_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """验证和清理AI生成的内容"""
        # 确保所有必需字段存在
        required_fields = [
            "world_name",
            "background",
            "rules",
            "features",
            "roles",
            "themes",
        ]
        for field in required_fields:
            if field not in content:
                content[field] = self._get_default_for_field(field)

        # 清理文本内容
        text_fields = ["world_name", "background", "rules"]
        for field in text_fields:
            if isinstance(content[field], str):
                # 移除可能的不当内容
                content[field] = self._clean_text(content[field])

        # 确保列表字段格式正确
        list_fields = ["features", "roles", "themes"]
        for field in list_fields:
            if isinstance(content[field], list):
                # 限制列表长度
                content[field] = content[field][:6]
                # 清理列表项
                content[field] = [
                    self._clean_text(str(item)) for item in content[field]
                ]
            else:
                content[field] = self._get_default_for_field(field)

        # 确保分数在合理范围内
        if "score" in content:
            content["score"] = max(0.0, min(1.0, float(content.get("score", 0.5))))
        if "confidence" in content:
            content["confidence"] = max(
                0.0, min(1.0, float(content.get("confidence", 0.5)))
            )

        return content

    def _clean_text(self, text: str) -> str:
        """清理文本内容"""
        # 移除特殊字符和潜在不当内容
        text = re.sub(r'[<>"\'\(\)]', "", text)
        # 限制长度
        return text[:200]

    def _get_default_for_field(self, field: str) -> Any:
        """获取字段的默认值"""
        defaults = {
            "world_name": "奇妙世界",
            "background": "一个充满奇迹的世界",
            "rules": "友善相处，互相帮助",
            "features": ["神奇的冒险", "有趣的朋友"],
            "roles": ["小英雄", "智慧导师"],
            "themes": ["友谊", "勇气"],
        }
        return defaults.get(field, "")

    def _optimize_and_validate(
        self, world: StoryWorld, safety_result: Dict[str, Any]
    ) -> StoryWorld:
        """优化和验证世界观"""
        # 根据安全检查结果调整安全等级
        if safety_result["level"] == SafetyLevel.WARNING:
            world["safety_level"] = SafetyLevel.WARNING
        else:
            world["safety_level"] = SafetyLevel.SAFE

        # 确保主题包含教育意义
        current_themes = set(world.get("themes", []))
        if not any(theme in self.educational_themes for theme in current_themes):
            world["themes"].extend(["友谊", "勇气"])

        # 确保角色名称儿童友好
        world["roles"] = [
            self._make_child_friendly_name(name) for name in world.get("roles", [])
        ]

        return world

    def _make_child_friendly_name(self, name: str) -> str:
        """使角色名称更儿童友好"""
        friendly_prefixes = ["小", "勇敢的", "聪明的", "可爱的"]
        if not any(prefix in name for prefix in friendly_prefixes):
            return f"小{name}"
        return name

    def _call_ai_api(self, prompt: str) -> str:
        """调用AI API（使用现有多模型支持）"""
        messages = [
            {
                "role": "system",
                "content": "你是一个儿童故事创作助手，专门创作适合儿童的正面内容。",
            },
            {"role": "user", "content": prompt},
        ]

        response = openai_client.chat_completion(
            messages=messages, temperature=0.7, max_tokens=1000
        )

        return response.strip()

    def _generate_world_id(self, user_id: str) -> str:
        """生成世界唯一ID"""
        import uuid

        return f"world_{user_id}_{uuid.uuid4().hex[:8]}"

    def get_world_templates(self) -> Dict[str, Any]:
        """获取可用的世界模板"""
        return {
            "templates": self.world_templates,
            "educational_themes": self.educational_themes,
        }

    def update_world(
        self, world_id: str, updates: Dict[str, Any], user_id: str
    ) -> WorldBuilderResult:
        """更新现有世界观"""
        # 这里可以集成mem0来存储和更新世界观
        # 暂时返回不支持的结果
        return {
            "success": False,
            "world": None,
            "safety_check": {
                "level": SafetyLevel.WARNING,
                "reasons": ["世界观更新功能暂未实现"],
            },
            "warnings": ["世界观更新功能暂未实现"],
            "error": "世界观更新功能暂未实现",
            "generation_time": 0.0,
        }


# 创建全局世界观构建智能体实例
world_agent = WorldAgent()
