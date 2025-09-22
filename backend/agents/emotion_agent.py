from typing import Dict, Any, List
from utils.openai_client import openai_client
from utils.ollama_client import ollama_client
from config.settings import settings


class EmotionAgent:
    """
    情感代理，负责情感陪伴和心理支持
    """

    def __init__(self):
        # 定义情感陪伴的系统提示
        self.system_prompt = """
            你是AI玩伴泡泡，用最简洁自然的语言与3-5岁儿童对话。所有系统功能在后台静默运行，前端只输出纯对话内容。你的本质是一个：
            1. 情绪容器：帮助儿童识别和表达感受
            2. 探索伙伴：通过提问激发好奇心
            3. 安全基地：提供稳定可靠的回应
            4. 语言脚手架：在儿童现有能力上+1级发展支持

            禁止行为清单：
            ✗ 使用拟人化动作描述（如"蹲下""摸头"）
            ✗ 给出具体医疗/养育建议
            ✗ 存储或重复儿童个人信息
            ✗ 使用负面强化语言（如"不行""错了"）

            #### 心理学增强模块
            1. 情绪响应协议
            当孩子表达情绪时：
            - 害怕 → "害怕像只小兔子在心里跳，我们一起轻轻抱住它~深呼吸，呼——"
            - 生气 → "红色火焰在跳舞呢！用魔法吹气：呼——呼——"
            - 伤心 → "心里下雨了吗？让我为你撑把小伞..."
            - 开心 → "笑容像彩虹糖在跳舞！"

            2. 认知发展支持
            - 象征思维："你的玩偶今天想听什么故事？"
            - 守恒练习："把橡皮泥变成长蛇，它还是原来的大小吗？"
            - 去中心化："小猫看到你躲起来，它会怎么想呢？"

            3. 语言发展策略
            - 词汇扩展：孩子说"车" → "是蓝色的救护车在唱歌吗？"
            - 语法修复：孩子说"宝宝摔" → "宝宝摔倒了，膝盖有点痛对吗？"

            #### 安全交互框架
            1. 三层过滤系统
            1. 基础层：屏蔽暴力/成人/隐私相关词
            2. 隐喻层：检测潜在负面隐喻（如"想消失"）
            3. 语境层：分析对话序列中的风险模式

            2. 危险话题响应模板
            - 自伤倾向 → "我们找大人一起保护你"
            - 家庭冲突 → "有些事需要大人帮忙解决"
            - 死亡话题 → "生命像四季，现在我们是春天"

            #### 对话生成规范
            1. 语言特征
            - 句子长度：4-12字
            - 词汇难度：儿童常用词+5%新词

            2. 风格模板
            ```
            - [情绪标签] + [感官比喻] + [开放结尾]
            示例：
                像彩虹糖在跳舞~你最喜欢哪种颜色？
                这个问题像打结的鞋带，我们一起慢慢解...
            - [情绪标签] 不要输出到回答中
            ```

            3. 特殊情景处理
            - 重复提问 → 阶梯式回答（每次增加1个新信息）
            - 虚构朋友 → "你的恐龙朋友今天想吃什么？
        """

        # 定义常见情绪类型和应对策略
        self.emotions = {
            "开心": {
                "description": "感到高兴、愉快",
                "response_strategy": "分享孩子的喜悦，鼓励他们继续保持积极心态",
            },
            "难过": {
                "description": "感到沮丧、悲伤",
                "response_strategy": "给予安慰和理解，帮助孩子表达情感",
            },
            "愤怒": {
                "description": "感到生气、恼火",
                "response_strategy": "帮助孩子理解愤怒的原因，引导他们用合适的方式表达",
            },
            "害怕": {
                "description": "感到恐惧、担心",
                "response_strategy": "提供安全感，帮助孩子面对恐惧",
            },
            "惊讶": {
                "description": "感到意外、震惊",
                "response_strategy": "与孩子一起探索新奇事物，鼓励好奇心",
            },
            "厌恶": {
                "description": "感到反感、不喜欢",
                "response_strategy": "尊重孩子的感受，帮助他们理解自己的喜好",
            },
            "焦虑": {
                "description": "感到紧张、不安",
                "response_strategy": "提供放松建议，帮助孩子缓解焦虑",
            },
            "孤独": {
                "description": "感到孤单、寂寞",
                "response_strategy": "给予陪伴感，鼓励孩子与他人建立联系",
            },
            "兴奋": {
                "description": "感到激动、热情",
                "response_strategy": "分享孩子的兴奋，引导他们合理表达热情",
            },
            "困惑": {
                "description": "感到迷茫、不解",
                "response_strategy": "耐心解答疑问，鼓励孩子继续探索",
            },
        }

    def analyze_emotion(self, content: str) -> Dict[str, Any]:
        """
        分析用户表达的情绪
        """
        # 构造提示词
        emotion_types = list(self.emotions.keys())
        prompt = f"""
        请分析以下孩子表达的内容中体现的情绪：
        "{content}"
        
        可能的情绪类型包括：{', '.join(emotion_types)}
        
        请按以下格式回复：
        情绪类型: [主要情绪]
        情绪强度: [低/中/高]
        分析理由: [简要说明判断依据]
        应对建议: [针对该情绪的初步应对建议]
        """

        messages = [
            {
                "role": "system",
                "content": "你是一个儿童情绪识别专家，严格按照要求格式回复。",
            },
            {"role": "user", "content": prompt},
        ]

        # 根据配置选择使用OpenAI还是Ollama
        if settings.use_ollama:
            response = ollama_client.chat_completion(
                messages=messages, temperature=0.3, max_tokens=200
            )
        else:
            response = openai_client.chat_completion(
                messages=messages, temperature=0.3, max_tokens=200
            )

        # 解析响应
        lines = response.strip().split("\n")
        result = {
            "emotion": "未知",
            "intensity": "中",
            "reason": "默认分析",
            "suggestion": "一般性关怀",
        }

        for line in lines:
            if line.startswith("情绪类型:"):
                result["emotion"] = line.replace("情绪类型:", "").strip()
            elif line.startswith("情绪强度:"):
                result["intensity"] = line.replace("情绪强度:", "").strip()
            elif line.startswith("分析理由:"):
                result["reason"] = line.replace("分析理由:", "").strip()
            elif line.startswith("应对建议:"):
                result["suggestion"] = line.replace("应对建议:", "").strip()

        return result

    def provide_emotional_support(
        self, content: str, emotion_analysis: Dict[str, Any]
    ) -> str:
        """
        提供情感支持和陪伴
        """
        emotion = emotion_analysis.get("emotion", "未知")
        intensity = emotion_analysis.get("intensity", "中")
        suggestion = emotion_analysis.get("suggestion", "")

        # 获取情绪对应的应对策略
        emotion_info = self.emotions.get(
            emotion,
            {"description": "一般情绪", "response_strategy": "提供通用的情感支持"},
        )

        # 构造提示词
        prompt = f"""
        一个孩子表达了以下内容: "{content}"
        情绪分析结果: 情绪类型为{emotion}，强度为{intensity}
        情绪描述: {emotion_info["description"]}
        初步应对建议: {suggestion}
        推荐应对策略: {emotion_info["response_strategy"]}
        
        请根据以下要求提供情感支持：
        1. 表达理解和共情
        2. 给予适当安慰
        3. 保持积极正面的态度
        4. 鼓励孩子表达更多感受
        5. 结合推荐应对策略给出建设性建议
        6. 用温暖、友善的语言
        7. 如果情绪强度很高，建议寻求成人帮助
        """

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]

        # 根据配置选择使用OpenAI还是Ollama
        if settings.use_ollama:
            response = ollama_client.chat_completion(
                messages=messages, temperature=0.7, max_tokens=400
            )
        else:
            response = openai_client.chat_completion(
                messages=messages, temperature=0.7, max_tokens=400
            )

        return response

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理情感陪伴请求
        """
        content = request.get("content", "")
        user_id = request.get("user_id", "unknown_user")
        emotion_type = request.get("emotion_type", None)

        # 如果指定了情绪类型，直接使用
        if emotion_type and emotion_type in self.emotions:
            emotion_analysis = {
                "emotion": emotion_type,
                "intensity": "中",
                "reason": "用户指定",
                "suggestion": self.emotions[emotion_type]["response_strategy"],
            }
        else:
            # 分析情绪
            emotion_analysis = self.analyze_emotion(content)

        # 提供情感支持
        support_response = self.provide_emotional_support(content, emotion_analysis)

        return {
            "agent": "emotion",
            "user_id": user_id,
            "content": content,
            "emotion_analysis": emotion_analysis,
            "response": support_response,
            "status": "processed",
        }
