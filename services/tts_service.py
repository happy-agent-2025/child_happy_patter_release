import pyttsx3  # type: ignore
from io import BytesIO
from typing import Optional


class TTSService:
    """
    文本转语音服务
    """
    
    def __init__(self):
        self.engine = pyttsx3.init()
        # 设置语音参数
        self.engine.setProperty('rate', 150)    # 语速
        self.engine.setProperty('volume', 0.9)  # 音量
        
        # 获取可用的语音
        voices = self.engine.getProperty('voices')
        if voices:
            # 选择中文语音（如果可用）
            for voice in voices: # type: ignore
                if 'zh' in voice.id or 'chinese' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
    
    def synthesize_speech(self, text: str) -> BytesIO:
        """
        将文本转换为语音
        
        Args:
            text: 要转换的文本
            
        Returns:
            包含音频数据的字节流
        """
        # 创建一个内存缓冲区来存储音频数据
        audio_buffer = BytesIO()
        
        # 定义回调函数来捕获音频数据
        def save_audio_data(data):
            audio_buffer.write(data)
        
        # 合成语音并直接写入内存缓冲区
        self.engine.save_to_file(text, audio_buffer)
        self.engine.runAndWait()
        
        # 重置缓冲区指针到开始位置
        audio_buffer.seek(0)
        return audio_buffer
    
    def save_speech_to_file(self, text: str, filename: str):
        """
        将文本转换为语音并保存到文件
        
        Args:
            text: 要转换的文本
            filename: 输出文件名
        """
        self.engine.save_to_file(text, filename)
        self.engine.runAndWait()
    
    def set_voice_properties(self, rate: Optional[int] = None, 
                           volume: Optional[float] = None,
                           voice_id: Optional[str] = None):
        """
        设置语音属性
        
        Args:
            rate: 语速（每分钟字数）
            volume: 音量（0.0到1.0）
            voice_id: 语音ID
        """
        if rate is not None:
            self.engine.setProperty('rate', rate)
        
        if volume is not None:
            self.engine.setProperty('volume', volume)
            
        if voice_id is not None:
            self.engine.setProperty('voice', voice_id)
    
    def get_available_voices(self) -> list:
        """
        获取可用的语音列表
        
        Returns:
            语音信息列表
        """
        voices = self.engine.getProperty('voices')
        voice_list = []
        for voice in voices: # type: ignore
            voice_list.append({
                'id': voice.id,
                'name': voice.name,
                'languages': voice.languages,
                'gender': getattr(voice, 'gender', 'unknown')
            })
        return voice_list