import numpy as np
import wave
import struct
from typing import BinaryIO, Tuple
import io
import zlib
import soundfile as sf
from scipy import signal


class AudioCodecService:
    """
    音频编解码服务
    提供音频格式转换和数据压缩/解压缩功能
    """
    
    def __init__(self):
        pass
    
    def encode_wav(self, audio_data: np.ndarray, sample_rate: int = 16000, 
                   sample_width: int = 2, channels: int = 1) -> bytes:
        """
        将音频数据编码为WAV格式
        
        Args:
            audio_data: 音频数据数组 (归一化到-1到1之间)
            sample_rate: 采样率
            sample_width: 采样宽度（字节）
            channels: 声道数
            
        Returns:
            WAV格式的音频数据
        """
        # 将浮点数据转换为整数数据
        if sample_width == 2:
            # 16位音频
            audio_int = (audio_data * 32767).astype(np.int16)
            fmt = '<h'  # 小端序16位有符号整数
        elif sample_width == 1:
            # 8位音频
            audio_int = (audio_data * 127).astype(np.int8)
            fmt = '<b'  # 小端序8位有符号整数
        else:
            raise ValueError("Unsupported sample width")
        
        # 将数据打包为二进制格式
        audio_bytes = b''.join(struct.pack(fmt, sample) for sample in audio_int)
        
        # 创建WAV文件头
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_bytes)
        
        return wav_buffer.getvalue()
    
    def decode_wav(self, wav_data: bytes) -> Tuple[np.ndarray, int]:
        """
        解码WAV格式音频数据
        
        Args:
            wav_data: WAV格式的音频数据
            
        Returns:
            (音频数据数组, 采样率)
        """
        wav_buffer = io.BytesIO(wav_data)
        with wave.open(wav_buffer, 'rb') as wav_file:
            # 获取音频参数
            sample_rate = wav_file.getframerate()
            sample_width = wav_file.getsampwidth()
            channels = wav_file.getnchannels()
            n_frames = wav_file.getnframes()
            
            # 读取音频数据
            audio_bytes = wav_file.readframes(n_frames)
            
            # 根据采样宽度解包数据
            if sample_width == 2:
                # 16位音频
                fmt = '<h'
                # 修复解包格式
                audio_int = struct.unpack('<' + 'h' * n_frames, audio_bytes)
                audio_data = np.array(audio_int, dtype=np.float32) / 32767
            elif sample_width == 1:
                # 8位音频
                fmt = '<b'
                # 修复解包格式
                audio_int = struct.unpack('<' + 'b' * n_frames, audio_bytes)
                audio_data = np.array(audio_int, dtype=np.float32) / 127
            else:
                raise ValueError("Unsupported sample width")
            
            return audio_data, sample_rate
    
    def compress_audio(self, audio_data: bytes) -> bytes:
        """
        压缩音频数据
        
        Args:
            audio_data: 原始音频数据
            
        Returns:
            压缩后的音频数据
        """
        return zlib.compress(audio_data)
    
    def decompress_audio(self, compressed_data: bytes) -> bytes:
        """
        解压缩音频数据
        
        Args:
            compressed_data: 压缩的音频数据
            
        Returns:
            解压缩后的音频数据
        """
        return zlib.decompress(compressed_data)
    
    def convert_sample_rate(self, audio_data: np.ndarray, 
                           original_rate: int, target_rate: int) -> np.ndarray:
        """
        转换音频采样率
        
        Args:
            audio_data: 音频数据数组
            original_rate: 原始采样率
            target_rate: 目标采样率
            
        Returns:
            转换采样率后的音频数据
        """
        if original_rate == target_rate:
            return audio_data
            
        # 使用scipy的高质量重采样算法
        # 计算重采样系数
        resample_ratio = target_rate / original_rate
        
        # 使用scipy.signal.resample进行高质量重采样
        if resample_ratio > 1:
            # 上采样
            new_length = int(len(audio_data) * resample_ratio)
            resampled = signal.resample(audio_data, new_length)
        else:
            # 下采样
            new_length = int(len(audio_data) * resample_ratio)
            resampled = signal.resample(audio_data, new_length)
            
        return resampled
    
    def encode_mp3(self, audio_data: np.ndarray, sample_rate: int = 16000) -> bytes:
        """
        将音频数据编码为MP3格式
        
        Args:
            audio_data: 音频数据数组 (归一化到-1到1之间)
            sample_rate: 采样率
            
        Returns:
            MP3格式的音频数据
        """
        # 使用soundfile将音频数据写入内存缓冲区
        mp3_buffer = io.BytesIO()
        sf.write(mp3_buffer, audio_data, sample_rate, format='MP3')
        return mp3_buffer.getvalue()
    
    def decode_mp3(self, mp3_data: bytes) -> Tuple[np.ndarray, int]:
        """
        解码MP3格式音频数据
        
        Args:
            mp3_data: MP3格式的音频数据
            
        Returns:
            (音频数据数组, 采样率)
        """
        # 使用soundfile从内存缓冲区读取音频数据
        mp3_buffer = io.BytesIO(mp3_data)
        audio_data, sample_rate = sf.read(mp3_buffer)
        return audio_data, sample_rate
    
    def encode_flac(self, audio_data: np.ndarray, sample_rate: int = 16000) -> bytes:
        """
        将音频数据编码为FLAC格式
        
        Args:
            audio_data: 音频数据数组 (归一化到-1到1之间)
            sample_rate: 采样率
            
        Returns:
            FLAC格式的音频数据
        """
        # 使用soundfile将音频数据写入内存缓冲区
        flac_buffer = io.BytesIO()
        sf.write(flac_buffer, audio_data, sample_rate, format='FLAC')
        return flac_buffer.getvalue()
    
    def decode_flac(self, flac_data: bytes) -> Tuple[np.ndarray, int]:
        """
        解码FLAC格式音频数据
        
        Args:
            flac_data: FLAC格式的音频数据
            
        Returns:
            (音频数据数组, 采样率)
        """
        # 使用soundfile从内存缓冲区读取音频数据
        flac_buffer = io.BytesIO(flac_data)
        audio_data, sample_rate = sf.read(flac_buffer)
        return audio_data, sample_rate