import pyttsx3 # type: ignore
from io import BytesIO


class TTSService:
    """
    文本转语音服务
    """
    
    def __init__(self):
        self.engine = pyttsx3.init()
        # 设置语音参数
        self.engine.setProperty('rate', 150)   # 语速
        self.engine.setProperty('volume', 0.9) # 音量
    
    def synthesize_speech(self, text: str) -> BytesIO:
        """
        将文本转换为语音
        """
        # 创建字节流存储音频数据
        audio_buffer = BytesIO()
        
        # 合成语音（实际项目中可能需要保存为文件或直接播放）
        self.engine.say(text)
        self.engine.runAndWait()
        
        # 注意：pyttsx3不直接支持输出到BytesIO，实际使用中可能需要其他库
        # 这里仅作为占位符
        return audio_buffer
    
    def save_speech_to_file(self, text: str, filename: str):
        """
        将文本转换为语音并保存到文件
        """
        self.engine.save_to_file(text, filename)
        self.engine.runAndWait()