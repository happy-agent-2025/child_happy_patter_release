"""
音频任务生命周期管理集成测试

验证音频任务创建、跟踪、完成标记的完整流程
"""
import os
import sys
import pytest
import threading
import time
import uuid

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestAudioTaskLifecycle:
    """测试音频任务生命周期管理"""

    def test_audio_task_creation_and_completion(self):
        """测试音频任务创建和完成流程"""

        # 模拟完整的音频任务管理流程
        class MockConnectProcess:
            def __init__(self):
                self.audio_tasks = []
                self.audio_task_lock = threading.Lock()
                self.task_sentence_mapping = {}
                self.completed_sentences = {}
                self.current_task_id = None
                self.playback_state_lock = threading.Lock()
                self.current_playing_index = 0
                self.total_sentences = 0
                self.is_last_sentence_playing = False
                self.current_audio_completed = False
                self.logger = MockLogger()

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

                        # 检查任务是否全部完成
                        if task_id in self.task_sentence_mapping:
                            total_sentences = len(self.task_sentence_mapping[task_id])
                            completed_count = len(self.completed_sentences[task_id])

                            if completed_count == total_sentences:
                                self.mark_audio_task_completed(task_id)

            def mark_audio_task_completed(self, task_id):
                """标记音频任务完成"""
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
                        # 获取当前句子的索引
                        current_sentence_index = self.current_playing_index

                        # 标记句子完成
                        self.mark_sentence_completed(self.current_task_id, current_sentence_index)

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

        # 测试音频任务生命周期
        connect = MockConnectProcess()

        # 创建音频任务
        task_id = "test_task_123"
        all_sentences = ["句子1", "句子2", "句子3"]
        connect.create_audio_task(task_id, all_sentences)

        # 验证任务创建
        assert connect.current_task_id == task_id, "当前任务ID应该被设置"
        assert task_id in connect.task_sentence_mapping, "任务应该被映射"
        assert len(connect.audio_tasks) == 1, "应该有一个音频任务"

        # 模拟播放第一个句子
        connect.set_playback_state(0, 3, False)  # 第一个句子，总共3个，不是最后一个
        connect.mark_audio_completed()

        # 验证第一个句子完成
        status = connect.get_audio_task_status(task_id)
        assert status['completed_sentences'] == 1, "第一个句子应该被标记完成"
        assert status['progress'] == 1/3, "进度应该是1/3"
        assert status['status'] == 'processing', "任务应该还在处理中"

        # 模拟播放第二个句子
        connect.set_playback_state(1, 3, False)  # 第二个句子，总共3个，不是最后一个
        connect.mark_audio_completed()

        # 验证第二个句子完成
        status = connect.get_audio_task_status(task_id)
        assert status['completed_sentences'] == 2, "第二个句子应该被标记完成"
        assert status['progress'] == 2/3, "进度应该是2/3"

        # 模拟播放第三个句子（最后一个）
        connect.set_playback_state(2, 3, True)  # 第三个句子，总共3个，是最后一个
        connect.mark_audio_completed()

        # 验证任务完成
        status = connect.get_audio_task_status(task_id)
        assert status['completed_sentences'] == 3, "所有句子都应该被标记完成"
        assert status['progress'] == 1.0, "进度应该是100%"
        assert status['status'] == 'completed', "任务应该标记为完成"

        # 验证任务清理
        assert task_id not in connect.task_sentence_mapping, "任务映射应该被清理"
        assert task_id not in connect.completed_sentences, "完成状态应该被清理"
        assert connect.current_task_id is None, "当前任务ID应该被清空"
        assert len(connect.audio_tasks) == 0, "所有任务应该被清理"

    def test_multiple_audio_tasks(self):
        """测试多个音频任务的管理"""

        class MockConnectProcess:
            def __init__(self):
                self.audio_tasks = []
                self.audio_task_lock = threading.Lock()
                self.task_sentence_mapping = {}
                self.completed_sentences = {}
                self.current_task_id = None
                self.playback_state_lock = threading.Lock()
                self.current_playing_index = 0
                self.total_sentences = 0
                self.is_last_sentence_playing = False
                self.current_audio_completed = False

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

            def set_playback_state(self, current_index, total_sentences, is_last_sentence):
                """设置播放状态"""
                with self.playback_state_lock:
                    self.current_playing_index = current_index
                    self.total_sentences = total_sentences
                    self.is_last_sentence_playing = is_last_sentence

            def mark_audio_completed(self):
                """标记音频播放完成"""
                with self.playback_state_lock:
                    self.current_audio_completed = True

                # 标记当前句子完成
                self._mark_current_sentence_completed()

            def _mark_current_sentence_completed(self):
                """标记当前句子在音频任务中完成"""
                with self.audio_task_lock:
                    if self.current_task_id and self.current_task_id in self.task_sentence_mapping:
                        current_sentence_index = self.current_playing_index
                        self.mark_sentence_completed(self.current_task_id, current_sentence_index)

        # 测试多个音频任务
        connect = MockConnectProcess()

        # 创建第一个任务
        task1_id = "task_1"
        task1_sentences = ["任务1句子1", "任务1句子2"]
        connect.create_audio_task(task1_id, task1_sentences)

        # 创建第二个任务
        task2_id = "task_2"
        task2_sentences = ["任务2句子1", "任务2句子2", "任务2句子3"]
        connect.create_audio_task(task2_id, task2_sentences)

        # 验证任务创建
        assert len(connect.audio_tasks) == 2, "应该有两个音频任务"
        assert connect.current_task_id == task2_id, "当前任务应该是第二个任务"

        # 完成第一个任务的所有句子
        connect.set_playback_state(0, 2, False)  # 任务1的第一个句子
        connect.mark_audio_completed()

        connect.set_playback_state(1, 2, True)  # 任务1的第二个句子（最后一个）
        connect.mark_audio_completed()

        # 验证第一个任务完成
        assert task1_id not in connect.task_sentence_mapping, "第一个任务应该被清理"
        assert len(connect.audio_tasks) == 1, "应该只剩下一个任务"

        # 完成第二个任务的所有句子
        connect.set_playback_state(0, 3, False)  # 任务2的第一个句子
        connect.mark_audio_completed()

        connect.set_playback_state(1, 3, False)  # 任务2的第二个句子
        connect.mark_audio_completed()

        connect.set_playback_state(2, 3, True)  # 任务2的第三个句子（最后一个）
        connect.mark_audio_completed()

        # 验证所有任务完成
        assert len(connect.audio_tasks) == 0, "所有任务应该被清理"
        assert connect.current_task_id is None, "当前任务ID应该被清空"


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