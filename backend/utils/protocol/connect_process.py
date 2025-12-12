import asyncio
from concurrent.futures import ThreadPoolExecutor
import queue
import threading
import time
import uuid
from ai_core.ai_instance_repository import AiInstanceRepository
from utils.protocol.message_process import MessageProcess
from utils.protocol.send_message import SendMessage
from utils.protocol.messge_type import MessageState, MessageType
from utils.logger import Logger


# 导入agents系统
from agents.langgraph_workflow import happy_partner_graph

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

        # Agents系统状态管理
        self.user_id = None  # 用户ID
        self.session_id = None  # 会话ID
        self.agents_state = None  # Agents系统状态

        # 音频播放状态跟踪
        self.current_playing_index = 0  # 当前播放句子索引
        self.total_sentences = 0        # 总句子数
        self.is_last_sentence_playing = False  # 最后一个句子播放状态
        self.audio_playback_monitor_thread = None  # 播放监控线程
        self.playback_completion_event = threading.Event()  # 播放完成事件
        self.playback_state_lock = threading.Lock()  # 播放状态锁
        self.current_audio_completed = False  # 当前音频播放完成状态
        self.audio_completion_callbacks = []  # 音频播放完成回调列表

        # 音频任务跟踪
        self.audio_tasks = []  # 音频任务队列
        self.audio_task_lock = threading.Lock()  # 音频任务锁
        self.task_sentence_mapping = {}  # 任务-句子映射
        self.completed_sentences = {}  # 已完成的句子
        self.current_task_id = None  # 当前处理的音频任务ID

        # 性能监控
        self.monitor_iteration_count = 0  # 监控迭代计数
        self.last_completion_time = None  # 上次完成时间

        # 句子信息现在通过音频队列传递，不再需要单独的句子信息队列

    
    def _audio_send_thread(self):
        """音频发送线程，通过事件控制线程运行，并释放资源"""
        while not self.stop_event.is_set():
            try:
                # 获取集成音频任务：包含future和句子信息
                integrated_task = self.audio_send_queue.get(timeout=1)
            except queue.Empty:
                self.logger.debug("音频发送队列为空")
                continue

            if integrated_task is None:
                continue

            try:
                # 解构集成任务
                future, sentence_info = integrated_task

                # 获取音频数据
                opus_data, duration, text = future.result(timeout=10) # 等待结果，超时10秒，等待处理完成， future只是占位符

                try:
                    # 提交协程处理，在主线程中处理
                    if sentence_info:
                        # 获取任务ID（如果存在）
                        task_id = sentence_info.get('task_id')
                        future_1 = asyncio.run_coroutine_threadsafe(
                            SendMessage.send_audio(
                                self, self.config, opus_data, text,
                                sentence_info['current_index'],
                                sentence_info['total_sentences'],
                                sentence_info['is_last_sentence'],
                                task_id
                            ), self.loop
                        )
                    else:
                        # 如果没有句子信息，使用默认参数
                        future_1 = asyncio.run_coroutine_threadsafe(
                            SendMessage.send_audio(self, self.config, opus_data, text), self.loop
                        )
                    future_1.result()

                except Exception as e:
                    self.logger.error(f"发送消息到前端异常: {e}")

            except Exception as e:
                import traceback
                self.logger.error(f"音频任务处理异常: {e}")
                self.logger.error(traceback.format_exc())

    def _initialize_agents_state(self):
        """初始化Agents系统状态"""
        try:
            # 生成用户ID和会话ID
            self.user_id = f"user_{uuid.uuid4().hex[:8]}"
            self.session_id = str(uuid.uuid4())

            # 初始化Agents状态
            self.agents_state = {
                "user_id": self.user_id,
                "session_id": self.session_id,
                "conversation_history": [],
                "user_preferences": {},
                "last_processed_time": None
            }
            self.logger.info(f"Agents系统状态初始化完成 - 用户ID: {self.user_id}, 会话ID: {self.session_id}")
        except Exception as e:
            self.logger.error(f"Agents系统状态初始化失败: {e}")
            # 设置默认状态
            self.agents_state = {
                "user_id": "default_user",
                "session_id": str(uuid.uuid4()),
                "conversation_history": [],
                "user_preferences": {},
                "last_processed_time": None
            }

    def _cleanup_agents_state(self):
        """清理Agents系统状态"""
        try:
            if self.agents_state:
                # 保存会话历史或执行其他清理操作
                self.logger.info(f"清理Agents系统状态 - 用户ID: {self.user_id}")
                self.agents_state = None
                self.user_id = None
                self.session_id = None
        except Exception as e:
            self.logger.error(f"Agents系统状态清理失败: {e}")

    def _clear_queue(self, q:queue.Queue):
        """清除队列"""
        if not q: return
        while not q.empty():
            try:
                q.get_nowait()
            except queue.Empty:
                continue
        q.queue.clear()


    def set_playback_state(self, current_index, total_sentences, is_last_sentence):
        """
        设置音频播放状态

        Args:
            current_index: 当前播放句子索引
            total_sentences: 总句子数
            is_last_sentence: 是否是最后一个句子
        """
        with self.playback_state_lock:
            self.current_playing_index = current_index
            self.total_sentences = total_sentences
            self.is_last_sentence_playing = is_last_sentence
            self.current_audio_completed = False  # 重置音频完成状态

            self.logger.info(f"设置播放状态: 当前句子 {current_index+1}/{total_sentences}, 最后一个句子: {is_last_sentence}")

    def mark_audio_completed(self):
        """标记当前音频播放完成"""
        with self.playback_state_lock:
            self.current_audio_completed = True

            if self.is_last_sentence_playing and self.current_playing_index == self.total_sentences - 1:
                self.logger.info("最后一个句子在send_audio中播放完成")
            else:
                self.logger.info(f"非最后一个句子音频播放完成: 句子 {self.current_playing_index+1}/{self.total_sentences}")

            # 触发所有回调
            for callback in self.audio_completion_callbacks:
                try:
                    callback()
                except Exception as e:
                    self.logger.error(f"音频完成回调执行失败: {e}")

        # 标记当前句子完成（如果当前有音频任务）
        self._mark_current_sentence_completed()

    def _mark_current_sentence_completed(self):
        """标记当前句子在音频任务中完成"""
        with self.audio_task_lock:
            if self.current_task_id and self.current_task_id in self.task_sentence_mapping:
                # 获取当前句子的索引
                current_sentence_index = self.current_playing_index

                # 标记句子完成
                self.mark_sentence_completed(self.current_task_id, current_sentence_index)

                self.logger.debug(f"标记句子完成: 任务 {self.current_task_id}, 句子 {current_sentence_index}")
            else:
                self.logger.debug("没有当前音频任务，跳过句子完成标记")

    def add_audio_completion_callback(self, callback):
        """添加音频播放完成回调"""
        with self.playback_state_lock:
            self.audio_completion_callbacks.append(callback)

    def add_audio_task(self, task_info):
        """
        添加音频任务

        Args:
            task_info: 音频任务信息，包含任务ID、音频数据、文本等
        """
        with self.audio_task_lock:
            self.audio_tasks.append(task_info)
            self.logger.info(f"添加音频任务: {task_info.get('task_id', 'unknown')}")

    def mark_audio_task_completed(self, task_id):
        """
        标记音频任务完成

        Args:
            task_id: 音频任务ID
        """
        with self.audio_task_lock:
            # 从任务队列中移除完成的任务
            self.audio_tasks = [task for task in self.audio_tasks if task.get('task_id') != task_id]

            # 清理映射和完成状态
            if task_id in self.task_sentence_mapping:
                del self.task_sentence_mapping[task_id]
            if task_id in self.completed_sentences:
                del self.completed_sentences[task_id]

            # 如果当前任务完成，清空当前任务ID
            if self.current_task_id == task_id:
                self.current_task_id = None

            self.logger.info(f"音频任务 {task_id} 完成，剩余任务数: {len(self.audio_tasks)}")

    def get_audio_task_count(self):
        """获取当前音频任务数量"""
        with self.audio_task_lock:
            return len(self.audio_tasks)

    def create_audio_task(self, task_id, all_sentences):
        """
        创建音频任务

        Args:
            task_id: 任务ID
            all_sentences: 所有句子列表
        """
        with self.audio_task_lock:
            task_info = {
                'task_id': task_id,
                'sentences': all_sentences,
                'completed_sentences': set(),
                'status': 'processing',
                'created_time': time.time()
            }
            self.audio_tasks.append(task_info)
            self.task_sentence_mapping[task_id] = all_sentences
            self.completed_sentences[task_id] = set()
            self.current_task_id = task_id

            self.logger.info(f"创建音频任务: {task_id}, 包含 {len(all_sentences)} 个句子")

    def mark_sentence_completed(self, task_id, sentence_index):
        """
        标记句子完成

        Args:
            task_id: 任务ID
            sentence_index: 句子索引
        """
        with self.audio_task_lock:
            if task_id in self.completed_sentences:
                self.completed_sentences[task_id].add(sentence_index)

                # 检查任务是否全部完成
                if task_id in self.task_sentence_mapping:
                    total_sentences = len(self.task_sentence_mapping[task_id])
                    completed_count = len(self.completed_sentences[task_id])

                    self.logger.debug(f"任务 {task_id} 句子完成: {completed_count}/{total_sentences}")

                    # 如果所有句子都完成，标记任务完成
                    if completed_count == total_sentences:
                        self.mark_audio_task_completed(task_id)
                        self.logger.info(f"音频任务 {task_id} 全部完成")

    def get_audio_task_status(self, task_id):
        """获取音频任务状态"""
        with self.audio_task_lock:
            if task_id not in self.task_sentence_mapping:
                return None

            total_sentences = len(self.task_sentence_mapping[task_id])
            completed_count = len(self.completed_sentences.get(task_id, set()))

            return {
                'task_id': task_id,
                'total_sentences': total_sentences,
                'completed_sentences': completed_count,
                'progress': completed_count / total_sentences if total_sentences > 0 else 0,
                'status': 'completed' if completed_count == total_sentences else 'processing'
            }

    def get_playback_monitor_stats(self):
        """获取播放监控统计信息"""
        with self.playback_state_lock:
            return {
                'monitor_iteration_count': self.monitor_iteration_count,
                'last_completion_time': self.last_completion_time,
                'current_playing_index': self.current_playing_index,
                'total_sentences': self.total_sentences,
                'is_last_sentence_playing': self.is_last_sentence_playing,
                'current_audio_completed': self.current_audio_completed,
                'audio_task_count': self.get_audio_task_count(),
                'monitor_thread_alive': (self.audio_playback_monitor_thread and
                                       self.audio_playback_monitor_thread.is_alive())
            }


    def start_audio_playback_monitor(self):
        """启动音频播放监控线程"""
        if self.audio_playback_monitor_thread is None or not self.audio_playback_monitor_thread.is_alive():
            self.audio_playback_monitor_thread = threading.Thread(
                target=self._audio_playback_monitor,
                daemon=True
            )
            self.audio_playback_monitor_thread.start()
            self.logger.info("音频播放监控线程已启动")

    def _audio_playback_monitor(self):
        """音频播放监控线程"""
        self.logger.info("音频播放监控线程启动")

        while not self.stop_event.is_set():
            try:
                self.monitor_iteration_count += 1

                # 检查是否是最后一个句子且在send_audio中播放完成
                with self.playback_state_lock:
                    is_last_sentence = self.is_last_sentence_playing
                    current_index = self.current_playing_index
                    total_sentences = self.total_sentences
                    current_audio_completed = self.current_audio_completed

                # 如果是最后一个句子且在send_audio中播放完成，则发送结束信号
                if (is_last_sentence and
                    current_index == total_sentences - 1 and
                    current_audio_completed):
                    self.logger.info("检测到最后一个句子在send_audio中播放完成，发送结束信号")
                    self._send_playback_completion_signal()
                    # 修复：发送信号后重置状态，继续监控
                    with self.playback_state_lock:
                        self.current_audio_completed = False
                    self.last_completion_time = time.time()

                # 性能优化：每100次迭代记录一次调试信息
                if self.monitor_iteration_count % 100 == 0:
                    self.logger.debug(f"音频播放监控线程运行中 - 迭代次数: {self.monitor_iteration_count}")

                # 等待一段时间再检查
                self.stop_event.wait(0.5)

            except Exception as e:
                self.logger.error(f"音频播放监控线程异常: {e}")
                # 修复：异常时继续监控，不break
                # 等待一段时间后继续，避免快速循环
                self.stop_event.wait(1.0)

        self.logger.info("音频播放监控线程停止")

    def _send_playback_completion_signal(self):
        """发送播放完成信号"""
        try:
            # 检查WebSocket连接是否仍然活跃
            if not self.websocket:
                self.logger.warning("WebSocket连接已断开，无法发送播放完成信号")
                return

            # 直接发送TTS结束信号，使用较短的超时时间
            future = asyncio.run_coroutine_threadsafe(
                SendMessage.send_audio(self, self.config, None, "播放完成"),
                self.loop
            )

            # 使用较短的超时时间（5秒）
            future.result(timeout=5)
            self.logger.info("播放完成信号已发送")

        except TimeoutError:
            self.logger.error("发送播放完成信号超时，可能连接已断开")
        except Exception as e:
            self.logger.error(f"发送播放完成信号异常: {e}")
            import traceback
            self.logger.error(f"详细错误信息: {traceback.format_exc()}")


    # 处理连接
    async def connect(self, websocket):
        self.logger.info("开始处理连接")
        self.websocket = websocket
        self.session_id = uuid.uuid4().hex

        # 初始化Agents系统状态
        self._initialize_agents_state()

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

    async def close(self):
        """处理连接关闭，资源清理"""
        self.logger.info("连接关闭")

        # 清理Agents系统状态
        self._cleanup_agents_state()


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

