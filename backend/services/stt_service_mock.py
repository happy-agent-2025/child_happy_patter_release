"""
模拟STT服务 - 用于绕过音频依赖问题
"""

class STTServiceMock:
    """模拟的语音转文本服务"""

    def __init__(self):
        self.enabled = True

    def transcribe_audio(self, audio_data: bytes, preprocess: bool = True) -> str:
        """
        模拟音频转录功能

        Args:
            audio_data: 音频数据
            preprocess: 是否预处理

        Returns:
            转录的文本
        """
        # 模拟转录结果
        mock_responses = [
            "你好，我想了解一下人工智能。",
            "什么是机器学习？",
            "请解释一下深度学习。",
            "今天天气怎么样？",
            "你能帮我学习数学吗？",
            "我想知道关于Python编程的知识。",
            "请讲一个故事。",
            "什么是神经网络？"
        ]

        import random
        return random.choice(mock_responses)

    def is_enabled(self) -> bool:
        """检查服务是否启用"""
        return self.enabled


# 为了保持兼容性，创建一个STTService别名
STTService = STTServiceMock