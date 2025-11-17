from abc import ABC, abstractmethod

import numpy as np
import torch

class Vad(ABC):
    @abstractmethod
    def is_no_speech(self, connect, audio_data) -> bool:
        """检测是否静音"""
        pass
    
    # 将pcm数据转换为张量数据
    def pcm_to_tensor(self, pcm_chunk: bytes) -> torch.Tensor:
        """将pcm数据转换为tensor张量数据"""
        # 将pcm二进制字节流数据转换为np的int16数组
        pcm_int16 = np.frombuffer(pcm_chunk, dtype=np.int16)
        # 将int16数组转换为float32数组
        pcm_float32 = pcm_int16.astype(np.float32)
        # 归一化pcm数据
        pcm_normalized = pcm_float32 / 32768.0
        # 将pcm归一化的数据转换为张量
        pcm_tensor = torch.from_numpy(pcm_normalized)
        return pcm_tensor