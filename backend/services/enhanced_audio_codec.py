"""
增强的音频编解码服务
解决音频格式兼容性问题，支持多种格式的统一处理
"""

import numpy as np
import wave
import struct
from typing import BinaryIO, Tuple, Optional, Union, Dict, Any
import io
import logging
import tempfile
import os
from pathlib import Path

# 配置日志
logger = logging.getLogger(__name__)

class EnhancedAudioCodecService:
    """
    增强的音频编解码服务
    - 支持多种音频格式（WAV, WebM, MP3, OGG等）
    - 统一的格式转换接口
    - 高效的内存操作
    - 完善的错误处理
    """
    
    def __init__(self):
        self.supported_formats = {
            'wav': self._handle_wav,
            'webm': self._handle_webm,
            'mp3': self._handle_mp3,
            'ogg': self._handle_ogg,
            'mp4': self._handle_mp4,
            'm4a': self._handle_m4a
        }
        
        # 检查可用的音频处理库
        self.available_libs = self._check_available_libraries()
        logger.info(f"可用的音频处理库: {list(self.available_libs.keys())}")
    
    def _check_available_libraries(self) -> Dict[str, bool]:
        """检查可用的音频处理库"""
        libs = {}
        
        # 检查pydub
        try:
            import pydub
            libs['pydub'] = True
            logger.info("✅ pydub 可用")
        except ImportError:
            libs['pydub'] = False
            logger.warning("⚠️ pydub 不可用，建议安装: pip install pydub")
        
        # 检查ffmpeg-python
        try:
            import ffmpeg
            libs['ffmpeg'] = True
            logger.info("✅ ffmpeg-python 可用")
        except ImportError:
            libs['ffmpeg'] = False
            logger.warning("⚠️ ffmpeg-python 不可用，建议安装: pip install ffmpeg-python")
        
        # 检查soundfile
        try:
            import soundfile as sf
            libs['soundfile'] = True
            logger.info("✅ soundfile 可用")
        except ImportError:
            libs['soundfile'] = False
            logger.warning("⚠️ soundfile 不可用，建议安装: pip install soundfile")
        
        return libs
    
    def detect_audio_format(self, audio_data: bytes) -> str:
        """
        检测音频格式
        
        Args:
            audio_data: 音频数据字节
            
        Returns:
            检测到的音频格式
        """
        if not audio_data:
            raise ValueError("音频数据为空")
        
        # 检查文件头魔数
        if audio_data.startswith(b'RIFF') and b'WAVE' in audio_data[:12]:
            return 'wav'
        elif audio_data.startswith(b'\x1a\x45\xdf\xa3'):  # WebM/Matroska
            return 'webm'
        elif audio_data.startswith(b'ID3') or audio_data.startswith(b'\xff\xfb'):
            return 'mp3'
        elif audio_data.startswith(b'OggS'):
            return 'ogg'
        elif audio_data.startswith(b'\x00\x00\x00\x20ftypM4A'):
            return 'm4a'
        elif b'ftyp' in audio_data[:20]:
            return 'mp4'
        else:
            logger.warning("无法识别音频格式，默认尝试WAV")
            return 'wav'
    
    def convert_to_standard_format(self, audio_data: bytes, 
                                 target_sample_rate: int = 16000,
                                 target_channels: int = 1,
                                 target_sample_width: int = 2) -> Tuple[bytes, Dict[str, Any]]:
        """
        将任意格式的音频转换为标准WAV格式
        
        Args:
            audio_data: 输入音频数据
            target_sample_rate: 目标采样率
            target_channels: 目标声道数
            target_sample_width: 目标采样宽度（字节）
            
        Returns:
            (标准WAV数据, 音频信息)
        """
        if not audio_data:
            raise ValueError("音频数据为空")
        
        # 检测输入格式
        input_format = self.detect_audio_format(audio_data)
        logger.info(f"检测到音频格式: {input_format}")
        
        # 尝试多种转换方法
        conversion_methods = [
            self._convert_with_pydub,
            self._convert_with_ffmpeg,
            self._convert_with_soundfile,
            self._convert_with_wave_fallback
        ]
        
        last_error = None
        for method in conversion_methods:
            try:
                result = method(audio_data, input_format, target_sample_rate, 
                              target_channels, target_sample_width)
                if result:
                    wav_data, info = result
                    logger.info(f"转换成功，使用方法: {method.__name__}")
                    return wav_data, info
            except Exception as e:
                last_error = e
                logger.warning(f"转换方法 {method.__name__} 失败: {e}")
                continue
        
        raise Exception(f"所有转换方法都失败，最后错误: {last_error}")
    
    def _convert_with_pydub(self, audio_data: bytes, input_format: str,
                           target_sample_rate: int, target_channels: int,
                           target_sample_width: int) -> Optional[Tuple[bytes, Dict[str, Any]]]:
        """使用pydub进行转换"""
        if not self.available_libs.get('pydub'):
            return None
        
        try:
            from pydub import AudioSegment
            
            # 从字节数据创建音频段
            if input_format == 'webm':
                # WebM需要特殊处理
                audio = AudioSegment.from_file(io.BytesIO(audio_data), format="webm")
            else:
                audio = AudioSegment.from_file(io.BytesIO(audio_data), format=input_format)
            
            # 获取原始信息
            original_info = {
                'sample_rate': audio.frame_rate,
                'channels': audio.channels,
                'sample_width': audio.sample_width,
                'duration_ms': len(audio),
                'format': input_format
            }
            
            # 转换为目标格式
            audio = audio.set_frame_rate(target_sample_rate)
            audio = audio.set_channels(target_channels)
            audio = audio.set_sample_width(target_sample_width)
            
            # 导出为WAV
            wav_buffer = io.BytesIO()
            audio.export(wav_buffer, format="wav")
            wav_data = wav_buffer.getvalue()
            
            # 目标信息
            target_info = {
                'sample_rate': target_sample_rate,
                'channels': target_channels,
                'sample_width': target_sample_width,
                'duration_ms': len(audio),
                'size_bytes': len(wav_data),
                'original': original_info
            }
            
            return wav_data, target_info
            
        except Exception as e:
            logger.error(f"pydub转换失败: {e}")
            return None
    
    def _convert_with_ffmpeg(self, audio_data: bytes, input_format: str,
                            target_sample_rate: int, target_channels: int,
                            target_sample_width: int) -> Optional[Tuple[bytes, Dict[str, Any]]]:
        """使用ffmpeg进行转换"""
        if not self.available_libs.get('ffmpeg'):
            return None
        
        try:
            import ffmpeg
            
            # 确定音频编码器
            acodec = 'pcm_s16le' if target_sample_width == 2 else 'pcm_s8'
            
            # 使用ffmpeg管道进行转换
            process = (
                ffmpeg
                .input('pipe:0', format=input_format if input_format != 'webm' else 'matroska')
                .output(
                    'pipe:1',
                    format='wav',
                    acodec=acodec,
                    ar=target_sample_rate,
                    ac=target_channels
                )
                .overwrite_output()
                .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True, quiet=True)
            )
            
            # 发送输入数据并获取输出
            wav_data, stderr = process.communicate(input=audio_data)
            
            if process.returncode != 0:
                raise Exception(f"FFmpeg转换失败: {stderr.decode()}")
            
            # 分析输出音频信息
            info = {
                'sample_rate': target_sample_rate,
                'channels': target_channels,
                'sample_width': target_sample_width,
                'size_bytes': len(wav_data),
                'format': 'wav'
            }
            
            return wav_data, info
            
        except Exception as e:
            logger.error(f"ffmpeg转换失败: {e}")
            return None