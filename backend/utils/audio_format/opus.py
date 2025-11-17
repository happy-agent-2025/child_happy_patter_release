import os
import pickle
import wave
import numpy as np
import opuslib_next
from pydub import AudioSegment

class Opus_Encode:
    
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        self.channels = 1
        self.sample_rate = 16000
        self.sample_width = 2
        self.opus_sample_rate = 16000
        self.opus_channels = 1
        self.opus_sample_width = 2
        self.opus_frame_time = 60   
        self.opus_frame_size = int(self.opus_sample_rate * self.opus_frame_time / 1000)
    
    # 音频转opus
    def audio_to_opus(self, audio_path):
        file_type = os.path.splitext(audio_path)[1]
        
        if file_type:
            file_type = file_type.lstrip(".") #去掉.
            
        audio = AudioSegment.from_file(audio_path, format=file_type) #音频文件
        
        # 音频参数设置
        audio = audio.set_channels(self.channels).set_frame_rate(self.sample_rate).set_sample_width(self.sample_width)
        
        #计算音频时长
        duration = len(audio) / 1000
        raw_data = audio.raw_data # 获取音频
        
        encoder = opuslib_next.Encoder(self.opus_sample_rate, self.opus_channels, opuslib_next.APPLICATION_AUDIO)
        
        # 获取每一帧的采样数
        frame_num = self.opus_frame_size
        
        # 每一帧的采样字节数
        frame_bytes_size = frame_num * self.opus_channels * self.opus_sample_width
        
        opus_data = []
        
        # 处理每一帧数据
        for i in range(0, len(raw_data), frame_bytes_size):
            chunk = raw_data[i:i+frame_bytes_size] # 每次取一帧
            chunk_len = len(chunk)
            
            if chunk_len < frame_bytes_size: # 如果帧的长度不足一帧，则填充0
                chunk += b'\x00' * (frame_bytes_size - chunk_len)
            
            np_frame = np.frombuffer(chunk, dtype=np.int16) # 将帧数据转换为numpy数组
            np_bytes = np_frame.tobytes() # 将numpy数组转换为字节
            
            opus_frame = encoder.encode(np_bytes, frame_num) # 编码一帧数据，二进制显示
            
            opus_data.append(opus_frame)
            
        return opus_data, duration
    
    # opus 解码
    def opus_to_wav_file(self, output_file, opus_data:list[bytes]):
                
        decoder = opuslib_next.Decoder(self.opus_sample_rate, self.opus_channels)
        
        pcm_data = []
    
        # 解码一帧数据
        for opus_frame in opus_data:
            try:
                pcm_frame = decoder.decode(opus_frame, self.opus_frame_size)
                pcm_data.append(pcm_frame)
                
            except opuslib_next.OpusError as e:
                print(f"Error decoding frame: {e}")
                continue
            
        with wave.open(output_file, 'wb') as f:
            f.setnchannels(self.opus_channels)
            f.setsampwidth(self.opus_sample_width)
            f.setframerate(self.opus_sample_rate)
            f.writeframes(b''.join(pcm_data)) # 将PCM数据写入WAVE文件
        return output_file

    def save_opus_raw(self, opus_datas, output_path):
        # 自动关闭文件
        with open(output_path, "wb") as f:
            pickle.dump(opus_datas, f)
            
    def load_opus_raw(self, input_path):
        with open(input_path, "rb") as f:
            opus_datas = pickle.load(f)
            
        return opus_datas
    
    # 保存opus数据
    def save_opus_raw_custom(self, opus_datas, output_path):
        with open(output_path, "wb") as f:
            for frame in opus_datas:
                f.write(len(frame).to_bytes(4, byteorder="big")) # 写入帧长度
                f.write(frame) # 写入帧数据
    
    #  自定义加载OPUS数据
    def load_opus_raw_custom(self, input_path):
        frames = []
        with open(input_path, "rb") as f:
            data = f.read()
            index = 0
            while index < len(data):
                frame_len = int.from_bytes(data[index:index+4], byteorder="big")
                index += 4
                frame = data[index:index+frame_len]
                index += frame_len
                frames.append(frame)
                
        return frames
        
    
if __name__ == "__main__":
    opus = Opus_Encode()
    opus_data, duration = opus.audio_to_opus("D:\\xiaozhi_source\\backend\\output.mp3")
    opus.save_opus_raw_custom(opus_data, "D:\\xiaozhi_source\\backend\\output.opus")
    opus_datas = opus.load_opus_raw_custom("D:\\xiaozhi_source\\backend\\output.opus")
    
    # print(opus_data, duration)
    # print(">>>>>>>>>>>>>>>>>>>>>>", opus_datas)
        
            
        
        