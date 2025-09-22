import ChatTTS
import torch
import torchaudio
import os

class ChatTTSEngine:
    _instance = None

    def __new__(cls, model_dir: str):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model_dir = model_dir
            cls._instance._init_model()
        return cls._instance

    def _init_model(self):
        self.chat = ChatTTS.Chat()
        self.chat.load(compile=False, source="custom", custom_path=self.model_dir)
        self.chat.eval()

    def tts(self, text: str, refine_text=True) -> tuple[int, torch.Tensor]:
        """返回 (sr, wav_tensor)"""
        if refine_text:
            text = self.chat.infer(text, skip_refine_text=False)[0]
        wavs = self.chat.infer(text, skip_refine_text=True)
        sr = 24000
        return sr, wavs[0]

# 全局单例
ENGINE = ChatTTSEngine(os.path.join(os.path.dirname(__file__), "../models/ChatTTS"))