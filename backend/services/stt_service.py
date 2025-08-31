import speech_recognition as sr
from typing import BinaryIO, Optional, Any, Union
import numpy as np
from io import BytesIO
import wave
import tempfile
import os
from datetime import datetime
import struct

# 获取speech_recognition中的异常类
try:
    UnknownValueError = sr.UnknownValueError
except AttributeError:
    UnknownValueError = Exception

try:
    RequestError = sr.RequestError
except AttributeError:
    RequestError = Exception

# 类型注释
AudioDataType = Any
RecognizerType = Any


class STTService:
    """
    语音转文本服务（完全内存操作）
    """
    
    def __init__(self):
        self.recognizer: RecognizerType = sr.Recognizer()
        # 设置识别器参数
        self.recognizer.energy_threshold = 400
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
    
    def _convert_to_wav_in_memory(self, audio_data: bytes) -> BytesIO:
        """
        将音频数据转换为WAV格式（内存操作）
        
        Args:
            audio_data: 原始音频数据
            
        Returns:
            WAV格式的BytesIO对象
        """
        try:
            # 首先尝试直接读取音频数据
            try:
                # 使用pydub进行格式转换（如果可用）
                try:
                    from pydub import AudioSegment
                    
                    # 从字节数据创建音频段
                    audio = AudioSegment.from_file(BytesIO(audio_data))
                    # 转换为WAV格式：16kHz, 16bit, 单声道
                    audio = audio.set_frame_rate(16000).set_sample_width(2).set_channels(1)
                    
                    # 导出到内存
                    wav_buffer = BytesIO()
                    audio.export(wav_buffer, format="wav")
                    wav_buffer.seek(0)
                    
                    return wav_buffer
                    
                except ImportError:
                    # pydub不可用，使用FFmpeg
                    pass
                
            except:
                # pydub处理失败，使用FFmpeg
                pass
            
            # 使用FFmpeg进行内存转换
            try:
                import ffmpeg
                
                # 使用FFmpeg管道进行内存转换
                process = (
                    ffmpeg
                    .input('pipe:0')
                    .output(
                        'pipe:1',
                        format='wav',
                        acodec='pcm_s16le',
                        ar=16000,
                        ac=1
                    )
                    .overwrite_output()
                    .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True, quiet=True)
                )
                
                # 写入输入数据
                process.stdin.write(audio_data)
                process.stdin.close()
                
                # 读取输出数据
                wav_data = process.stdout.read()
                process.wait()
                
                if process.returncode == 0:
                    return BytesIO(wav_data)
                else:
                    raise Exception("FFmpeg转换失败")
                    
            except ImportError:
                # FFmpeg不可用，尝试其他方法
                pass
            
            # 最后尝试：如果数据已经是WAV格式，直接返回
            try:
                # 检查是否是WAV文件
                with wave.open(BytesIO(audio_data)) as wav_file:
                    # 如果是WAV，检查格式是否符合要求
                    if (wav_file.getframerate() == 16000 and 
                        wav_file.getnchannels() == 1 and 
                        wav_file.getsampwidth() == 2):
                        return BytesIO(audio_data)
            except:
                pass
            
            # 如果所有方法都失败，抛出异常
            raise Exception("无法转换音频格式")
            
        except Exception as e:
            print(f"音频转换失败: {e}")
            raise
    
    def _bytes_to_audio_data(self, audio_buffer: BytesIO) -> sr.AudioData:
        """
        将字节数据转换为speech_recognition的AudioData对象
        
        Args:
            audio_buffer: 包含WAV音频数据的BytesIO对象
            
        Returns:
            speech_recognition的AudioData对象
        """
        try:
            # 读取WAV文件信息
            with wave.open(audio_buffer) as wav_file:
                frame_rate = wav_file.getframerate()
                frames = wav_file.readframes(wav_file.getnframes())
                sample_width = wav_file.getsampwidth()
            
            # 创建AudioData对象
            audio_data = sr.AudioData(frames, frame_rate, sample_width)
            return audio_data
            
        except Exception as e:
            print(f"创建AudioData失败: {e}")
            raise
    
    def _recognize_from_memory(self, audio_data: sr.AudioData) -> str:
        """
        从内存中的音频数据进行识别
        
        Args:
            audio_data: speech_recognition的AudioData对象
            
        Returns:
            识别出的文本
        """
        try:
            # 使用Google语音识别
            text = self.recognizer.recognize_google(audio_data, language='zh-CN')
            return text
            
        except UnknownValueError:
            return "无法识别音频内容"
        except RequestError as e:
            print(f"语音识别服务错误: {e}")
            return "语音识别服务不可用"
        except Exception as e:
            print(f"语音识别失败: {e}")
            return "语音识别失败"
    
    def transcribe_audio(self, audio_input: Union[BinaryIO, bytes, bytearray],
                         preprocess: bool = True) -> str:
        """
        将音频转换为文本（完全内存操作）
        
        Args:
            audio_input: 音频文件对象、字节数据或bytearray
            
        Returns:
            识别出的文本
        """
        try:
            # 1. 统一转换为字节数据
            if isinstance(audio_input, (BytesIO, BinaryIO)):
                audio_input.seek(0)
                audio_data = audio_input.read()
            elif isinstance(audio_input, (bytes, bytearray)):
                audio_data = bytes(audio_input)
            else:
                raise ValueError("不支持的音频输入类型")
            
            if not audio_data:
                return "音频数据为空"
            
            print(f"接收到音频数据: {len(audio_data)} 字节")
            
            # 2. 转换为标准WAV格式（内存中）
            wav_buffer = self._convert_to_wav_in_memory(audio_data)
            print(f"转换为WAV格式成功: {wav_buffer.getbuffer().nbytes} 字节")
            
            # 3. 创建AudioData对象
            audio_data_obj = self._bytes_to_audio_data(wav_buffer)
            
            # 4. 进行语音识别
            text = self._recognize_from_memory(audio_data_obj)
            
            return text
            
        except Exception as e:
            print(f"音频转文本失败: {e}")
            return f"处理失败: {str(e)}"
    
    def transcribe_with_fallback(self, audio_input: Union[BinaryIO, bytes, bytearray],
                         preprocess: bool = True) -> str:
        """
        带降级处理的音频转文本（如果内存操作失败，使用文件回退）
        
        Args:
            audio_input: 音频文件对象、字节数据或bytearray
            
        Returns:
            识别出的文本
        """
        try:
            # 首先尝试内存操作
            return self.transcribe_audio(audio_input)
            
        except Exception as e:
            print(f"内存操作失败，尝试文件回退: {e}")
            
            # 使用文件回退方案
            temp_filename = None
            try:
                # 创建临时文件
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    temp_filename = temp_file.name
                
                # 将数据写入临时文件
                if isinstance(audio_input, (BytesIO, BinaryIO)):
                    audio_input.seek(0)
                    with open(temp_filename, 'wb') as f:
                        f.write(audio_input.read())
                elif isinstance(audio_input, (bytes, bytearray)):
                    with open(temp_filename, 'wb') as f:
                        f.write(audio_input)
                
                # 使用文件进行识别
                with sr.AudioFile(temp_filename) as source:
                    audio = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio, language='zh-CN')
                
                return text
                
            except Exception as fallback_error:
                print(f"文件回退也失败: {fallback_error}")
                return "无法处理音频"
            finally:
                # 清理临时文件
                if temp_filename is not None and os.path.exists(temp_filename):
                    os.remove(temp_filename)
    
    def get_audio_info(self, audio_input: Union[BinaryIO, bytes, bytearray]) -> dict:
        """
        获取音频文件信息（内存操作）
        
        Args:
            audio_input: 音频文件对象、字节数据或bytearray
            
        Returns:
            音频信息字典
        """
        try:
            # 统一转换为字节数据
            if isinstance(audio_input, (BytesIO, BinaryIO)):
                audio_input.seek(0)
                audio_data = audio_input.read()
            elif isinstance(audio_input, (bytes, bytearray)):
                audio_data = bytes(audio_input)
            else:
                return {"error": "不支持的音频输入类型"}
            
            info = {
                "size_bytes": len(audio_data),
                "format": "unknown"
            }
            
            # 尝试检测格式
            try:
                import magic
                file_type = magic.from_buffer(audio_data[:1024])
                info["format"] = file_type
            except ImportError:
                info["format"] = "需要安装python-magic来检测格式"
            
            # 如果是WAV格式，获取详细信息
            try:
                with wave.open(BytesIO(audio_data)) as wav_file:
                    info.update({
                        "sample_rate": wav_file.getframerate(),
                        "channels": wav_file.getnchannels(),
                        "sample_width": wav_file.getsampwidth(),
                        "frames": wav_file.getnframes(),
                        "duration_seconds": wav_file.getnframes() / wav_file.getframerate() if wav_file.getframerate() > 0 else 0
                    })
            except:
                pass
            
            return info
            
        except Exception as e:
            return {"error": f"获取音频信息失败: {str(e)}"}


# 使用示例
def example_usage():
    """使用示例"""
    stt_service = STTService()
    
    # 示例1: 从文件读取并转换
    with open("D:\\rag\\happy_partter\\happy_partner\\backend\\audio_files\\converted_20250831_164202.wav", "rb") as f:
        audio_data = f.read()
        text = stt_service.transcribe_audio(audio_data)
        print(f"识别结果: {text}")
    
    # 示例2: 使用BytesIO
    with open("D:\\rag\\happy_partter\\happy_partner\\backend\\audio_files\\converted_20250831_164202.wav", "rb") as f:
        audio_buffer = BytesIO(f.read())
        text = stt_service.transcribe_audio(audio_buffer)
        print(f"识别结果: {text}")
    
    # 示例3: 获取音频信息
    with open("D:\\rag\\happy_partter\\happy_partner\\backend\\audio_files\\converted_20250831_164202.wav", "rb") as f:
        audio_data = f.read()
        info = stt_service.get_audio_info(audio_data)
        print(f"音频信息: {info}")


if __name__ == "__main__":
    example_usage()