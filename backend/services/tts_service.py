import tempfile
import os
from io import BytesIO
from typing import Optional, List, Dict
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

class TTSService:
    """文本转语音服务（修复事件循环冲突）"""
    
    def __init__(self, engine_type: str = "pyttsx3", **kwargs):
        """
        初始化TTS引擎
        
        Args:
            engine_type: 引擎类型 (pyttsx3, gtts, edge_tts)
            **kwargs: 引擎特定参数
        """
        self.engine = None
        self.engine_type = engine_type
        self.logger = logging.getLogger(__name__)
        self._thread_pool = ThreadPoolExecutor(max_workers=1)  # 用于线程隔离
        
        self._initialize_engine(engine_type, **kwargs)
    
    def _initialize_engine(self, engine_type: str, **kwargs):
        """初始化指定的TTS引擎"""
        try:
            if engine_type == "pyttsx3":
                self._init_pyttsx3(**kwargs)
            elif engine_type == "gtts":
                self._init_gtts(**kwargs)
            elif engine_type == "edge_tts":
                self._init_edge_tts(**kwargs)
            else:
                raise ValueError(f"不支持的TTS引擎类型: {engine_type}")
                
            self.logger.info(f"TTS引擎初始化成功: {engine_type}")
            
        except ImportError as e:
            self.logger.error(f"缺少依赖: {e}")
            raise
        except Exception as e:
            self.logger.error(f"引擎初始化失败: {e}")
            raise
    
    def _init_pyttsx3(self, **kwargs):
        """初始化pyttsx3引擎（离线）"""
        try:
            import pyttsx3
            
            self.engine = pyttsx3.init()
            
            # 设置参数
            rate = kwargs.get('rate', 100)  # 语速
            volume = kwargs.get('volume', 0.9)  # 音量
            voice_id = kwargs.get('voice_id')  # 语音ID
            
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
            
            if voice_id is not None:
                voices = self.engine.getProperty('voices')
                if isinstance(voices, list) and voice_id < len(voices):
                    self.engine.setProperty('voice', voices[voice_id].id)
            
            self.logger.debug("pyttsx3引擎配置完成")
            
        except ImportError:
            self.logger.error("请安装pyttsx3: pip install pyttsx3")
            raise
    
    def _init_gtts(self, **kwargs):
        """初始化gTTS引擎（在线，需要网络）"""
        try:
            from gtts import gTTS
            self.gTTS = gTTS
            self.lang = kwargs.get('lang', 'zh-cn')
            self.slow = kwargs.get('slow', False)
            self.logger.debug("gTTS引擎初始化完成")
            
        except ImportError:
            self.logger.error("请安装gTTS: pip install gtts")
            raise
    
    def _init_edge_tts(self, **kwargs):
        """初始化Edge-TTS引擎（在线，需要网络）"""
        try:
            import edge_tts
            self.edge_tts = edge_tts
            self.voice = str(kwargs.get('voice', 'zh-CN-XiaoxiaoNeural'))
            self.rate = str(kwargs.get('rate', '+0%'))
            self.volume = str(kwargs.get('volume', '+0%'))
            self.logger.debug("Edge-TTS引擎初始化完成")
            
        except ImportError:
            self.logger.error("请安装edge-tts: pip install edge-tts")
            raise
    
    def synthesize_speech(self, text: str, output_format: str = "wav") -> Optional[BytesIO]:
        """
        将文本转换为语音
        
        Args:
            text: 要转换的文本
            output_format: 输出格式 (wav, mp3)
            
        Returns:
            包含音频数据的字节流，失败时返回None
        """
        if not text or len(text.strip()) == 0:
            self.logger.warning("输入文本为空")
            return None
        
        try:
            if self.engine_type == "pyttsx3":
                return self._synthesize_pyttsx3(text, output_format)
            elif self.engine_type == "gtts":
                return self._synthesize_gtts(text, output_format)
            elif self.engine_type == "edge_tts":
                return self._synthesize_edge_tts_thread_safe(text, output_format)
            else:
                raise ValueError(f"不支持的引擎类型: {self.engine_type}")
                
        except Exception as e:
            self.logger.error(f"语音合成失败: {e}")
            return None
    
    def _synthesize_pyttsx3(self, text: str, output_format: str) -> BytesIO:
        """使用pyttsx3合成语音"""
        with tempfile.NamedTemporaryFile(suffix=f'.{output_format}', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            # 保存到临时文件
            if self.engine:
                self.engine.save_to_file(text, temp_filename)
                self.engine.runAndWait()
            
                # 读取文件内容到内存
                with open(temp_filename, 'rb') as f:
                    audio_data = f.read()
                
                # 创建内存缓冲区
                audio_buffer = BytesIO(audio_data)
                audio_buffer.seek(0)
                
                self.logger.debug(f"pyttsx3合成成功: {len(text)}字符 -> {len(audio_data)}字节")
                return audio_buffer
            else:
                self.logger.error(f"无法处理音频输入")
                raise ValueError("无法处理音频输入")
            
        except Exception as e:
            self.logger.error(f"pyttsx3合成失败: {str(e)}")
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_filename):
                try:
                    os.unlink(temp_filename)
                except:
                    pass
    
    def _synthesize_gtts(self, text: str, output_format: str) -> Optional[BytesIO]:
        """使用gTTS合成语音"""
        if output_format != 'mp3':
            self.logger.warning("gTTS只支持MP3格式，将使用mp3")
            output_format = 'mp3'
        
        try:
            # 直接创建到内存
            audio_buffer = BytesIO()
            
            # 创建TTS对象并保存到内存
            tts = self.gTTS(text=text, lang=self.lang, slow=self.slow)
            tts.write_to_fp(audio_buffer)
            
            audio_buffer.seek(0)
            self.logger.debug(f"gTTS合成成功: {len(text)}字符")
            return audio_buffer
            
        except Exception as e:
            self.logger.error(f"gTTS合成失败: {e}")
            return None
    
    def _synthesize_edge_tts_thread_safe(self, text: str, output_format: str) -> Optional[BytesIO]:
        """线程安全的Edge-TTS合成（修复事件循环冲突）"""
        try:
            # 在线程池中执行异步任务
            future = self._thread_pool.submit(
                self._run_edge_tts_in_thread, text, output_format
            )
            return future.result(timeout=30)  # 30秒超时
            
        except Exception as e:
            self.logger.error(f"Edge-TTS线程执行失败: {e}")
            return None
    
    def _run_edge_tts_in_thread(self, text: str, output_format: str) -> Optional[BytesIO]:
        """在单独线程中运行Edge-TTS"""
        try:
            # 在新线程中创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self._synthesize_edge_tts_async(text, output_format)
            )
            loop.close()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Edge-TTS线程内合成失败: {e}")
            return None
    async def _synthesize_edge_tts_async(self, text: str, output_format: str = "wav") -> Optional[BytesIO]:
        """Edge-TTS合成并转换为WAV格式"""
        temp_mp3_filename = None
        temp_wav_filename = None
        try:            
            # 第一步：Edge-TTS输出MP3到临时文件
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_mp3_filename = temp_file.name
            
            communicate = self.edge_tts.Communicate(
                text, 
                voice=self.voice, 
                rate=self.rate, 
                volume=self.volume
            )
            await communicate.save(temp_mp3_filename)
            
            # 第二步：转换为WAV格式
            if output_format.lower() == 'wav':
                # 创建WAV临时文件
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:
                    temp_wav_filename = wav_file.name
                
                # 使用FFmpeg转换
                self._convert_mp3_to_wav(temp_mp3_filename, temp_wav_filename)
                final_filename = temp_wav_filename
            else:
                final_filename = temp_mp3_filename
            
            # 读取最终文件
            with open(final_filename, 'rb') as f:
                audio_data = f.read()
            
            audio_buffer = BytesIO(audio_data)
            audio_buffer.seek(0)
            
            self.logger.info(f"Edge-TTS合成成功 -> {output_format.upper()}")
            return audio_buffer
            
        except Exception as e:
            self.logger.error(f"Edge-TTS合成失败: {e}")
            return None
        finally:
            # 清理临时文件
            for filename in [temp_mp3_filename, temp_wav_filename]:
                if filename and os.path.exists(filename):
                    try:
                        os.unlink(filename)
                    except:
                        pass

    def _convert_mp3_to_wav(self, input_mp3: str, output_wav: str):
        """将MP3转换为WAV格式"""
        try:
            import ffmpeg
            
            (
                ffmpeg
                .input(input_mp3)
                .output(
                    output_wav,
                    acodec='pcm_s16le',  # 16位PCM编码
                    ar='44100',          # 44.1kHz采样率
                    ac=1                  # 单声道
                )
                .overwrite_output()
                .run(quiet=True)
            )
            
        except Exception as e:
            self.logger.error(f"MP3转WAV失败: {e}")
            raise
    
    def get_available_voices(self) -> list:
        """获取可用的语音列表"""
        if self.engine_type == "pyttsx3" and self.engine:
            voices = self.engine.getProperty('voices')
            if isinstance(voices, list):
                return [{"id": i, "name": voice.name, "id_str": voice.id} 
                       for i, voice in enumerate(voices)]
        
        elif self.engine_type == "edge_tts":
            # 线程安全的方式获取语音列表
            try:
                future = self._thread_pool.submit(self._get_edge_voices_in_thread)
                return future.result(timeout=10)
            except:
                return []
        
        return []
    
    def _get_edge_voices_in_thread(self) -> list:
        """在单独线程中获取Edge-TTS语音列表"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def async_get_voices():
                return await self.edge_tts.list_voices()
            
            voices = loop.run_until_complete(async_get_voices())
            loop.close()
            
            if isinstance(voices, list):
                return [{"name": v["ShortName"], "locale": v["Locale"]} 
                       for v in voices if "zh" in v["Locale"]]
            return []
            
        except Exception:
            return []
    
    def set_voice_properties(self, rate: Optional[float] = None, volume: Optional[float] = None):
        """设置语音属性（仅对pyttsx3有效）"""
        if self.engine_type == "pyttsx3" and self.engine:
            if rate is not None:
                self.engine.setProperty('rate', rate)
            if volume is not None:
                self.engine.setProperty('volume', volume)
    
    def __del__(self):
        """清理资源"""
        self._thread_pool.shutdown()

# 使用示例
def example_usage():
    """使用示例"""
    # 1. 使用pyttsx3（离线）
    tts_service = TTSService("pyttsx3", rate=150, volume=0.8)
    
    # 获取可用语音
    voices = tts_service.get_available_voices()
    print("可用语音:", voices)
    
    # 合成语音
    audio_buffer = tts_service.synthesize_speech("哇！你想学数学呀？太棒了！数学就像是一个超级有趣的游戏，可以帮助我们解决很多问题哦！😊 让我来给你讲一个简单的数学小故事吧！比如说，你有3个苹果🍎，你的好朋友又给了你2个苹果🍎，那么你一共有多少个苹果呢？对了，就是3+2=5个！是不是很简单？ 数学还可以帮我们做很多好玩的事情，比如： - 数一数你有多少玩具🧸 - 算一算买糖果需要多少钱🍬 - 甚至还能帮你搭积木的时候知道怎么摆更稳哦！ 如果你喜欢，我们可以一起玩个游戏：下次你吃零食的时候，数一数有几块，然后分给爸爸妈妈一些，再算算还剩多少？这样就是在做数学啦！ 记住哦，数学就像探险一样，每一次都能发现新宝藏💎。如果你有特别想学的数学知识，或者遇到不明白的地方，随时都可以来问我！我们一起加油，成为数学小达人吧！✨")
    if audio_buffer:
        # 保存到文件
        with open("output.wav", "wb") as f:
            f.write(audio_buffer.getvalue())
        print("语音合成成功并保存为output.wav")
    
    # 2. 使用Edge-TTS（在线，需要网络）
    try:
        tts_online = TTSService("edge_tts")
        audio_mp3 = tts_online.synthesize_speech("哇！你想学数学呀？太棒了！数学就像是一个超级有趣的游戏，可以帮助我们解决很多问题哦！😊 让我来给你讲一个简单的数学小故事吧！比如说，你有3个苹果🍎，你的好朋友又给了你2个苹果🍎，那么你一共有多少个苹果呢？对了，就是3+2=5个！是不是很简单？ 数学还可以帮我们做很多好玩的事情，比如： - 数一数你有多少玩具🧸 - 算一算买糖果需要多少钱🍬 - 甚至还能帮你搭积木的时候知道怎么摆更稳哦！ 如果你喜欢，我们可以一起玩个游戏：下次你吃零食的时候，数一数有几块，然后分给爸爸妈妈一些，再算算还剩多少？这样就是在做数学啦！ 记住哦，数学就像探险一样，每一次都能发现新宝藏💎。如果你有特别想学的数学知识，或者遇到不明白的地方，随时都可以来问我！我们一起加油，成为数学小达人吧！✨", "mp3")
        if audio_mp3:
            with open("output_online.mp3", "wb") as f:
                f.write(audio_mp3.getvalue())
            print("Edge-TTS语音合成成功")
    except Exception as e:
        print(f"Edge-TTS合成失败: {e}")

if __name__ == "__main__":
    example_usage()