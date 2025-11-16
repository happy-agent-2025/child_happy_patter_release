from typing import Dict, Any
from core.openai_client import openai_client
from core.ollama_client import ollama_client
from config.settings import settings


class EduAgent:
    """
    教育代理，负责教育内容问答
    """

    def __init__(self):
        # 定义教育场景的系统提示
        self.system_prompt = """
        你是一个专门为儿童设计的教育AI助手，你的职责是：
        1. 用简单易懂的语言回答问题
        2. 耐心、友好地与孩子交流
        3. 根据孩子的年龄调整回答的复杂程度
        4. 鼓励孩子思考和探索
        5. 在回答中加入趣味性元素
        6. 确保内容准确、科学
        7. 避免使用复杂术语，必要时进行解释
        """

        # 定义学科领域
        self.subjects = [
            "语文",
            "数学",
            "英语",
            "科学",
            "历史",
            "地理",
            "艺术",
            "音乐",
            "体育",
            "道德与法治",
            "信息技术",
        ]

        # 定义年龄段特点和适配策略
        self.age_groups = {
            "5-6岁": {
                "description": "学龄前儿童",
                "roleistics": "好奇心强，注意力短暂，喜欢游戏化学习",
                "approach": "使用大量图片、故事和游戏化元素，语言简单生动",
            },
            "7-8岁": {
                "description": "小学低年级",
                "roleistics": "开始系统学习，理解能力增强，喜欢动手实践",
                "approach": "结合具体例子和简单实验，增加互动性",
            },
            "9-10岁": {
                "description": "小学中年级",
                "roleistics": "逻辑思维发展，知识面扩大，有一定自主学习能力",
                "approach": "引入简单逻辑推理，提供更多背景知识",
            },
            "11-12岁": {
                "description": "小学高年级",
                "roleistics": "抽象思维发展，批判性思维萌芽，学习能力较强",
                "approach": "鼓励独立思考，引导探索更深层的知识",
            },
        }

    def _get_subject_context(self, question: str) -> str:
        """
        使用大模型分析问题涉及的学科领域
        """
        # 构造提示词
        prompt = f"""
        请分析以下问题最适合归类到哪个学科领域：
        
        问题: "{question}"
        
        可选的学科包括：{', '.join(self.subjects)}
        
        请直接回答最相关的学科名称，如果不确定，请回答"通用"。
        """

        messages = [
            {
                "role": "system",
                "content": "你是一个教育领域的专家，能够准确判断问题所属的学科。",
            },
            {"role": "user", "content": prompt},
        ]

        # 根据配置选择使用OpenAI还是Ollama
        try:
            if settings.use_ollama:
                response = ollama_client.chat_completion(
                    messages=messages, temperature=0.1, max_tokens=10
                )
            else:
                response = openai_client.chat_completion(
                    messages=messages, temperature=0.1, max_tokens=10
                )
            subject = response.strip()
            # 验证返回的学科是否在我们的学科列表中
            if subject in self.subjects:
                return subject
            else:
                # 如果返回的学科不在列表中，回退到关键词匹配
                return self._fallback_subject_detection(question)
        except Exception as e:
            # 如果API调用失败，回退到关键词匹配
            return self._fallback_subject_detection(question)

    def _fallback_subject_detection(self, question: str) -> str:
        """
        当大模型分析失败时的回退方案 - 基于关键词的简单匹配
        """
        question_lower = question.lower()

        # 简单的关键词匹配来判断学科
        if any(
            keyword in question_lower
            for keyword in [
                "加",
                "减",
                "乘",
                "除",
                "数",
                "几何",
                "算",
                "平行四边形",
                "1+1",
            ]
        ):
            return "数学"
        elif any(
            keyword in question_lower
            for keyword in ["读", "写", "诗", "词", "句", "文章", "李白"]
        ):
            return "语文"
        elif any(
            keyword in question_lower for keyword in ["英语", "英文", "单词", "字母"]
        ):
            return "英语"
        elif any(
            keyword in question_lower
            for keyword in ["植物", "动物", "实验", "科学", "物理", "化学", "光合作用"]
        ):
            return "科学"
        elif any(
            keyword in question_lower
            for keyword in ["历史", "古代", "皇帝", "朝代", "长城"]
        ):
            return "历史"
        elif any(
            keyword in question_lower
            for keyword in ["地理", "国家", "城市", "气候", "地图", "首都"]
        ):
            return "地理"
        elif any(
            keyword in question_lower for keyword in ["音乐", "歌曲", "乐器", "钢琴"]
        ):
            return "音乐"
        elif any(
            keyword in question_lower for keyword in ["画", "颜色", "艺术", "梵高"]
        ):
            return "艺术"
        elif any(
            keyword in question_lower for keyword in ["运动", "体育", "健康", "游泳"]
        ):
            return "体育"
        elif any(
            keyword in question_lower
            for keyword in ["道德", "法律", "规则", "社会", "交通规则"]
        ):
            return "道德与法治"
        elif any(
            keyword in question_lower for keyword in ["人工智能", "信息技术", "电脑"]
        ):
            return "信息技术"
        else:
            return "通用"

    def answer_question(self, question: str, user_info: Dict[str, Any]) -> str:
        """
        使用OpenAI智能回答教育相关问题
        """
        if user_info is None:
            user_info = {}

        user_age = user_info.get("age", "7-8岁")
        user_grade = user_info.get("grade", "小学低年级")

        # 获取问题涉及的学科
        subject = self._get_subject_context(question)

        # 获取年龄段特点
        age_group_info = self.age_groups.get(user_age, self.age_groups["7-8岁"])

        # 构造提示词
        prompt = f"""
        用户是一个{user_age}的孩子{age_group_info["description"]}，正在{user_grade}学习。
        他提出了一个问题: "{question}"
        
        该问题可能涉及的学科领域: {subject}
        该年龄段特点: {age_group_info["roleistics"]}
        推荐教学方式: {age_group_info["approach"]}
        
        请根据以下要求回答：
        1. 使用适合该年龄段的语言和例子
        2. 回答要准确、科学
        3. 可以适当增加趣味性
        4. 鼓励孩子继续探索和学习
        5. 如果问题不清晰，可以询问更多细节
        6. 结合推荐的教学方式进行回答
        """

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]

        # 根据配置选择使用OpenAI还是Ollama
        if settings.use_ollama:
            response = ollama_client.chat_completion(
                messages=messages, temperature=0.7, max_tokens=500
            )
        else:
            response = openai_client.chat_completion(
                messages=messages, temperature=0.7, max_tokens=500
            )

        return response

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理教育问答请求
        """
        question = request.get("content", "")
        user_info = {
            "user_id": request.get("user_id", "unknown_user"),
            "age": request.get("age", "7-8岁"),
            "grade": request.get("grade", "小学低年级"),
            "grade_level": request.get("grade_level", "小学低年级"),
        }

        # 如果提供了grade_level，根据它来确定age
        grade_level = request.get("grade_level", "")
        if grade_level:
            if "学前" in grade_level or "幼" in grade_level:
                user_info["age"] = "5-6岁"
            elif "一" in grade_level or "二" in grade_level:
                user_info["age"] = "7-8岁"
            elif "三" in grade_level or "四" in grade_level:
                user_info["age"] = "9-10岁"
            elif "五" in grade_level or "六" in grade_level:
                user_info["age"] = "11-12岁"

        answer = self.answer_question(question, user_info)

        return {
            "agent": "edu",
            "question": question,
            "answer": answer,
            "subject": self._get_subject_context(question),
            "status": "processed",
        }
