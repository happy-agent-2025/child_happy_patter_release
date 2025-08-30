import speech_recognition as sr
from typing import BinaryIO, Optional, Any, Union
import numpy as np
from services.processing import AudioProcessingService
from services.codecs import AudioCodecService
import os
from datetime import datetime
from io import BytesIO
import tempfile
import struct
import wave
import struct

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
            
            # 验证是否为有效的音频文件
            try:
                # 如果是WebM/Opus格式，直接返回成功
                if self._is_webm_opus_format(filename):
                    return
                
                # 否则检查是否为有效的WAV文件
                with sr.AudioFile(filename) as test_audio:
                    with open(filename, "rb") as f:
                        f.read()  # 再次验证文件可读性
            except Exception as e:
                raise ValueError(f"保存的文件不是有效的音频文件: {str(e)}")
        
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
            # 首先尝试使用soundfile直接转换（支持更多格式）
            try:
                import soundfile as sf
                import numpy as np
                # 读取音频文件
                audio_data, sample_rate = sf.read(input_filename)
                # 写入WAV格式
                sf.write(output_filename, audio_data, sample_rate, format='WAV')
                print(f"使用soundfile转换音频成功: {input_filename} -> {output_filename}")
                return True
            except Exception as e:
                print(f"使用soundfile转换音频失败: {str(e)}")
            
            # 尝试使用pydub进行转换（如果可用）
            try:
                import pydub
                # 加载音频文件（pydub会自动识别格式）
                print("Using pydub for audio conversion",input_filename)
                audio = pydub.AudioSegment.from_file(input_filename)
                # 导出为WAV格式
                audio.export(output_filename, format="wav")
                return True
            except ImportError:
                print("pydub库未安装，无法自动转换音频格式")
            except Exception as e:
                print(f"使用pydub转换音频失败: {str(e)}")
            
            # 如果pydub不可用或转换失败，尝试使用python-ffmpeg进行转换
            try:
                import ffmpeg
                # 使用python-ffmpeg进行音频转换
                (
                    ffmpeg
                    .input(input_filename) # type: ignore
                    .output(output_filename, acodec='pcm_s16le', ar=16000, ac=1)
                    .overwrite_output()
                    .run(quiet=True, capture_stdout=True, capture_stderr=True)
                )
                print(f"使用python-ffmpeg转换音频成功: {input_filename} -> {output_filename}")
                return True
            except ImportError:
                print("python-ffmpeg库未安装，尝试使用系统ffmpeg")
            except Exception as e:
                print(f"使用python-ffmpeg转换音频失败: {str(e)}")
                
            # 如果python-ffmpeg不可用或失败，尝试使用系统ffmpeg
            try:
                import subprocess
                import os
                # 检查ffmpeg是否可用
                try:
                    subprocess.run(['ffmpeg', '-version'], 
                                 capture_output=True, check=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    print("未找到FFmpeg，无法转换音频格式")
                    return False
                
                # 尝试使用ffmpeg转换
                result = subprocess.run([
                    'ffmpeg', '-i', input_filename, 
                    '-acodec', 'pcm_s16le', 
                    '-ar', '16000', 
                    '-ac', '1', 
                    output_filename
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print(f"使用系统FFmpeg转换音频成功: {input_filename} -> {output_filename}")
                    return True
                else:
                    print(f"系统FFmpeg转换失败: {result.stderr}")
            except FileNotFoundError:
                print("未找到系统FFmpeg，无法转换音频格式")
            except Exception as e:
                print(f"使用系统FFmpeg转换音频失败: {str(e)}")
            
            # 如果所有转换方法都失败，返回False
            return False
        except Exception as e:
            print(f"音频转换失败: {str(e)}")
            return False

    def _is_webm_opus_format(self, file_path: str) -> bool:
        """
        检查文件是否为WebM/Opus格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否为WebM/Opus格式
        """
        try:
            with open(file_path, 'rb') as f:
                # 读取文件头
                header = f.read(8)
                if len(header) < 8:
                    return False
                
                # WebM文件头检查（EBML格式）
                # WebM文件通常以\x1A\x45\xDF\xA3开头
                if header[:4] == b'\x1A\x45\xDF\xA3':
                    return True
                
                # 检查Opus标识
                if header[:8] == b'OggS\x00\x02\x00\x00\x00':
                    # 进一步检查Opus标识
                    f.seek(28)
                    opus_header = f.read(8)
                    if opus_header == b'OpusHead':
                        return True
                
                return False
        except Exception:
            return False
    
    def _is_valid_wav(self, file_path: str) -> bool:
        """
        检查文件是否为有效的WAV文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否为有效的WAV文件
        """
        try:
            with open(file_path, 'rb') as f:
                # 读取文件头
                header = f.read(12)
                if len(header) < 12:
                    return False
                
                # 检查RIFF和WAVE标识
                if header[:4] != b'RIFF' or header[8:12] != b'WAVE':
                    return False
                
                # 尝试使用wave模块打开
                f.seek(0)
                with wave.open(f, 'rb'):
                    pass
                
                return True
        except Exception:
            return False
    
    def _fix_wav_header(self, file_path: str) -> bool:
        """
        尝试修复WAV文件头
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否修复成功
        """
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # 检查是否是原始PCM数据（没有WAV头）
            if len(data) > 0 and data[:4] != b'RIFF':
                # 创建一个基本的WAV头
                # 假设是16位，单声道，16kHz采样率
                sample_rate = 16000
                channels = 1
                bits_per_sample = 16
                byte_rate = sample_rate * channels * bits_per_sample // 8
                block_align = channels * bits_per_sample // 8
                
                # WAV头结构
                wav_header = b'RIFF' + struct.pack('<I', len(data) + 36) + b'WAVE'
                wav_header += b'fmt ' + struct.pack('<IHHIIHH', 16, 1, channels, sample_rate, byte_rate, block_align, bits_per_sample)
                wav_header += b'data' + struct.pack('<I', len(data))
                
                # 写入修复后的文件
                with open(file_path, 'wb') as f:
                    f.write(wav_header)
                    f.write(data)
                
                return True
            
            return False
        except Exception as e:
            print(f"修复WAV文件头失败: {str(e)}")
            return False
    
    def transcribe_audio(self, audio_file: Optional[Union[BinaryIO, bytes]] = None, 
                         preprocess: bool = True) -> str:
        """
        将音频转换为文本
        
        Args:
            audio_file: 音频文件对象或字节数据，如果为None则使用麦克风录音
            preprocess: 是否对音频进行预处理以提高识别准确率
            
        Returns:
            识别出的文本
        """
        try:
            audio: Optional[AudioDataType] = None
            # 创建音频文件目录（如果不存在）
            audio_dir = "audio_files"
            if not os.path.exists(audio_dir):
                os.makedirs(audio_dir)
            
            # 生成基于时间戳的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 直接使用.wav扩展名，确保speech_recognition能正确识别
            audio_filename = os.path.join(audio_dir, f"audio_{timestamp}.wav")
            
            # 将audio_file写入指定文件
            if audio_file is not None:
                self._handle_audio_input(audio_file, audio_filename)
                print(f"音频文件已保存到: {audio_filename}")
                
                # 检查是否为有效的音频文件
                if not self._is_valid_wav(audio_filename) and not self._is_webm_opus_format(audio_filename):
                    print("检测到无效的音频文件，尝试修复文件头")
                    if self._fix_wav_header(audio_filename):
                        print("WAV文件头修复成功")
                    else:
                        print("WAV文件头修复失败")
                
                # 尝试直接使用原始文件
                try:
                    # 如果是WebM/Opus格式，先转换为WAV
                    if self._is_webm_opus_format(audio_filename):
                        print("检测到WebM/Opus格式音频，尝试转换为WAV")
                        converted_filename = os.path.join(audio_dir, f"converted_{timestamp}.wav")
                        if self._convert_audio_format(audio_filename, converted_filename):
                            print("WebM/Opus转换为WAV成功")
                            with sr.AudioFile(converted_filename) as source:
                                audio = self.recognizer.record(source)
                            # 清理转换后的文件
                            if os.path.exists(converted_filename):
                                os.remove(converted_filename)
                        else:
                            print("WebM/Opus转换为WAV失败，尝试直接处理")
                            with sr.AudioFile(audio_filename) as source:
                                audio = self.recognizer.record(source)
                    else:
                        # 对于WAV格式，直接加载
                        with sr.AudioFile(audio_filename) as source:
                            audio = self.recognizer.record(source)
                    print("直接加载音频文件成功")
                except Exception as e:
                    print(f"直接加载音频文件失败: {str(e)}")
                    
                    # 如果直接加载失败，尝试使用我们自己的解码器
                    try:
                        print("尝试使用内部解码器处理音频")
                        # 读取音频数据
                        with open(audio_filename, "rb") as f:
                            audio_data = f.read()
                        
                        # 尝试解码音频
                        decoded_audio = self.audio_codec.decode_audio(audio_data)
                        if decoded_audio and len(decoded_audio) > 0:
                            # 保存解码后的音频到新的文件
                            decoded_filename = os.path.join(audio_dir, f"decoded_{timestamp}.wav")
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
                    except Exception as decode_error:
                        print(f"内部解码器处理失败: {str(decode_error)}")
                
                # 清理临时文件
                try:
                    # 只有在音频处理失败时才清理文件
                    if audio is None and os.path.exists(audio_filename):
                        os.remove(audio_filename)
                except Exception as cleanup_error:
                    print(f"清理临时文件时出错: {str(cleanup_error)}")
            else:
                # 使用麦克风录音
                with sr.Microphone() as source:
                    print("请说话...")
                    # 调整环境噪声
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source, timeout=5)
            
            # 如果需要预处理且提供了音频文件，则进行预处理
            if preprocess and audio_file is not None and audio:
                # 获取音频数据并进行预处理
                # 修复：使用get_raw_data方法获取音频数据而不是直接访问frame_data属性
                raw_data = audio.get_raw_data()
                audio_data = np.frombuffer(raw_data, dtype=np.int16)
                # 获取音频参数
                sample_rate = audio.sample_rate
                sample_width = audio.sample_width
                processed_audio = self.audio_processor.preprocess_audio(
                    np.divide(audio_data.astype(np.float32), 32768.0), 
                    sample_rate
                )
                
                # 将处理后的音频数据编码为WAV格式
                processed_wav = self.audio_codec.encode_wav(processed_audio, sample_rate)
                
                # 创建AudioData对象并重新加载处理后的音频   
                audio_data_obj = sr.AudioData(processed_wav, sample_rate, sample_width)
                with sr.AudioFile(audio_data_obj.get_wav_data()) as source:
                    audio = self.recognizer.record(source)
            
            # 使用Google语音识别API转换文本
            if audio:
                text = self.recognizer.recognize_google(audio, language="zh-CN")
                return text
            else:
                return "无法获取音频数据"
        except UnknownValueError:
            print("无法理解音频内容")
            return "无法理解音频内容"
        except RequestError as e:
            print(f"语音识别服务错误: {str(e)}")
            return f"语音识别服务错误: {str(e)}"
        except Exception as e:
            print(f"语音识别失败: {str(e)}")
            return f"语音识别失败: {str(e)}"
    
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
