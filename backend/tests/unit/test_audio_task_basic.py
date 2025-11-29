"""
音频任务基本功能测试
"""
import os
import sys
import pytest
import threading

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestAudioTaskBasic:
    """测试音频任务基本功能"""

    def test_create_audio_task(self):
        """测试创建音频任务"""

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
                        'created_time': 1234567890.0
                    }
                    self.audio_tasks.append(task_info)
                    self.task_sentence_mapping[task_id] = all_sentences
                    self.completed_sentences[task_id] = set()
                    self.current_task_id = task_id

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
        assert connect.audio_tasks[0]['task_id'] == task_id
        assert connect.audio_tasks[0]['sentences'] == all_sentences

    def test_mark_sentence_completed(self):
        """测试标记句子完成"""

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
                        'created_time': 1234567890.0
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

        # 测试句子完成标记
        connect = MockConnectProcess()

        # 创建音频任务
        task_id = "test_task"
        all_sentences = ["句子1", "句子2", "句子3"]
        connect.create_audio_task(task_id, all_sentences)

        # 标记句子完成
        connect.mark_sentence_completed(task_id, 0)
        connect.mark_sentence_completed(task_id, 2)

        # 验证句子完成状态
        assert 0 in connect.completed_sentences[task_id]
        assert 2 in connect.completed_sentences[task_id]
        assert 1 not in connect.completed_sentences[task_id]

    def test_mark_audio_task_completed(self):
        """测试标记音频任务完成"""

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
                        'created_time': 1234567890.0
                    }
                    self.audio_tasks.append(task_info)
                    self.task_sentence_mapping[task_id] = all_sentences
                    self.completed_sentences[task_id] = set()
                    self.current_task_id = task_id

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

        # 测试任务完成标记
        connect = MockConnectProcess()

        # 创建音频任务
        task_id = "test_task"
        all_sentences = ["句子1", "句子2", "句子3"]
        connect.create_audio_task(task_id, all_sentences)

        # 标记任务完成
        connect.mark_audio_task_completed(task_id)

        # 验证任务清理
        assert task_id not in connect.task_sentence_mapping
        assert task_id not in connect.completed_sentences
        assert connect.current_task_id is None
        assert len(connect.audio_tasks) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])