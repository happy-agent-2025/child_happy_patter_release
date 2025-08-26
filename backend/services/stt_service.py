import speech_recognition as sr
from typing import BinaryIO, Optional
import numpy as np
from services.processing import AudioProcessingService
from services.codecs import AudioCodecService

# 获取speech_recognition中的异常类
try:
    UnknownValueError = sr.UnknownValueError
except AttributeError:
    # 如果找不到UnknownValueError，使用通用异常
    UnknownValueError = Exception

try:
    RequestError = sr.RequestError
except AttributeError:
    # 如果找不到RequestError，使用通用异常
    RequestError = Exception


class STTService:
    """
    语音转文本服务
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.audio_processor = AudioProcessingService()
        self.audio_codec = AudioCodecService()
        # 设置识别器参数
        self.recognizer.energy_threshold = 400
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
    
    def transcribe_audio(self, audio_file: Optional[BinaryIO] = None, 
                         preprocess: bool = True) -> str:
        """
        将音频转换为文本
        
        Args:
            audio_file: 音频文件对象，如果为None则使用麦克风录音
            preprocess: 是否对音频进行预处理以提高识别准确率
            
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
            
            # 如果需要预处理且提供了音频文件，则进行预处理
            if preprocess and audio_file:
                # 获取音频数据并进行预处理
                audio_data = np.frombuffer(audio.frame_data, dtype=np.int16)
                processed_audio = self.audio_processor.preprocess_audio(
                    audio_data.astype(np.float32) / 32768.0, 
                    audio.sample_rate
                )
                
                # 将处理后的音频数据编码为WAV格式
                processed_wav = self.audio_codec.encode_wav(processed_audio, audio.sample_rate)
                
                # 重新加载处理后的音频
                with sr.AudioFile(sr.AudioData(processed_wav, audio.sample_rate, audio.sample_width).get_wav_data()) as source:
                    audio = self.recognizer.record(source)
            
            # 使用Google语音识别API转换文本
            text = self.recognizer.recognize_google(audio, language="zh-CN")
            return text
        except UnknownValueError:
            return "无法理解音频内容"
        except RequestError as e:
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
        # 直接调用transcribe_audio方法并启用预处理
        return self.transcribe_audio(audio_file, preprocess=True)
    
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