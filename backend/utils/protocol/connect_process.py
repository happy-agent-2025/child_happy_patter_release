import asyncio
from concurrent.futures import ThreadPoolExecutor
import queue
import threading
import uuid
from ai_core.ai_instance_repository import AiInstanceRepository
from utils.protocol.message_process import MessageProcess
from utils.protocol.send_message import SendMessage
from utils.logger import Logger

TAG = __name__

# 处理连接之后的内容
class ConnectProcess:
    def __init__(self, config, ai:AiInstanceRepository):
        self.websocket = None
        self.config = config
        self.ai = ai
        self.logger = Logger().log_init(TAG)
        self.connect_thread_pool = ThreadPoolExecutor(max_workers=10)
        self.audio_send_queue = queue.Queue()  #  音频发送队列
        self.loop = asyncio.get_event_loop() # 获取事件循环
        self.audio_send_thread = None # 音频发送线程
        self.stop_event = threading.Event() # 停止事件，事件管理当前线程
    
    def _audio_send_thread(self):
        """音频发送线程，通过事件控制线程运行，并释放资源"""
        while not self.stop_event.is_set():
            
            try:
                future = self.audio_send_queue.get(timeout=1)
            except queue.Empty:
                self.logger.debug("音频发送队列为空")
                continue
            
            if future is None:
                continue
            
            opus_data, duration, text = future.result(timeout=10) # 等待结果，超时10秒，等待处理完成， future只是占位符
            
            try: 
                # 提交协程处理，在主线程中处理
                future_1 = asyncio.run_coroutine_threadsafe(
                    SendMessage.send_audio(self, self.config, opus_data, text), self.loop
                )
                future_1.result()
            except Exception as e:
                self.logger.error(f"发送消息到前端异常: {e}")
    
    async def close(self):
        """处理连接关闭，资源清理"""
        self.logger.info("连接关闭")
        if self.stop_event:
            self.stop_event.set()
            
        # 关闭线程
        if self.connect_thread_pool:
            self.connect_thread_pool.shutdown(wait=False, cancel_futures=True)
            self.connect_thread_pool = None
        
        # 清除队列
        self._clear_queue(self.audio_send_queue)
        # 关闭websocket
        if self.websocket:
            await self.websocket.close()
        self.logger.info("连接关闭完成，资源释放完成")
    
    def _clear_queue(self, q:queue.Queue):
        """清除队列"""
        if not q: return
        while not q.empty():
            try:
                q.get_nowait()
            except queue.Empty:
                continue
        q.queue.clear()
    
    # 处理连接
    async def connect(self, websocket):
        self.logger.info("开始处理连接")
        self.websocket = websocket
        self.session_id = uuid.uuid4().hex
        message_process = MessageProcess(self.config, self)
        
        # 创建新线程
        self.audio_send_thread = threading.Thread(target=self._audio_send_thread, daemon = True)
        self.audio_send_thread.start() # 启动音频发送线程

        try:
            # 循环处理消息
            while True:
                try:
                    message = await self.websocket.recv()
                    await message_process.process_message(message)
                except Exception as e:
                    self.logger.info("客户端断开连接", e)
                    break  # 退出循环，结束连接处理
        except Exception as e:
            self.logger.error("处理消息异常: " + str(e))
        finally:
            # 不管结束正常还是异常都会走下面
            await self.close()
