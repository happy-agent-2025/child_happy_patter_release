from utils.ai_factory.ai_factory import AIFactory

class AiInstanceRepository:
    def __init__(self, config):
        self.config = config
        self.ai_factory = AIFactory(self.config)
        self.asr = self.ai_factory.create_asr_instance()
        self.tts = self.ai_factory.create_tts_instance()
        self.llm = self.ai_factory.create_llm_instance()
        self.vad = self.ai_factory.create_vad_instance()
        