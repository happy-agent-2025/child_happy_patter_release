import asyncio
import os
import edge_tts
from ai_core.tts.base import TTS
from utils.util import Util

class TTSModule(TTS):
    def __init__(self, config):
        self.output_dir = Util.get_project_dir() + config.get("output_dir")
        self.voice = config.get("voice")
        
    def text_to_opus_data(self, text):
        
        text = super().clean_text_for_tts(text)
        
        # 返回3个变量
        if not text:
            return b"", 0, text
        
        audio_path = Util.get_random_file_path(self.output_dir, "mp3")
        comunicate = edge_tts.Communicate(text, self.voice)
        
        # 同步里调用异步
        try:
            asyncio.run(comunicate.save(audio_path)) # 使用循环运行异步任务
        except RuntimeError:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(comunicate.save(audio_path))
            loop.close()
        except edge_tts.exceptions.NoAudioReceived:
            return [], 0, text
        except Exception:
            return [], 0, text
            
        if not os.path.exists(audio_path): return [], 0, text
        
        opus_datas, duration = super().audio_file_to_opus(audio_path)
        
        # 返回音频 + 时间 + 文字
        return opus_datas, duration, text
        
