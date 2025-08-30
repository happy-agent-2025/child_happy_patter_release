import speech_recognition as sr
from typing import BinaryIO, Optional, Any, Union
import numpy as np
from services.processing import AudioProcessingService
from services.codecs import AudioCodecService
import os
from datetime import datetime
import struct
import wave
from pathlib import Path

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

# 类型注释
AudioDataType = Any
RecognizerType = Any


class STTService:
    """
    语音转文本服务
    """
    
    def __init__(self):
        self.recognizer: RecognizerType = sr.Recognizer()
        self.audio_processor = AudioProcessingService()
        self.audio_codec = AudioCodecService()
        # 设置识别器参数
        self.recognizer.energy_threshold = 400
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
    
    def _handle_audio_input(self, audio_input: Union[BinaryIO, bytes], filename: str):
        """
        处理不同类型的音频输入数据并保存到文件
        
        Args:
            audio_input: 音频文件对象或字节数据
            filename: 保存的文件名
        """
        
        try:
            if isinstance(audio_input, bytes):
                # 处理字节数据
                with open(filename, "wb") as f:
                    f.write(audio_input)
            
            elif isinstance(audio_input, bytearray):
                # 处理bytearray数据
                with open(filename, "wb") as f:
                    f.write(bytes(audio_input))
            
            elif isinstance(audio_input, memoryview):
                # 处理memoryview数据
                with open(filename, "wb") as f:
                    f.write(audio_input.tobytes())
            
            elif str(type(audio_input)).find('BytesIO') != -1:
                # 处理BytesIO对象，先检查是否有seek和read方法
                seek_method = getattr(audio_input, 'seek', None)
                if seek_method and callable(seek_method):
                    audio_input.seek(0)
                
                read_method = getattr(audio_input, 'read', None)
                if read_method and callable(read_method):
                    with open(filename, "wb") as f:
                        f.write(audio_input.read())
                elif str(type(audio_input)).find('BytesIO') != -1:
                    getvalue_method = getattr(audio_input, 'getvalue', None)
                    if getvalue_method and callable(getvalue_method):
                        with open(filename, "wb") as f:
                            value = getvalue_method()
                            if isinstance(value, (bytes, bytearray)):
                                f.write(value)
                            else:
                                f.write(str(value).encode())
                    else:
                        # 最后尝试直接写入
                        with open(filename, "wb") as f:
                            f.write(str(audio_input).encode())
                else:
                    # 最后尝试直接写入
                    with open(filename, "wb") as f:
                        f.write(str(audio_input).encode())
            
            elif hasattr(audio_input, 'read') and callable(getattr(audio_input, 'read', None)):
                # 处理文件对象
                seek_method = getattr(audio_input, 'seek', None)
                if seek_method and callable(seek_method):
                    audio_input.seek(0)
                
                # 分块读取，避免内存问题
                chunk_size = 1024 * 1024  # 1MB per chunk
                with open(filename, "wb") as f:
                    while True:
                        chunk = audio_input.read(chunk_size)
                        if not chunk:
                            break
                        # 确保chunk是bytes类型
                        if isinstance(chunk, (bytes, bytearray)):
                            f.write(bytes(chunk))
                        elif isinstance(chunk, memoryview):
                            f.write(chunk.tobytes())
                        else:
                            f.write(str(chunk).encode())
            
            else:
                # 尝试使用通用方法处理
                read_method = getattr(audio_input, 'read', None)
                if read_method and callable(read_method):
                    # 分块读取
                    chunk_size = 1024 * 1024
                    with open(filename, "wb") as f:
                        while True:
                            chunk = read_method(chunk_size)
                            if not chunk:
                                break
                            # 确保chunk是bytes类型
                            if isinstance(chunk, (bytes, bytearray)):
                                f.write(bytes(chunk))
                            elif isinstance(chunk, memoryview):
                                f.write(chunk.tobytes())
                            else:
                                f.write(str(chunk).encode())
                else:
                    # 直接写入数据，确保是bytes类型
                    with open(filename, "wb") as f:
                        if isinstance(audio_input, (bytes, bytearray)):
                            f.write(bytes(audio_input))
                        elif isinstance(audio_input, memoryview):
                            f.write(audio_input.tobytes())
                        else:
                            f.write(str(audio_input).encode())
        
        except Exception as e:
            print(f"处理音频输入时发生错误: {str(e)}")
            # 清理可能损坏的文件
            if os.path.exists(filename):
                os.remove(filename)
            raise
    
    def _convert_audio_format(self, input_filename: str, output_filename: str) -> bool:
        """
        尝试将音频文件转换为WAV格式
        
        Args:
            input_filename: 输入文件名
            output_filename: 输出文件名
            
        Returns:
            转换是否成功
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_filename)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            import ffmpeg
            # 正确的调用顺序
            (
                ffmpeg
                .input(input_filename)
                .output(
                    output_filename, 
                    acodec='pcm_s16le', 
                    ar=16000, 
                    ac=1
                )
                .overwrite_output()  # 这个应该在output之后
                .run(quiet=True)
            )
            print(f"转换音频成功: {input_filename} -> {output_filename}")
            
            # 验证文件是否真的创建了
            if os.path.exists(output_filename):
                file_size = os.path.getsize(output_filename)
                print(f"文件已保存: {output_filename} (大小: {file_size} 字节)")
                return True
            else:
                print("错误: 文件未创建")
                return False
                
        except ffmpeg.Error as e: # type: ignore
            print(f"FFmpeg错误: {e.stderr.decode() if hasattr(e, 'stderr') else str(e)}")
            return False
        except Exception as e:
            print(f"其他错误: {e}")
            return False
    
    # 谷歌在线音频检测，不适用这个
    def _debug_speech_recognition_internals(self, converted_filename: str) -> str:
        """深入调试speech_recognition库的内部问题"""
        try:
            absolute_path = os.path.abspath(converted_filename).replace('\\', '/')
            print(f"绝对路径: {absolute_path}")
            
            # 手动检查speech_recognition的AudioFile初始化过程
            recognizer = sr.Recognizer()
            
            # 尝试直接查看AudioFile的初始化代码
            try:
                # 手动模拟AudioFile的初始化过程
                with open(absolute_path, 'rb') as audio_file:
                    # 检查文件是否可读
                    data = audio_file.read(100)
                    print(f"文件头数据: {data[:20]}")
                    
                    # 重新打开文件用于AudioFile
                    audio_file.seek(0)
                    
                    # 这里是最可能出错的地方
                    audio_source = sr.AudioFile(audio_file)
                    print("AudioFile对象创建成功")
                    
                    with audio_source as source:
                        print("音频源上下文管理器进入成功")
                        audio = recognizer.record(source)
                        print("音频录制成功")
                        
                        try:
                            text = recognizer.recognize_google(audio, language='zh-CN') # type: ignore
                            print(f"识别成功: {text}")
                            return text
                        except sr.UnknownValueError:
                            print("无法识别内容")
                            return "无法识别"
                            
            except Exception as e:
                print(f"AudioFile初始化详细错误: {e}")
                import traceback
                traceback.print_exc()
                return "无法识别内容"
                
        except Exception as e:
            print(f"总体错误: {e}")
            return "无法识别内容"
        
    def transcribe_audio(self, audio_file: Optional[Union[BinaryIO, bytes]] = None, 
                         preprocess: bool = True) -> str:
        """
        将音频转换为文本
        
        Args:
            audio_file: 音频文件对象或字节数据
            
        Returns:
            识别出的文本
        """
        # 创建音频文件目录（如果不存在）
        audio_dir = "audio_files"
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)
        
        # 生成基于时间戳的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 直接使用.wav扩展名，确保speech_recognition能正确识别
        audio_filename = os.path.join(audio_dir, f"audio_{timestamp}")
        
        # 将audio_file写入指定文件
        if audio_file is not None:
            self._handle_audio_input(audio_file, audio_filename)
            print(f"音频文件已保存到: {audio_filename}")
            
        print("检测到WebM/Opus格式音频，尝试转换为WAV")
        converted_filename = os.path.join(audio_dir, f"converted_{timestamp}.wav")
        if self._convert_audio_format(audio_filename, converted_filename):
            print("WebM/Opus转换为WAV成功")
            
            absolute_path = os.path.abspath(converted_filename).replace('\\', '/')
            print(f"绝对路径: {absolute_path}")
            print(f"文件存在: {os.path.exists(absolute_path)}")
            
            text = self._debug_speech_recognition_internals(converted_filename)
            
            return text
        
        return "无法处理识别音频"
        
    def transcribe_with_preprocessing(self, audio_file: Union[BinaryIO, bytes]) -> str:
        """
        带预处理的音频转文本
        
        Args:
            audio_file: 音频文件对象或字节数据
            
        Returns:
            识别出的文本
        """
        # 直接调用transcribe_audio方法并启用预处理
        return self.transcribe_audio(audio_file, preprocess=True)
    
    def get_audio_info(self, audio_file: Union[BinaryIO, bytes]) -> dict:
        """
        获取音频文件信息
        
        Args:
            audio_file: 音频文件对象或字节数据
            
        Returns:
            音频信息字典
        """
        try:
            # 创建临时文件来处理音频数据
            audio_dir = "audio_files"
            if not os.path.exists(audio_dir):
                os.makedirs(audio_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 使用.wav扩展名确保正确识别
            wav_filename = os.path.join(audio_dir, f"temp_audio_{timestamp}.wav")
            
            # 处理音频输入并保存到临时文件
            self._handle_audio_input(audio_file, wav_filename)
            
            audio = None
            # 尝试加载音频文件
            try:
                with sr.AudioFile(wav_filename) as source:
                    audio = self.recognizer.record(source)
                print("直接加载音频文件成功")
            except Exception as e:
                print(f"直接加载音频文件失败: {str(e)}")
                
                # 尝试使用内部解码器
                try:
                    print("尝试使用内部解码器处理音频")
                    # 读取音频数据
                    with open(wav_filename, "rb") as f:
                        audio_data = f.read()
                    
                    # 尝试解码音频
                    decoded_audio = self.audio_codec.decode_audio(audio_data)
                    if decoded_audio and len(decoded_audio) > 0:
                        # 保存解码后的音频到新的文件
                        decoded_filename = os.path.join(audio_dir, f"decoded_info_{timestamp}.wav")
                        with open(decoded_filename, "wb") as f:
                            f.write(decoded_audio)
                        with sr.AudioFile(decoded_filename) as source:
                            audio = self.recognizer.record(source)
                        print("使用内部解码器解码音频成功")
                        
                        # 清理解码后的文件
                        if os.path.exists(decoded_filename):
                            os.remove(decoded_filename)
                    else:
                        print("内部解码器无法解码音频")
                        raise e  # 重新抛出原始异常
                except Exception as decode_error:
                    print(f"内部解码器处理失败: {str(decode_error)}")
                    raise e  # 重新抛出原始异常
            
            if audio is None:
                raise Exception("无法加载音频文件")
            
            # 获取音频信息
            info = {
                "sample_rate": audio.sample_rate,
                "duration": len(audio.frame_data) / audio.sample_rate,
                "sample_width": audio.sample_width
            }
            
            # 删除临时文件
            try:
                if os.path.exists(wav_filename):
                    os.remove(wav_filename)
            except Exception as cleanup_error:
                print(f"清理临时文件时出错: {str(cleanup_error)}")
                
            return info
        except Exception as e:
            return {"error": f"获取音频信息失败: {str(e)}"}
