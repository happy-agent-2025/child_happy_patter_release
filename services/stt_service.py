import speech_recognition as sr
from typing import BinaryIO, Optional
import numpy as np
from services.processing import AudioProcessingService


class STTService:
    """
    语音转文本服务
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.audio_processor = AudioProcessingService()
        # 设置识别器参数
        self.recognizer.energy_threshold = 400
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
    
    def transcribe_audio(self, audio_file: Optional[BinaryIO] = None) -> str:
        """
        将音频转换为文本
        
        Args:
            audio_file: 音频文件对象，如果为None则使用麦克风录音
            
        Returns:
            识别出的文本
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
                    # 调整环境噪声
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source, timeout=5)
            
            # 使用Google语音识别API转换文本
            text = self.recognizer.recognize_google(audio, language="zh-CN")
            return text
        except sr.UnknownValueError:
            return "无法理解音频内容"
        except sr.RequestError as e:
            return f"语音识别服务错误: {str(e)}"
        except Exception as e:
            return f"语音识别失败: {str(e)}"
    
    def transcribe_with_preprocessing(self, audio_file: BinaryIO) -> str:
        """
        带预处理的音频转文本
        
        Args:
            audio_file: 音频文件对象
            
        Returns:
            识别出的文本
        """
        try:
            # 先进行基本识别
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
            
            # 尝试识别
            text = self.recognizer.recognize_google(audio, language="zh-CN") # type: ignore
            return text
        except sr.UnknownValueError:
            return "无法理解音频内容"
        except sr.RequestError as e:
            return f"语音识别服务错误: {str(e)}"
        except Exception as e:
            return f"语音识别失败: {str(e)}"
    
    def get_audio_info(self, audio_file: BinaryIO) -> dict:
        """
        获取音频文件信息
        
        Args:
            audio_file: 音频文件对象
            
        Returns:
            音频信息字典
        """
        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                
            # 获取音频信息
            info = {
                "sample_rate": audio.sample_rate,
                "duration": len(audio.frame_data) / audio.sample_rate,
                "sample_width": audio.sample_width
            }
            return info
        except Exception as e:
            return {"error": f"获取音频信息失败: {str(e)}"}