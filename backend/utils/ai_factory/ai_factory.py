import importlib
from pathlib import Path
import sys

from ai_core.asr.base import Asr
from ai_core.llm.base import LLM
from ai_core.tts.base import TTS
from ai_core.vad.base import Vad
from utils.logger import Logger

TAG = __name__

# AI工厂类
class AIFactory:
    def __init__(self, config):
        self.config = config
        self.logger =Logger().log_init(TAG)
        
    
    # 创建ASR实例,语音识别的实例类
    def _create_instance(self, type:str, base_class):
        model = self.config["select_model"][type]
        config_ = self.config[type][model]
        
        module_file = config_.get("type") # 获取模型文件名
        file_path = Path("ai_core") / type.lower() / f'{module_file}.py'
        
        # 加载配置的模块
        if file_path.exists():
            lib_name = '.'.join(file_path.with_suffix('').parts) # 获取模块名，重新获取模块
            if lib_name not in sys.modules:
                sys.modules[lib_name] = importlib.import_module(f'{lib_name}')
                class_name = f'{type}Module'
                return getattr(sys.modules[lib_name], class_name)(config_)
            
        raise Exception(f"未找到{type}模块: {module_file}")
    # 创建ASR实例,语音识别的实例类
    def create_asr_instance(self) ->  Asr:
        self.logger.info("AI工厂创建ASR实例")
        return self._create_instance("ASR", Asr)
    
    # 创建LLM实例,语言模型实例类
    def create_llm_instance(self) ->  LLM:
        self.logger.info("AI工厂创建TTS实例")
        return self._create_instance("LLM", LLM)
    
    # 创建TTS实例,语音合成的实例类
    def create_tts_instance(self) ->  TTS:
        self.logger.info("AI工厂创建LLM实例")
        return self._create_instance("TTS", TTS)
    
    # 创建TTS实例,语音合成的实例类
    def create_vad_instance(self) ->  Vad:
        self.logger.info("AI工厂创建LLM实例")
        return self._create_instance("VAD", Vad)