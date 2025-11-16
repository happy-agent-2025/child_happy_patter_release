from typing import Dict, Any, List
from core.openai_client import openai_client
from core.ollama_client import ollama_client
from config.settings import settings


class EmotionAgent:
    """
    情感代理，负责情感陪伴和心理支持
    """
    
    def __init__(self):
        # 定义情感陪伴的系统提示
        self.system_prompt = """
        你是一个专门为儿童设计的情感陪伴AI助手，你的职责是：
        1. 耐心倾听孩子的情感表达
        2. 给予理解和支持
        3. 帮助孩子识别和表达情绪
        4. 提供积极的心理引导
        5. 在适当时候给出建议
        6. 保持温暖、友善的语调
        7. 避免评判性的语言
        8. 在必要时建议寻求成人帮助
        """
        
        # 定义常见情绪类型和应对策略
        self.emotions = {
            "开心": {
                "description": "感到高兴、愉快",
                "response_strategy": "分享孩子的喜悦，鼓励他们继续保持积极心态"
            },
            "难过": {
                "description": "感到沮丧、悲伤",
                "response_strategy": "给予安慰和理解，帮助孩子表达情感"
            },
            "愤怒": {
                "description": "感到生气、恼火",
                "response_strategy": "帮助孩子理解愤怒的原因，引导他们用合适的方式表达"
            },
            "害怕": {
                "description": "感到恐惧、担心",
                "response_strategy": "提供安全感，帮助孩子面对恐惧"
            },
            "惊讶": {
                "description": "感到意外、震惊",
                "response_strategy": "与孩子一起探索新奇事物，鼓励好奇心"
            },
            "厌恶": {
                "description": "感到反感、不喜欢",
                "response_strategy": "尊重孩子的感受，帮助他们理解自己的喜好"
            },
            "焦虑": {
                "description": "感到紧张、不安",
                "response_strategy": "提供放松建议，帮助孩子缓解焦虑"
            },
            "孤独": {
                "description": "感到孤单、寂寞",
                "response_strategy": "给予陪伴感，鼓励孩子与他人建立联系"
            },
            "兴奋": {
                "description": "感到激动、热情",
                "response_strategy": "分享孩子的兴奋，引导他们合理表达热情"
            },
            "困惑": {
                "description": "感到迷茫、不解",
                "response_strategy": "耐心解答疑问，鼓励孩子继续探索"
            }
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
            {"role": "system", "content": "你是一个儿童情绪识别专家，严格按照要求格式回复。"},
            {"role": "user", "content": prompt}
        ]
        
        # 根据配置选择使用OpenAI还是Ollama
        if settings.use_ollama:
            response = ollama_client.chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=200
            )
        else:
            response = openai_client.chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=200
            )
        
        # 解析响应
        lines = response.strip().split('\n')
        result = {
            "emotion": "未知",
            "intensity": "中",
            "reason": "默认分析",
            "suggestion": "一般性关怀"
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
    
    def provide_emotional_support(self, content: str, emotion_analysis: Dict[str, Any]) -> str:
        """
        提供情感支持和陪伴
        """
        emotion = emotion_analysis.get("emotion", "未知")
        intensity = emotion_analysis.get("intensity", "中")
        suggestion = emotion_analysis.get("suggestion", "")
        
        # 获取情绪对应的应对策略
        emotion_info = self.emotions.get(emotion, {
            "description": "一般情绪",
            "response_strategy": "提供通用的情感支持"
        })
        
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
            {"role": "user", "content": prompt}
        ]
        
        # 根据配置选择使用OpenAI还是Ollama
        if settings.use_ollama:
            response = ollama_client.chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=400
            )
        else:
            response = openai_client.chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=400
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
                "suggestion": self.emotions[emotion_type]["response_strategy"]
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
            "status": "processed"
        }