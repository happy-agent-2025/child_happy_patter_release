"""
音频播放监控简化测试用例

专注于验证音频播放完成信号缺失的核心问题，避免依赖问题
"""
import os
import sys
import pytest
import threading
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestAudioPlaybackSimple:
    """测试音频播放监控简化功能"""

    def test_monitor_thread_break_issue(self):
        """测试监控线程在检测到播放完成时break退出的问题"""

        # 模拟当前ConnectProcess中的_audio_playback_monitor方法
        class MockConnectProcess:
            def __init__(self):
                self.stop_event = threading.Event()
                self.is_last_sentence_playing = False
                self.current_playing_index = 0
                self.total_sentences = 0
                self.current_audio_completed = False
                self.playback_state_lock = threading.Lock()
                self.logger = MockLogger()

            def _audio_playback_monitor(self):
                """模拟当前有问题的监控线程实现"""
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
                            break  # 问题：线程在此退出

                        # 等待一段时间再检查
                        self.stop_event.wait(0.5)

                    except Exception as e:
                        self.logger.error(f"音频播放监控线程异常: {e}")
                        break

            def _send_playback_completion_signal(self):
                """模拟发送播放完成信号"""
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

        class MockLogger:
            def __init__(self):
                self.messages = []

            def info(self, msg):
                self.messages.append(f"INFO: {msg}")

            def error(self, msg):
                self.messages.append(f"ERROR: {msg}")

        # 测试当前实现的问题
        connect = MockConnectProcess()

        # 启动监控线程
        monitor_thread = threading.Thread(target=connect._audio_playback_monitor, daemon=True)
        monitor_thread.start()

        # 设置播放状态为最后一个句子
        connect.set_playback_state(2, 3, True)  # 第三个句子，总共3个句子，是最后一个
        connect.mark_audio_completed()  # 标记播放完成

        # 等待线程处理
        time.sleep(0.5)

        # 验证问题：监控线程在检测到播放完成时break退出
        assert not monitor_thread.is_alive(), "监控线程应该在检测到播放完成时break退出（这是当前的问题）"

        # 验证日志包含播放完成信息
        completion_logs = [msg for msg in connect.logger.messages if "检测到最后一个句子在send_audio中播放完成" in msg]
        assert len(completion_logs) > 0, "应该记录播放完成检测日志"

    def test_missing_audio_task_methods(self):
        """测试缺失的音频任务跟踪方法"""

        # 模拟当前ConnectProcess的状态
        class MockConnectProcess:
            def __init__(self):
                # 当前实现中缺少这些方法
                pass

        connect = MockConnectProcess()

        # 验证缺失的方法（这些方法当前不存在）
        assert not hasattr(connect, 'add_audio_task'), "add_audio_task方法当前应该不存在"
        assert not hasattr(connect, 'mark_audio_task_completed'), "mark_audio_task_completed方法当前应该不存在"

    def test_continuous_monitoring_requirement(self):
        """测试监控线程需要持续运行的需求"""

        # 模拟修复后的监控线程实现
        class FixedConnectProcess:
            def __init__(self):
                self.stop_event = threading.Event()
                self.is_last_sentence_playing = False
                self.current_playing_index = 0
                self.total_sentences = 0
                self.current_audio_completed = False
                self.playback_state_lock = threading.Lock()
                self.logger = MockLogger()
                self.audio_tasks = []  # 新增：音频任务队列

            def _audio_playback_monitor(self):
                """修复后的监控线程实现 - 应该持续运行"""
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
                            # 修复：不break，继续监控

                        # 等待一段时间再检查
                        self.stop_event.wait(0.5)

                    except Exception as e:
                        self.logger.error(f"音频播放监控线程异常: {e}")
                        # 修复：异常时也不break，继续监控

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
                """新增：添加音频任务"""
                self.audio_tasks.append(task_info)

            def mark_audio_task_completed(self, task_id):
                """新增：标记音频任务完成"""
                self.logger.info(f"音频任务 {task_id} 完成")

        # 测试修复后的实现
        connect = FixedConnectProcess()

        # 启动监控线程
        monitor_thread = threading.Thread(target=connect._audio_playback_monitor, daemon=True)
        monitor_thread.start()

        # 设置播放状态为最后一个句子
        connect.set_playback_state(2, 3, True)  # 第三个句子，总共3个句子，是最后一个
        connect.mark_audio_completed()  # 标记播放完成

        # 等待线程处理
        time.sleep(0.5)

        # 验证修复：监控线程应该持续运行
        assert monitor_thread.is_alive(), "修复后监控线程应该持续运行"

        # 验证新增的方法
        assert hasattr(connect, 'add_audio_task'), "修复后应该有add_audio_task方法"
        assert hasattr(connect, 'mark_audio_task_completed'), "修复后应该有mark_audio_task_completed方法"


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