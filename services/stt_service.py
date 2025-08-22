import speech_recognition as sr
from typing import BinaryIO, Optional


class STTService:
    """
    语音转文本服务
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def transcribe_audio(self, audio_file: Optional[BinaryIO] = None) -> str:
        """
        将音频转换为文本
        """
        try:
            if audio_file:
                # 处理上传的音频文件
                with sr.AudioFile(audio_file) as source:
                    audio = self.recognizer.record(source)
            else:
                # 使用麦克风录音
                with sr.Microphone() as source:
                    print("请说话...")
                    audio = self.recognizer.listen(source)
            
            # 使用Google语音识别API转换文本
            # 使用类型注释解决Pylance报错
            text = self.recognizer.recognize_google(audio, language="zh-CN")  # type: ignore
            return text
        except Exception as e:
            return f"语音识别失败: {str(e)}"