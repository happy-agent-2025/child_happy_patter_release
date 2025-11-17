from abc import ABC, abstractmethod
import re
from utils.audio_format.opus import Opus_Encode


class TTS(ABC):
    
    def audio_file_to_opus(self, audio_file_path):
        """将语音文件转为opus数据"""
        opus = Opus_Encode()
        opus_data, duration = opus.audio_to_opus(audio_file_path)
        return opus_data, duration
    
    @abstractmethod
    def text_to_opus_data(self, text):
        """将文本转为opus数据"""
        raise NotImplementedError()
    
    
    # 清理文本，正则表达式清除不需要的符号 
    def clean_text_for_tts(self, text):
        if not isinstance(text, str):
            return str(text) if text is not None else ""
        # 处理Markdown链接 [描述](URL) → 保留描述
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

        # 移除URL链接
        text = re.sub(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            "链接",
            text
        )
        # 移除Markdown格式
        text = re.sub(r'[*_`~#]', '', text)  # 移除基本Markdown标记
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # 移除链接但保留描述文本
        # 移除特殊字符但保留标点
        text = re.sub(r'[^\w\s，。！？；：\'\-%.]', '', text)
        # 移除多余的空格和换行
        text = ' '.join(text.split())
        return text