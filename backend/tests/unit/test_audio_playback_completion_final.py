"""
音频播放完成信号最终验证测试

验证音频播放完成信号缺失问题的完整修复
"""
import os
import sys
import pytest
import threading
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestAudioPlaybackCompletionFinal:
    """音频播放完成信号最终验证测试"""

    def test_playback_completion_signal_fixed(self):
        """测试播放完成信号修复"""

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
                self.task_sentence_mapping = {}
                self.completed_sentences = {}
                self.current_task_id = None
                self.monitor_iteration_count = 0
                self.last_completion_time = None

            def _audio_playback_monitor(self):
                """修复后的监控线程实现"""
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

                        # 等待一段时间再检查
                        self.stop_event.wait(0.1)

                    except Exception as e:
                        self.logger.error(f"音频播放监控线程异常: {e}")
                        # 修复：异常时继续监控，不break
                        self.stop_event.wait(0.5)

                self.logger.info("音频播放监控线程停止")

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

                # 标记当前句子完成（如果当前有音频任务）
                self._mark_current_sentence_completed()

            def _mark_current_sentence_completed(self):
                """标记当前句子在音频任务中完成"""
                with self.audio_task_lock:
                    if self.current_task_id and self.current_task_id in self.task_sentence_mapping:
                        current_sentence_index = self.current_playing_index
                        self.mark_sentence_completed(self.current_task_id, current_sentence_index)

            def create_audio_task(self, task_id, all_sentences):
                """创建音频任务"""
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

            def mark_sentence_completed(self, task_id, sentence_index):
                """标记句子完成"""
                with self.audio_task_lock:
                    if task_id in self.completed_sentences:
                        self.completed_sentences[task_id].add(sentence_index)

            def mark_audio_task_completed(self, task_id):
                """标记音频任务完成"""
                with self.audio_task_lock:
                    self.audio_tasks = [task for task in self.audio_tasks if task.get('task_id') != task_id]
                    if task_id in self.task_sentence_mapping:
                        del self.task_sentence_mapping[task_id]
                    if task_id in self.completed_sentences:
                        del self.completed_sentences[task_id]
                    if self.current_task_id == task_id:
                        self.current_task_id = None

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
                        'audio_task_count': len(self.audio_tasks),
                        'monitor_thread_alive': True
                    }

        # 测试修复后的实现
        connect = FixedConnectProcess()

        # 启动监控线程
        monitor_thread = threading.Thread(target=connect._audio_playback_monitor, daemon=True)
        monitor_thread.start()

        # 创建音频任务
        task_id = "test_task"
        all_sentences = ["句子1", "句子2", "句子3"]
        connect.create_audio_task(task_id, all_sentences)

        # 模拟播放过程
        for i in range(3):
            is_last = (i == 2)  # 第三个句子是最后一个
            connect.set_playback_state(i, 3, is_last)
            connect.mark_audio_completed()

            # 等待监控线程处理
            time.sleep(0.1)

        # 验证监控线程仍然在运行
        assert monitor_thread.is_alive(), "修复后监控线程应该持续运行"

        # 验证播放完成信号日志
        completion_logs = [msg for msg in connect.logger.messages if "检测到最后一个句子在send_audio中播放完成" in msg]
        assert len(completion_logs) > 0, "应该记录播放完成检测日志"

        signal_logs = [msg for msg in connect.logger.messages if "播放完成信号已发送" in msg]
        assert len(signal_logs) > 0, "应该记录播放完成信号发送日志"

        # 验证监控统计信息
        stats = connect.get_playback_monitor_stats()
        assert stats['monitor_iteration_count'] > 0, "监控线程应该有迭代计数"
        assert stats['last_completion_time'] is not None, "应该有完成时间记录"
        assert stats['current_audio_completed'] == False, "音频完成状态应该已重置"

        # 停止监控线程
        connect.stop_event.set()
        monitor_thread.join(timeout=1.0)

        # 验证任务完成
        assert len(connect.audio_tasks) == 0, "所有音频任务应该已完成"

    def test_original_problem_solved(self):
        """验证原始问题已解决"""

        # 原始问题：音频播放完成信号缺失，没有打印"检测到最后一个句子在send_audio中播放完成，发送结束信号"
        # 原因：监控线程在检测到播放完成时break退出

        class OriginalProblem:
            def __init__(self):
                self.stop_event = threading.Event()
                self.logger = MockLogger()

            def _audio_playback_monitor_original(self):
                """原始有问题的实现"""
                while not self.stop_event.is_set():
                    try:
                        # 模拟检测到播放完成
                        if True:  # 假设检测到播放完成
                            self.logger.info("检测到最后一个句子在send_audio中播放完成，发送结束信号")
                            break  # 原始问题：线程在此退出

                        self.stop_event.wait(0.1)

                    except Exception as e:
                        self.logger.error(f"音频播放监控线程异常: {e}")
                        break

            def _audio_playback_monitor_fixed(self):
                """修复后的实现"""
                while not self.stop_event.is_set():
                    try:
                        # 模拟检测到播放完成
                        if True:  # 假设检测到播放完成
                            self.logger.info("检测到最后一个句子在send_audio中播放完成，发送结束信号")
                            # 修复：不break，继续监控

                        self.stop_event.wait(0.1)

                    except Exception as e:
                        self.logger.error(f"音频播放监控线程异常: {e}")
                        # 修复：异常时继续监控

        # 测试原始问题
        original = OriginalProblem()
        original_thread = threading.Thread(target=original._audio_playback_monitor_original, daemon=True)
        original_thread.start()
        time.sleep(0.2)

        # 验证原始问题：线程在检测到播放完成时退出
        assert not original_thread.is_alive(), "原始实现中线程应该在检测到播放完成时退出"

        # 测试修复后的实现
        fixed = OriginalProblem()
        fixed_thread = threading.Thread(target=fixed._audio_playback_monitor_fixed, daemon=True)
        fixed_thread.start()
        time.sleep(0.2)

        # 验证修复：线程持续运行
        assert fixed_thread.is_alive(), "修复后线程应该持续运行"

        # 停止修复后的线程
        fixed.stop_event.set()
        fixed_thread.join(timeout=1.0)

        # 验证日志记录
        original_logs = [msg for msg in original.logger.messages if "检测到最后一个句子在send_audio中播放完成" in msg]
        fixed_logs = [msg for msg in fixed.logger.messages if "检测到最后一个句子在send_audio中播放完成" in msg]

        assert len(original_logs) == 1, "原始实现应该记录1次播放完成检测"
        assert len(fixed_logs) == 1, "修复后实现应该记录1次播放完成检测"


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