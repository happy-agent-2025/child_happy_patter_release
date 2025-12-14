import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import re
import time
import traceback
import uuid
from utils.protocol.messge_type import MessageState, MessageType
from utils.protocol.send_message import SendMessage
from utils.Dialogue import Dialogue
from utils.logger import Logger
from utils.sentence_splitter import SmartSentenceSplitter


# 导入agents系统
from agents.langgraph_workflow import happy_partner_graph

# 性能优化：简单的响应缓存
class ResponseCache:
    """响应缓存类"""
    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size
        self.access_count = {}

    def get(self, key: str) -> str:
        """获取缓存响应"""
        if key in self.cache:
            self.access_count[key] = self.access_count.get(key, 0) + 1
            return self.cache[key]
        return None

    def set(self, key: str, value: str):
        """设置缓存响应"""
        if len(self.cache) >= self.max_size:
            # 移除最少使用的缓存项
            if self.access_count:
                min_key = min(self.access_count, key=self.access_count.get)
                del self.cache[min_key]
                del self.access_count[min_key]
        self.cache[key] = value
        self.access_count[key] = 1

# 全局缓存实例
_response_cache = ResponseCache()

TAG = __name__

class MessageProcess:
    def __init__(self, config, connect):
        self.config = config
        self.connect = connect
        self.ai = connect.ai
        self.logger = Logger().log_init(TAG)
        self.asr_opus_datas = []
        self.client_audio_stop = False
        self.text = ""
        self.sendMessage = SendMessage()
        self.dialogue = Dialogue()
        self.vad = self.ai.vad
        self.is_processing = False
        self.sentence_splitter = SmartSentenceSplitter()

        # 音频传输状态管理
        self.is_audio_transmitting = False  # 音频传输状态标志
        self.audio_transmission_lock = asyncio.Lock()  # 音频传输锁

        
    async def process_message(self, message):
        """消息路由"""
        if isinstance(message, str):
            await self.text_message(message)
        elif isinstance(message, bytes):
            await self.bytes_message(message)
        else:
            self.logger.error("Invalid message type: %s", type(message))
    
    # 将音频数据缓存下来，后面开始进行opus解码并转成文字
    async def bytes_message(self, message):
        """处理二进制消息"""
        # 检查是否正在处理或音频传输中
        if self.is_processing or self.is_audio_transmitting:
            self.logger.debug("系统繁忙，跳过当前音频处理")
            return


        # is_no_speech表示没有说话，表示一句话结束，is_has_speech表示有说话
        is_no_speech, is_has_speech = self.vad.is_no_speech(self.connect, message)
        if is_no_speech:
            self.logger.info(f"一句话结束...")
            self.client_audio_stop = True
            is_has_speech = True # 有话，准备往下

        # 如果当前没有语音活动，则将当前时间保存为无语音活动时，保留最后的10个字节
        if not is_has_speech:
            self.asr_opus_datas.append(message)
            self.asr_opus_datas = self.asr_opus_datas[-10:] # 节省静音的数据
            return

        self.asr_opus_datas.append(message) # 缓存opus数据，直到收到stop消息才能进行播放处理
        if not self.client_audio_stop:
            return

        self.client_audio_stop = False  # 停止音频处理
        if len(self.asr_opus_datas) < 15:
            return

        self.is_processing = True
        self.connect.connect_thread_pool.submit(self.start_chat, self.asr_opus_datas) # 提交任务
    
    def is_only_punctuation(self,text):
        """检查字符串是否仅由标点符号组成（无字母、数字、字母等）"""
        if not text or not isinstance(text, str):
            return True  # 空或非字符串视为无效
        cleaned = re.sub(r'[\w\s]', '', text, flags=re.UNICODE)  # \w 匹配字母数字汉字，\s 匹配空白
        return cleaned == text  # 如果只剩标点，返回 True
    
    # 开始处理音频数据，并把消息返回给客户端
    async def _process_with_agents(self, user_text: str) -> str:
        """使用agents系统处理用户消息"""
        try:
            # 检查缓存
            cache_key = f"{user_text}"  # 简单的文本作为缓存键
            cached_response = _response_cache.get(cache_key)
            if cached_response:
                self.logger.info(f"从缓存获取响应，长度: {len(cached_response)} 字符")
                return cached_response

            # 使用LangGraph工作流处理消息
            user_id = getattr(self.connect, 'user_id', 'default_user')
            session_id = getattr(self.connect, 'session_id', str(uuid.uuid4()))

            self.logger.info(f"开始Agents系统处理 - 用户ID: {user_id}, 会话ID: {session_id}")

            result = await happy_partner_graph.process_message(
                user_id=user_id,
                content=user_text,
                session_id=session_id
            )

            response = result.get("response", "抱歉，我无法回答这个问题。")
            self.logger.info(f"Agents系统处理完成，响应长度: {len(response)} 字符")

            # 缓存响应
            _response_cache.set(cache_key, response)

            return response

        except asyncio.TimeoutError:
            self.logger.error("Agents系统处理超时")
            return self._fallback_to_llm(user_text)
        except Exception as e:
            self.logger.error(f"Agents系统处理失败: {e}")
            # 降级到原有LLM调用
            return self._fallback_to_llm(user_text)

    def _fallback_to_llm(self, user_text: str) -> str:
        """降级到原有LLM调用"""
        try:
            self.dialogue.put_user(user_text)
            response = self.ai.llm.generate_response(self.dialogue.get_dialogue(), self.connect.session_id)
            assistant_text = ''
            for chunk in response:
                assistant_text += chunk
            self.dialogue.put_assistant(assistant_text)
            return assistant_text
        except Exception as e:
            self.logger.error(f"LLM降级处理失败: {e}")
            return "抱歉，系统暂时无法处理您的请求。"

    def start_chat(self, message):
        """开始聊天 - 集成agents系统"""
        
        processing_text = ""
        is_only_wake_up = False
        if isinstance(message, str):
            is_only_wake_up = True
            processing_text = message
            self.logger.info(f"传入的文本: {processing_text}")
        else:
            is_only_wake_up = False
            processing_text = self.ai.asr.opus_data_to_text(message)
            """检查文本是否只包含符号（不含有效文字）"""
            if self.is_only_punctuation(processing_text):
                self.logger.info(f"识别到的垃圾文本: {processing_text}")
                future = self.connect.connect_thread_pool.submit(self.ai.tts.text_to_opus_data, None)
                sentence_info = {
                    'current_index': 0,
                    'total_sentences': 1,
                    'is_last_sentence': True,
                }
                self.connect.enqueue_audio_task(future, sentence_info)
                self.is_processing = False
                return
            self.logger.info(f"识别结果: {processing_text}")

        # 发送用户文本到前端
        try:
            future = asyncio.run_coroutine_threadsafe(
                SendMessage._send_stt_text(self.connect, processing_text),
                self.connect.loop
            )
            future.result(timeout=5)
        except Exception as e:
            self.logger.error(f"websocket 发送异常{e}")
         
        if not is_only_wake_up:
            # 使用agents系统处理消息
            try:
                # 在现有线程池中运行异步的agents处理
                future = asyncio.run_coroutine_threadsafe(
                    self._process_with_agents(processing_text),
                    self.connect.loop
                )
                assistant_text = future.result(timeout=30)  # 设置30秒超时
            except Exception as e:
                self.logger.error(f"Agents系统处理超时或失败: {e}")
                # 降级到原有LLM调用
                assistant_text = self._fallback_to_llm(processing_text)
        else:
            assistant_text = processing_text

        # 处理响应文本流式输出
        iot_messages = []

        # 设置音频传输状态
        self.is_audio_transmitting = True

        try:
            # 使用智能分句器将长文本拆分成所有完整句子
            all_sentences = self.sentence_splitter.split_all_sentences(assistant_text)

            self.logger.info(f"智能分句结果: 共{len(all_sentences)}个句子")

            # 为本轮响应生成任务ID
            task_id = f"task_{uuid.uuid4().hex[:8]}"

            # 处理每个句子
            for i, sentence in enumerate(all_sentences):
                if len(sentence.strip()) > 0 and not self.is_only_punctuation(sentence):
                    is_last_sentence = (i == len(all_sentences) - 1)

                    # 创建句子信息
                    sentence_info = {
                        'current_index': i,
                        'total_sentences': len(all_sentences),
                        'is_last_sentence': is_last_sentence,
                        'task_id': task_id,
                    }

                    self.logger.info(f"完整句子[{i+1}/{len(all_sentences)}]: {sentence}")
                    future = self.connect.connect_thread_pool.submit(self.ai.tts.text_to_opus_data, sentence)

                    self.connect.enqueue_audio_task(future, sentence_info)


        except Exception as e:
            self.logger.error(f"音频处理错误: {e}")
        finally:
            # 确保状态被正确重置
            self.is_processing = False
            self.is_audio_transmitting = False

    # 获取完整的句子
    def get_complete_sentence(self, text_buffer: list):
        """
        使用智能分句器从文本缓冲区中获取完整的句子

        Args:
            text_buffer: 文本缓冲区列表

        Returns:
            tuple: (remaining_buffer, complete_sentence)
        """
        return self.sentence_splitter.get_complete_sentence(text_buffer)

    async def text_message(self, message):
        """处理文本消息"""
        self.logger.info(">>>> 接收到文本消息: " + message)
        try:
            msg_json = json.loads(message) # 加载JSON消息
            if msg_json["type"] == MessageType.HELLO.value:
                await self.sendMessage.send_hello_message(self.connect, self.config)
                
            if msg_json["type"] == MessageType.LISTEN.value:
                if msg_json["state"] == MessageState.DETECT.value:
                    # 处理前端过来的消息，前端连接之后，发文本消息到后端进行处理
                    if "text" in msg_json:
                        text = msg_json["text"]
                        # 检查是否正在处理或音频传输中
                        if not (self.is_processing or self.is_audio_transmitting) and text == "你好小智":
                            self.connect.connect_thread_pool.submit(self.start_chat, "你好，有什么可以帮助您的吗？") # 提交任务，发送语音消息
                        else:
                            self.logger.info(f"文本消息处理:{self.is_processing}-{self.is_audio_transmitting}-{text}")
                
                # 处理开始录音，把上次的声音清除
                if msg_json["state"] == MessageState.START.value:
                    self.text = ""
                    self.client_audio_stop = False
                    self.asr_opus_datas.clear()
                
                # 当前端发送语音消息发送完毕的时候，开始做llm + tts处理 + 发送消息给到前端
                if msg_json["state"] == MessageState.STOP.value:
                    self.client_audio_stop = True
                    # if len(self.asr_opus_datas) > 0:
                    #     await self.bytes_message(b"")
   
        except json.JSONDecodeError as e:
            self.logger.error("JSON 解析错误: " + str(e))
        except Exception as e:
            self.logger.error("处理文本消息时出错: " + str(e))
            traceback.print_exc()
            
    
