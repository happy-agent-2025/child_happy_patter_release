from typing import Dict, Any, List
from utils.openai_client import openai_client


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
        
        # 定义常见情绪类型
        self.emotion_types = [
            "开心", "难过", "愤怒", "害怕", "惊讶", "厌恶", "焦虑", "孤独", "兴奋", "困惑"
        ]
    
    def analyze_emotion(self, content: str) -> Dict[str, Any]:
        """
        分析用户表达的情绪
        """
        # 构造提示词
        prompt = f"""
        请分析以下孩子表达的内容中体现的情绪：
        "{content}"
        
        可能的情绪类型包括：{', '.join(self.emotion_types)}
        
        请按以下格式回复：
        情绪类型: [主要情绪]
        情绪强度: [低/中/高]
        分析理由: [简要说明判断依据]
        """
        
        messages = [
            {"role": "system", "content": "你是一个儿童情绪识别专家，严格按照要求格式回复。"},
            {"role": "user", "content": prompt}
        ]
        
        # 调用OpenAI API进行情绪分析
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
            "reason": "默认分析"
        }
        
        for line in lines:
            if line.startswith("情绪类型:"):
                result["emotion"] = line.replace("情绪类型:", "").strip()
            elif line.startswith("情绪强度:"):
                result["intensity"] = line.replace("情绪强度:", "").strip()
            elif line.startswith("分析理由:"):
                result["reason"] = line.replace("分析理由:", "").strip()
        
        return result
    
    def provide_emotional_support(self, content: str, emotion_analysis: Dict[str, Any]) -> str:
        """
        提供情感支持和陪伴
        """
        emotion = emotion_analysis.get("emotion", "未知")
        intensity = emotion_analysis.get("intensity", "中")
        
        # 构造提示词
        prompt = f"""
        一个孩子表达了以下内容: "{content}"
        情绪分析结果: 情绪类型为{emotion}，强度为{intensity}
        
        请根据以下要求提供情感支持：
        1. 表达理解和共情
        2. 给予适当安慰
        3. 保持积极正面的态度
        4. 鼓励孩子表达更多感受
        5. 在必要时给出建设性建议
        6. 用温暖、友善的语言
        """
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # 调用OpenAI API提供情感支持
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