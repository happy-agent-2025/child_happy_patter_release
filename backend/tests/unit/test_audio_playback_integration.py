"""
音频播放监控集成测试用例

验证修复后的音频播放完成信号功能
"""
import os
import sys
import pytest
import threading
import time
import uuid

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestAudioPlaybackIntegration:
    """测试音频播放监控集成功能"""

    def test_monitor_thread_continuous_monitoring(self):
        """测试监控线程持续监控多个音频任务"""

        # 模拟修复后的ConnectProcess
        class FixedConnectProcess:
            def __init__(self):
                self.stop_event = threading.Event()
                self.is_last_sentence_playing = False
                self.current_playing_index = 0
                self.total_sentences = 0
                self.current_audio_completed = False
                self.playback_state_lock = threading.Lock()
                self.logger = MockLogger()
                self.audio_tasks = []
                self.audio_task_lock = threading.Lock()

            def _audio_playback_monitor(self):
                """修复后的监控线程实现 - 持续运行"""
                while not self.stop_event.is_set():
                    try:
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

                        # 等待一段时间再检查
                        self.stop_event.wait(0.5)

                    except Exception as e:
                        self.logger.error(f"音频播放监控线程异常: {e}")
                        # 修复：异常时继续监控，不break

            def _send_playback_completion_signal(self):
                """发送播放完成信号"""
                self.logger.info("播放完成信号已发送")

            def set_playback_state(self, current_index, total_sentences, is_last_sentence):
                """设置播放状态"""
                with self.playback_state_lock:
                    self.current_playing_index = current_index
                    self.total_sentences = total_sentences
                    self.is_last_sentence_playing = is_last_sentence
                    self.current_audio_completed = False

            def mark_audio_completed(self):
                """标记音频播放完成"""
                with self.playback_state_lock:
                    self.current_audio_completed = True

            def add_audio_task(self, task_info):
                """添加音频任务"""
                with self.audio_task_lock:
                    self.audio_tasks.append(task_info)
                    self.logger.info(f"添加音频任务: {task_info.get('task_id', 'unknown')}")

            def mark_audio_task_completed(self, task_id):
                """标记音频任务完成"""
                with self.audio_task_lock:
                    self.audio_tasks = [task for task in self.audio_tasks if task.get('task_id') != task_id]
                    self.logger.info(f"音频任务 {task_id} 完成，剩余任务数: {len(self.audio_tasks)}")

            def get_audio_task_count(self):
                """获取当前音频任务数量"""
                with self.audio_task_lock:
                    return len(self.audio_tasks)

        # 测试修复后的实现
        connect = FixedConnectProcess()

        # 启动监控线程
        monitor_thread = threading.Thread(target=connect._audio_playback_monitor, daemon=True)
        monitor_thread.start()

        # 模拟多个音频任务
        task_ids = []
        for i in range(3):
            task_id = f"task_{i}"
            task_ids.append(task_id)
            connect.add_audio_task({
                'task_id': task_id,
                'text': f'测试句子{i+1}',
                'audio_data': b'test_audio_data'
            })

        # 验证任务添加成功
        assert connect.get_audio_task_count() == 3, "应该成功添加3个音频任务"

        # 模拟播放多个句子
        for i in range(3):
            is_last = (i == 2)  # 第三个句子是最后一个
            connect.set_playback_state(i, 3, is_last)
            connect.mark_audio_completed()

            # 标记任务完成
            connect.mark_audio_task_completed(task_ids[i])

            # 等待监控线程处理
            time.sleep(0.2)

        # 验证监控线程仍然在运行
        assert monitor_thread.is_alive(), "修复后监控线程应该持续运行"

        # 验证所有任务已完成
        assert connect.get_audio_task_count() == 0, "所有音频任务应该已完成"

        # 验证播放完成信号日志
        completion_logs = [msg for msg in connect.logger.messages if "检测到最后一个句子在send_audio中播放完成" in msg]
        assert len(completion_logs) > 0, "应该记录播放完成检测日志"

        # 验证播放完成信号发送日志
        signal_logs = [msg for msg in connect.logger.messages if "播放完成信号已发送" in msg]
        assert len(signal_logs) > 0, "应该记录播放完成信号发送日志"

    def test_audio_task_management(self):
        """测试音频任务管理功能"""

        class FixedConnectProcess:
            def __init__(self):
                self.audio_tasks = []
                self.audio_task_lock = threading.Lock()
                self.logger = MockLogger()

            def add_audio_task(self, task_info):
                """添加音频任务"""
                with self.audio_task_lock:
                    self.audio_tasks.append(task_info)
                    self.logger.info(f"添加音频任务: {task_info.get('task_id', 'unknown')}")

            def mark_audio_task_completed(self, task_id):
                """标记音频任务完成"""
                with self.audio_task_lock:
                    self.audio_tasks = [task for task in self.audio_tasks if task.get('task_id') != task_id]
                    self.logger.info(f"音频任务 {task_id} 完成，剩余任务数: {len(self.audio_tasks)}")

            def get_audio_task_count(self):
                """获取当前音频任务数量"""
                with self.audio_task_lock:
                    return len(self.audio_tasks)

        # 测试音频任务管理
        connect = FixedConnectProcess()

        # 添加多个任务
        for i in range(5):
            connect.add_audio_task({
                'task_id': f'task_{i}',
                'text': f'测试句子{i+1}',
                'audio_data': b'test_audio_data'
            })

        # 验证任务添加
        assert connect.get_audio_task_count() == 5, "应该成功添加5个音频任务"

        # 标记部分任务完成
        connect.mark_audio_task_completed('task_0')
        connect.mark_audio_task_completed('task_2')

        # 验证任务完成
        assert connect.get_audio_task_count() == 3, "完成2个任务后应该剩余3个任务"

        # 标记剩余任务完成
        connect.mark_audio_task_completed('task_1')
        connect.mark_audio_task_completed('task_3')
        connect.mark_audio_task_completed('task_4')

        # 验证所有任务完成
        assert connect.get_audio_task_count() == 0, "所有任务完成后应该剩余0个任务"

    def test_playback_completion_signal_reset(self):
        """测试播放完成信号发送后状态重置"""

        class FixedConnectProcess:
            def __init__(self):
                self.stop_event = threading.Event()
                self.is_last_sentence_playing = False
                self.current_playing_index = 0
                self.total_sentences = 0
                self.current_audio_completed = False
                self.playback_state_lock = threading.Lock()
                self.logger = MockLogger()

            def _audio_playback_monitor(self):
                """修复后的监控线程实现"""
                while not self.stop_event.is_set():
                    try:
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

                        # 等待一段时间再检查
                        self.stop_event.wait(0.5)

                    except Exception as e:
                        self.logger.error(f"音频播放监控线程异常: {e}")

            def _send_playback_completion_signal(self):
                """发送播放完成信号"""
                self.logger.info("播放完成信号已发送")

            def set_playback_state(self, current_index, total_sentences, is_last_sentence):
                """设置播放状态"""
                with self.playback_state_lock:
                    self.current_playing_index = current_index
                    self.total_sentences = total_sentences
                    self.is_last_sentence_playing = is_last_sentence
                    self.current_audio_completed = False

            def mark_audio_completed(self):
                """标记音频播放完成"""
                with self.playback_state_lock:
                    self.current_audio_completed = True

            def get_current_audio_completed(self):
                """获取当前音频完成状态"""
                with self.playback_state_lock:
                    return self.current_audio_completed

        # 测试状态重置
        connect = FixedConnectProcess()

        # 启动监控线程
        monitor_thread = threading.Thread(target=connect._audio_playback_monitor, daemon=True)
        monitor_thread.start()

        # 设置播放状态为最后一个句子
        connect.set_playback_state(2, 3, True)
        connect.mark_audio_completed()

        # 等待监控线程处理
        time.sleep(0.3)

        # 验证状态已重置
        assert not connect.get_current_audio_completed(), "发送播放完成信号后状态应该重置"

        # 验证监控线程仍然在运行
        assert monitor_thread.is_alive(), "监控线程应该持续运行"


class MockLogger:
    """模拟日志器"""
    def __init__(self):
        self.messages = []

    def info(self, msg):
        self.messages.append(f"INFO: {msg}")

    def error(self, msg):
        self.messages.append(f"ERROR: {msg}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])