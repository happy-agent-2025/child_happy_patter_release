"""
音频任务生命周期管理简化测试
"""
import os
import sys
import pytest
import threading
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestAudioTaskSimple:
    """测试音频任务简化功能"""

    def test_basic_audio_task_creation(self):
        """测试基本音频任务创建"""

        # 模拟ConnectProcess中的音频任务管理方法
        class MockConnectProcess:
            def __init__(self):
                self.audio_tasks = []
                self.audio_task_lock = threading.Lock()
                self.task_sentence_mapping = {}
                self.completed_sentences = {}
                self.current_task_id = None

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

        # 测试基本功能
        connect = MockConnectProcess()

        # 创建音频任务
        task_id = "test_task"
        all_sentences = ["句子1", "句子2", "句子3"]
        connect.create_audio_task(task_id, all_sentences)

        # 验证任务创建
        assert connect.current_task_id == task_id
        assert task_id in connect.task_sentence_mapping
        assert len(connect.audio_tasks) == 1

        # 标记句子完成
        connect.mark_sentence_completed(task_id, 0)
        connect.mark_sentence_completed(task_id, 1)
        connect.mark_sentence_completed(task_id, 2)

        # 标记任务完成
        connect.mark_audio_task_completed(task_id)

        # 验证任务清理
        assert task_id not in connect.task_sentence_mapping
        assert task_id not in connect.completed_sentences
        assert connect.current_task_id is None
        assert len(connect.audio_tasks) == 0

    def test_mark_audio_completed_integration(self):
        """测试mark_audio_completed集成"""

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

        # 测试集成功能
        connect = MockConnectProcess()

        # 创建音频任务
        task_id = "test_task"
        all_sentences = ["句子1", "句子2"]
        connect.create_audio_task(task_id, all_sentences)

        # 模拟播放第一个句子
        connect.set_playback_state(0, 2, False)
        connect.mark_audio_completed()

        # 验证第一个句子被标记完成
        assert 0 in connect.completed_sentences[task_id]

        # 模拟播放第二个句子
        connect.set_playback_state(1, 2, True)
        connect.mark_audio_completed()

        # 验证第二个句子被标记完成
        assert 1 in connect.completed_sentences[task_id]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])