import os
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
from ai_core.asr.base import Asr
from utils.util import Util

class ASRModule(Asr):
    def __init__(self, config):
        self.model_dir = config.get("model_dir")
        self.output_dir = Util.get_project_dir() + config.get("output_dir")
        print(self.model_dir,self.output_dir)
        
        self.model = AutoModel(
            model = self.model_dir,
            device = "cpu",
            vad_kwargs = {"max_single_segment_time": 3},  # 修正拼写错误
            disable_updates = True,
            trust_remote_code=False
        )
        
    # 音频转文字    
    def audio_file_to_text(self, audio_file_path):
        try:
            # 读取音频文件为字节
            with open(audio_file_path, 'rb') as f:
                audio_bytes = f.read()
            
            # 使用字节数据作为输入
            res = self.model.generate(
                input=audio_bytes,
                cache={},
                language="auto",
                use_itn=True,
                batch_size_s=60,
                merge_vad=True,
            )
            
            if res and len(res) > 0:
                res = res[0]["text"]
                return rich_transcription_postprocess(res)
            return ""
        except Exception as e:
            print(f"ASR处理错误: {e}")
            return ""
    # opus音频转文字
    def opus_data_to_text(self,opus_data):
        file_path = Util.get_random_file_path(self.output_dir, "wav")
        super().opus_data_to_wav(opus_data, file_path)
        # 判断输出文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件 {file_path} 不存在")
        res = self.audio_file_to_text(file_path)
        return res