from abc import ABC, abstractmethod
from utils.audio_format.opus import Opus_Encode


class Asr(ABC):

    def opus_data_to_wav(self,opus_data, file_path):
        """将opus数据转为wav并保存到file_path"""
        opus = Opus_Encode()
        print(file_path)
        opus.opus_to_wav_file(file_path, opus_data)

    @abstractmethod
    def opus_data_to_text(self, opus_data):
        """将opus数据转为文本"""
        raise NotImplementedError()