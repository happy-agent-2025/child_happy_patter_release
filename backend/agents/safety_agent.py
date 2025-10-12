from typing import Dict, Any, List
from utils.openai_client import openai_client
import re


class SafetyAgent:
    """
    安全代理，负责内容过滤和安全审查
    """
    
    def __init__(self):
        # 定义儿童友好的安全指导原则
        self.safety_guidelines = """
        儿童内容安全指导原则：
        1. 禁止暴力、血腥、危险行为相关内容
        2. 禁止成人内容、性暗示相关内容
        3. 禁止鼓励违法行为、反社会行为
        4. 禁止自我伤害、自杀相关内容
        5. 禁止恶意欺骗、诱导行为
        6. 禁止泄露个人隐私信息
        7. 禁止不实医疗、健康建议
        8. 禁止歧视性、仇恨性言论
        """
        
        # 定义敏感关键词列表（第一层过滤）
        self.sensitive_keywords = {
            # 暴力相关
            'violence': ['暴力', '打斗', '武器', '刀', '枪', '血腥', '死亡', '杀害', '伤害', '打架'],
            # 成人内容相关
            'adult': ['色情', '性爱', '裸体', '成人', '性暗示', '性行为'],
            # 危险行为相关
            'dangerous': ['自杀', '自残', '毒品', '酗酒', '吸烟', '危险动作', '炸药', '爆炸'],
            # 隐私信息相关
            'privacy': ['身份证', '手机号', '地址', '密码', '银行卡', '账号', '身份证号'],
            # 仇恨言论相关
            'hate': ['歧视', '仇恨', '种族主义', '性别歧视', '宗教歧视', '骂人']
        }
    
    def _pre_filter_content(self, content: str) -> Dict[str, Any]:
        """
        第一层过滤：基于关键词的快速过滤
        """
        issues = []
        is_safe = True
        
        # 检查内容中是否包含敏感关键词
        for category, keywords in self.sensitive_keywords.items():
            for keyword in keywords:
                if keyword in content:  # 使用简单的包含检查而不是正则表达式
                    issues.append(f"检测到{category}相关敏感内容: {keyword}")
                    is_safe = False
        
        return {
            "is_safe": is_safe,
            "issues": issues
        }
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """
        快速内容安全验证（简化版）
        """
        # 先进行关键词预过滤
        pre_filter_result = self._pre_filter_content(content)
        if not pre_filter_result["is_safe"]:
            return {
                "is_safe": False,
                "reasons": pre_filter_result["issues"]
            }

        # 快速验证：如果没有明显问题，认为是安全的
        return {
            "is_safe": True,
            "reasons": []
        }

    def filter_content(self, content: str) -> Dict[str, Any]:
        """
        使用OpenAI智能过滤内容中的敏感信息（第二层过滤）
        """
        # 先进行关键词预过滤
        pre_filter_result = self._pre_filter_content(content)
        if not pre_filter_result["is_safe"]:
            return {
                "original_content": content,
                "is_safe": False,
                "issues": pre_filter_result["issues"],
                "filtered_content": "[内容包含敏感信息，已被过滤]"
            }

        # 构造提示词
        prompt = f"""
        你是一个专业的儿童内容安全审查员，请根据以下安全指导原则审查用户内容：

        {self.safety_guidelines}

        用户内容: "{content}"

        请分析该内容是否适合儿童，并按以下格式回复：
        安全状态: [安全/不安全]
        检测到的问题: [具体问题描述，如果安全则写"无"]
        过滤后内容: [如果内容不安全，提供修改建议；如果安全则写"保持原样"]
        """

        messages = [
            {"role": "system", "content": "你是一个专业的儿童内容安全安全审查员，严格按照要求格式回复。"},
            {"role": "user", "content": prompt}
        ]

        # 调用OpenAI API进行内容安全审查
        response = openai_client.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=300
        )

        # 解析响应
        lines = response.strip().split('\n')
        result = {
            "original_content": content,
            "is_safe": True,
            "issues": [],
            "filtered_content": content
        }

        for line in lines:
            if line.startswith("安全状态:"):
                result["is_safe"] = "不安全" not in line
            elif line.startswith("检测到的问题:"):
                issues = line.replace("检测到的问题:", "").strip()
                if issues != "无":
                    result["issues"] = [issues]
            elif line.startswith("过滤后内容:"):
                filtered = line.replace("过滤后内容:", "").strip()
                if filtered != "保持原样":
                    result["filtered_content"] = filtered

        return result
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理安全审查请求
        """
        content = request.get("content", "")
        filter_result = self.filter_content(content)
        
        return {
            "agent": "safety",
            "result": filter_result,
            "status": "processed"
        }