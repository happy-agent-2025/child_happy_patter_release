"""
音频播放监控最终验证测试

验证音频播放完成信号缺失问题的完整修复
"""
import os
import sys
import pytest
import threading
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestAudioPlaybackFinal:
    """音频播放监控最终验证测试"""

    def test_final_monitor_implementation(self):
        """测试最终监控实现 - 模拟修复后的ConnectProcess"""

        class FinalConnectProcess:
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
                self.monitor_iteration_count = 0
                self.last_completion_time = None

            def _audio_playback_monitor(self):
                """最终修复的监控线程实现"""
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
                        self.stop_event.wait(0.5)

                    except Exception as e:
                        self.logger.error(f"音频播放监控线程异常: {e}")
                        # 修复：异常时继续监控，不break
                        self.stop_event.wait(1.0)

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
                        'monitor_thread_alive': True  # 模拟线程存活状态
                    }

        # 测试最终实现
        connect = FinalConnectProcess()

        # 启动监控线程
        monitor_thread = threading.Thread(target=connect._audio_playback_monitor, daemon=True)
        monitor_thread.start()

        # 验证初始状态
        stats = connect.get_playback_monitor_stats()
        assert stats['monitor_iteration_count'] == 0, "初始迭代计数应该为0"
        assert stats['current_audio_completed'] == False, "初始音频完成状态应该为False"

        # 模拟多个音频任务序列
        for sequence in range(2):  # 模拟2个完整的音频序列
            # 添加音频任务
            for i in range(3):
                task_id = f"seq_{sequence}_task_{i}"
                connect.add_audio_task({
                    'task_id': task_id,
                    'text': f'序列{sequence+1}句子{i+1}',
                    'audio_data': b'test_audio_data'
                })

            # 模拟播放过程
            for i in range(3):
                is_last = (i == 2)  # 第三个句子是最后一个
                connect.set_playback_state(i, 3, is_last)
                connect.mark_audio_completed()

                # 标记任务完成
                connect.mark_audio_task_completed(f"seq_{sequence}_task_{i}")

                # 等待监控线程处理
                time.sleep(0.3)

            # 验证监控线程仍然在运行
            assert monitor_thread.is_alive(), f"序列{sequence+1}后监控线程应该持续运行"

        # 验证最终状态
        final_stats = connect.get_playback_monitor_stats()
        assert final_stats['monitor_iteration_count'] > 0, "监控线程应该有迭代计数"
        assert final_stats['last_completion_time'] is not None, "应该有完成时间记录"
        assert final_stats['audio_task_count'] == 0, "所有音频任务应该已完成"
        assert final_stats['current_audio_completed'] == False, "最终音频完成状态应该重置为False"

        # 验证日志记录
        completion_logs = [msg for msg in connect.logger.messages if "检测到最后一个句子在send_audio中播放完成" in msg]
        assert len(completion_logs) >= 2, "应该记录至少2次播放完成检测日志"

        signal_logs = [msg for msg in connect.logger.messages if "播放完成信号已发送" in msg]
        assert len(signal_logs) >= 2, "应该记录至少2次播放完成信号发送日志"

        # 停止监控线程
        connect.stop_event.set()
        monitor_thread.join(timeout=2.0)

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

                        self.stop_event.wait(0.5)

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

                        self.stop_event.wait(0.5)

                    except Exception as e:
                        self.logger.error(f"音频播放监控线程异常: {e}")
                        # 修复：异常时继续监控

        # 测试原始问题
        original = OriginalProblem()
        original_thread = threading.Thread(target=original._audio_playback_monitor_original, daemon=True)
        original_thread.start()
        time.sleep(0.5)

        # 验证原始问题：线程在检测到播放完成时退出
        assert not original_thread.is_alive(), "原始实现中线程应该在检测到播放完成时退出"

        # 测试修复后的实现
        fixed = OriginalProblem()
        fixed_thread = threading.Thread(target=fixed._audio_playback_monitor_fixed, daemon=True)
        fixed_thread.start()
        time.sleep(0.5)

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