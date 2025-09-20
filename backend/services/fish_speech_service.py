# 手动注册 dual_ar 架构
from transformers import AutoConfig, PretrainedConfig
import json
import torch
import logging
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)

class DualARConfig(PretrainedConfig):
    model_type = "dual_ar"
    
    def __init__(
        self,
        vocab_size=10000,
        hidden_size=768,
        num_hidden_layers=12,
        num_attention_heads=12,
        intermediate_size=3072,
        hidden_act="gelu",
        hidden_dropout_prob=0.1,
        attention_probs_dropout_prob=0.1,
        max_position_embeddings=512,
        initializer_range=0.02,
        layer_norm_eps=1e-12,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.intermediate_size = intermediate_size
        self.hidden_act = hidden_act
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.max_position_embeddings = max_position_embeddings
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps

# 注册配置类
AutoConfig.register("dual_ar", DualARConfig)

# 加载实际配置
try:
    model_path = "/mnt/backend/models/fish-speech/checkpoints/openaudio-s1-mini"
    config_path = os.path.join(model_path, "config.json")
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            actual_config = json.load(f)
        
        logger.info("✅ dual_ar 架构已手动注册并加载实际配置")
    else:
        logger.warning("⚠️ 配置文件不存在")
        
except Exception as e:
    logger.warning(f"⚠️ 无法加载模型配置: {e}")

class FishSpeechService:
    def __init__(self, model_name: str = "/mnt/backend/models/fish-speech/checkpoints/openaudio-s1-mini"):
        """
        初始化 Fish-Speech 服务。
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self._load_model()

    def _load_model(self):
        """
        加载 Fish-Speech 模型。
        """
        try:
            logger.info(f"Loading Fish-Speech model: {self.model_name} on device: {self.device}")
            
            # 方法1: 首先尝试使用 fish_speech 原生API
            self._try_fish_speech_api()
            
            # 如果原生API失败，尝试其他方法
            if not self.model:
                self._try_alternative_methods()
                
        except Exception as e:
            logger.error(f"❌ Failed to load Fish-Speech model: {e}")

    def _try_fish_speech_api(self):
        """
        尝试使用 fish_speech 包的原生API。
        """
        try:
            from fish_speech.utils import load_model
            
            logger.info("🐟 Trying to load using fish_speech native API...")
            
            # 使用 fish_speech 的加载函数
            self.model = load_model(self.model_name, device=self.device)
            logger.info("✅ Fish-Speech model loaded using native API")
            
        except ImportError:
            logger.error("❌ fish_speech package not installed, trying alternative methods...")
            return False
        except Exception as e:
            logger.error(f"❌ Native API failed: {e}, trying alternative methods...")
            return False
        return True

    def _try_alternative_methods(self):
        """
        尝试其他加载方法。
        """
        try:
            # 方法2: 使用 transformers 的低级API
            from transformers import AutoModel
            
            logger.info("🔄 Trying to load with transformers AutoModel...")
            
            # 加载配置
            config = AutoConfig.from_pretrained(self.model_name)
            
            # 加载模型，不使用 device_map
            self.model = AutoModel.from_pretrained(
                self.model_name,
                config=config,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                trust_remote_code=True
            )
            
            # 手动移动设备
            self.model = self.model.to(self.device)
            logger.info("✅ Fish-Speech model loaded using transformers")
            
        except Exception as e:
            logger.error(f"❌ Transformers loading failed: {e}")
            
            # 方法3: 使用最基础的加载方式
            try:
                logger.info("🔄 Trying basic model loading...")
                
                # 直接使用 PyTorch 加载（如果模型是 .pth 或 .bin 格式）
                model_path = self.model_name
                model_files = [f for f in os.listdir(model_path) if f.endswith(('.pth', '.bin', '.safetensors'))]
                
                if model_files:
                    # 这里需要根据实际模型结构来创建模型实例
                    # 由于是复杂模型，我们只能加载权重
                    logger.warning("⚠️ Basic loading: only weights can be loaded, model architecture required")
                else:
                    logger.error("❌ No model weight files found")
                    
            except Exception as inner_e:
                logger.error(f"❌ Basic loading also failed: {inner_e}")

    def synthesize_speech(self, text: str) -> Optional[Dict[str, Any]]:
        """
        合成语音。
        """
        if not self.model:
            logger.error("❌ Model is not loaded.")
            return None

        try:
            # 根据模型类型调用不同的生成方法
            if hasattr(self.model, 'generate'):
                # 如果模型有 generate 方法
                result = self.model.generate(text=text)
                return {"audio": result, "sampling_rate": 24000}
            elif hasattr(self.model, 'infer'):
                # 如果模型有 infer 方法
                result = self.model.infer(text=text)
                return {"audio": result, "sampling_rate": 24000}
            else:
                # 尝试调用模型
                logger.warning("⚠️ Using direct model call - may not work correctly")
                inputs = self._prepare_inputs(text)
                with torch.no_grad():
                    output = self.model(**inputs)
                return self._process_output(output)
                
        except Exception as e:
            logger.error(f"❌ Synthesis failed: {e}")
            return None

    def _prepare_inputs(self, text: str):
        """准备模型输入（需要根据实际模型调整）。"""
        # 这里是伪代码，需要根据实际模型调整
        return {"input_text": text}

    def _process_output(self, output):
        """处理模型输出（需要根据实际模型调整）。"""
        # 这里是伪代码，需要根据实际模型调整
        return {"audio": output, "sampling_rate": 24000}

    def is_loaded(self) -> bool:
        """检查模型是否成功加载。"""
        return self.model is not None

# 测试代码
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 测试配置注册
    try:
        config = AutoConfig.from_pretrained("/mnt/backend/models/fish-speech/checkpoints/openaudio-s1-mini")
        print(f"✅ 配置加载成功: {config.model_type}")
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
    
    # 测试服务初始化
    print("\n🔧 测试模型加载...")
    service = FishSpeechService()
    print(f"模型加载状态: {service.is_loaded()}")