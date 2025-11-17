import time
import opuslib_next
import torch
from ai_core.vad.base import Vad
from utils.logger import Logger

TAG = __name__

class VADModule(Vad):
    def __init__(self, config):
        # print(config)
        # 加载模型，这里加载的是silero_vad.jit,加载后返回模型对象和工具链，我们这里只需要模型对象
        self.model = torch.hub.load(
            repo_or_dir=config["model_dir"], source="local", force_reload=False,
            model="silero_vad",
        )[0] # type: ignore
        if not callable(self.model):
            raise RuntimeError("模型加载失败，self.model 不是一个可调用对象")
        
        self.logger = Logger().log_init(TAG)
        # 创建opus解码器，采样率16k，单声道
        self.decoder = opuslib_next.Decoder(16000, 1)
        # 获取配置的门槛值
        self.threshold = float(config.get("threshold", 0.5))
        # 获取配置的最小静默时间
        self.min_silence_ms = int(config.get("min_silence_ms", 800))
        self.pcm_buffer = bytearray()
        # 上一次有语音的时间
        self.have_voice_last_time = 0.0
        # 是否停止
        self.is_voice_stop = False
        # 是否有语音
        self.is_have_voice = False
        
        self.have_voice_count = 0
        
    # 检测是否有静音数据
    def is_no_speech(self, connect, audio_data):

        try:
            pcm_data = self.decoder.decode(audio_data, 960)
            self.pcm_buffer.extend(pcm_data)
            # 处理缓冲区中的完整帧（每次处理512采样点）
            frame_quantity = 512 * 2
            is_have_voice = False
            while len(self.pcm_buffer) >= frame_quantity:
                # 提取要处理的PCM数据片段
                pcm_chunk = self.pcm_buffer[: frame_quantity]
                # 将已提取的PCM数据片从缓冲区删除
                self.pcm_buffer = self.pcm_buffer[frame_quantity:]
                # 将pcm二进制字节流数据转换为张量
                pcm_tensor = self.pcm_to_tensor(pcm_chunk)
                # 禁止梯度的推理计算
                with torch.no_grad():
                    threshold = self.model(pcm_tensor, 16000).item()
                # 如果语音概率高于阈值，则说明有语音活动
                if threshold >= self.threshold:
                    is_have_voice = True
                # 如果当前为静音，并且之前有语音活动，需要计算静音时长
                if not is_have_voice and self.is_have_voice:
                    # 将当前时间减去上次有语音活动时间
                    stop_duration = time.time() * 1000 - self.have_voice_last_time
                    # 如果静音时长超过配置的最小静音时长，则认为一句话说完
                    if stop_duration >= self.min_silence_ms:
                        self.is_voice_stop = True
                        self.is_have_voice = False
                        self.have_voice_count = 0
                        return True, self.is_have_voice
                # 如果当前有语音活动，则将当前时间保存为有语音活动时的时间
                if is_have_voice:
                    self.have_voice_count = self.have_voice_count + 1
                    if self.have_voice_count > 5:
                        # self.logger.error(f"有音频 活动..")
                        self.is_have_voice = True
                    self.have_voice_last_time = time.time() * 1000
            return False, self.is_have_voice
        except opuslib_next.OpusError as e:
            self.logger.error(f"opus解码异常: {e}")
        except Exception as e:
            self.logger.error(f"推理异常:{e}")