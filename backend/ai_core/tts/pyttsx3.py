import os
import pyttsx3
from ai_core.tts.base import TTS
from utils.util import Util

class TTSModule(TTS):
    def __init__(self, config):
        self.output_dir = Util.get_project_dir() + config.get("output_dir")
        self.voice = config.get("voice")

    def _select_voice(self, engine):
        if not self.voice:
            return
        try:
            voices = engine.getProperty("voices")
            for v in voices:
                if self.voice and (self.voice in getattr(v, "id", "") or self.voice in getattr(v, "name", "")):
                    engine.setProperty("voice", v.id)
                    return
        except Exception:
            return

    def text_to_opus_data(self, text):
        text = super().clean_text_for_tts(text)
        if not text:
            return b"", 0, text
        audio_path = Util.get_random_file_path(self.output_dir, "wav")
        try:
            engine = pyttsx3.init()
            self._select_voice(engine)
            engine.save_to_file(text, audio_path)
            engine.runAndWait()
        except Exception:
            return [], 0, text
        if not os.path.exists(audio_path):
            return [], 0, text
        opus_datas, duration = super().audio_file_to_opus(audio_path)
        return opus_datas, duration, text
