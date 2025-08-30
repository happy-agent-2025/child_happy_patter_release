import pyttsx3  # type: ignore
from io import BytesIO
from typing import Optional
import tempfile
import os


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
        # 创建临时文件来存储音频数据
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            # 使用save_to_file将音频保存到临时文件
            self.engine.save_to_file(text, temp_filename)
            self.engine.runAndWait()
            
            # 从临时文件读取音频数据到内存缓冲区
            with open(temp_filename, 'rb') as f:
                audio_data = f.read()
            
            # 创建BytesIO对象并写入音频数据
            audio_buffer = BytesIO(audio_data)
            audio_buffer.seek(0)
            return audio_buffer
        finally:
            # 清理临时文件
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
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