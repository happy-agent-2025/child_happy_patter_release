"""
音频队列状态检测测试用例
验证智能队列状态检测机制替代简单的time.sleep(2)
"""
import pytest
import sys
import os
import time
import threading
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.protocol.connect_process import ConnectProcess


class TestAudioQueueStateDetection:
    """测试音频队列状态检测功能"""

    def test_connect_process_has_audio_queue(self):
        """测试ConnectProcess包含音频队列"""
        config = Mock()
        ai = Mock()

        connect_process = ConnectProcess(config, ai)

        # 验证音频队列存在
        assert hasattr(connect_process, 'audio_send_queue')
        assert connect_process.audio_send_queue is not None

    def test_audio_send_thread_exists(self):
        """测试音频发送线程存在"""
        config = Mock()
        ai = Mock()

        connect_process = ConnectProcess(config, ai)

        # 验证音频发送线程相关属性存在
        assert hasattr(connect_process, 'audio_send_thread')
        assert hasattr(connect_process, 'stop_event')

    def test_wait_for_audio_completion_method_exists(self):
        """测试wait_for_audio_completion方法存在（修复后状态）"""
        config = Mock()
        ai = Mock()

        connect_process = ConnectProcess(config, ai)

        # 验证现在有智能等待方法
        assert hasattr(connect_process, 'wait_for_audio_completion')
        assert callable(getattr(connect_process, 'wait_for_audio_completion'))

    def test_audio_queue_task_tracking_exists(self):
        """测试音频任务跟踪功能存在（修复后状态）"""
        config = Mock()
        ai = Mock()

        connect_process = ConnectProcess(config, ai)

        # 验证现在有任务跟踪功能
        assert hasattr(connect_process, 'audio_tasks')
        assert hasattr(connect_process, 'audio_completion_event')
        assert hasattr(connect_process, 'audio_task_lock')
        assert hasattr(connect_process, 'pending_audio_tasks')

    def test_message_process_uses_smart_queue_detection(self):
        """测试MessageProcess使用智能队列状态检测等待音频队列"""
        # 这个测试验证修复后的状态
        import utils.protocol.message_process as message_process_module

        # 读取文件内容检查是否使用智能队列状态检测
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'utils', 'protocol', 'message_process.py'
        )

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 验证使用智能队列状态检测
        assert 'wait_for_audio_completion' in content
        assert '# 等待音频队列处理完成（智能队列状态检测）' in content
        assert 'get_audio_queue_status' in content

    def test_audio_queue_processing_completion_detection(self):
        """测试音频队列处理完成检测功能"""
        config = Mock()
        ai = Mock()

        connect_process = ConnectProcess(config, ai)

        # 验证现在可以检测队列处理完成状态
        assert hasattr(connect_process, 'wait_for_audio_completion')

        # 测试没有待处理任务时立即返回True
        connect_process.pending_audio_tasks = 0
        result = connect_process.wait_for_audio_completion(timeout=1)
        assert result == True

        # 测试有任务时返回False（因为mock对象没有实际任务）
        connect_process.pending_audio_tasks = 1
        result = connect_process.wait_for_audio_completion(timeout=0.1)
        assert result == False

    def test_audio_queue_timeout_handling(self):
        """测试音频队列超时处理"""
        config = Mock()
        ai = Mock()

        connect_process = ConnectProcess(config, ai)

        # 验证现在有超时处理机制
        assert hasattr(connect_process, 'wait_for_audio_completion')

        # 测试超时处理
        connect_process.pending_audio_tasks = 1
        result = connect_process.wait_for_audio_completion(timeout=0.1)
        assert result == False  # 应该超时返回False

    def test_multiple_audio_tasks_completion_tracking(self):
        """测试多个音频任务完成跟踪"""
        config = Mock()
        ai = Mock()

        connect_process = ConnectProcess(config, ai)

        # 验证现在可以跟踪多个任务的完成状态
        assert hasattr(connect_process, 'audio_tasks')
        assert hasattr(connect_process, 'pending_audio_tasks')
        assert hasattr(connect_process, 'add_audio_task')
        assert hasattr(connect_process, 'mark_audio_task_completed')

        # 测试任务跟踪功能
        connect_process.pending_audio_tasks = 0
        mock_future = Mock()
        connect_process.add_audio_task(mock_future)
        assert connect_process.pending_audio_tasks == 1
        assert len(connect_process.audio_tasks) == 1

        connect_process.mark_audio_task_completed()
        assert connect_process.pending_audio_tasks == 0

    def test_audio_queue_progress_monitoring(self):
        """测试音频队列进度监控"""
        config = Mock()
        ai = Mock()

        connect_process = ConnectProcess(config, ai)

        # 验证现在有进度监控功能
        assert hasattr(connect_process, 'get_audio_queue_status')

        # 测试队列状态监控
        status = connect_process.get_audio_queue_status()
        assert isinstance(status, dict)
        assert 'pending_tasks' in status
        assert 'total_tasks' in status
        assert 'queue_size' in status
        assert 'is_completed' in status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])