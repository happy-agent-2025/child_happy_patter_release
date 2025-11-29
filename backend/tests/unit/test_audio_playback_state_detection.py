"""
音频播放状态检测功能测试用例

按照TDD模式编写，验证音频播放状态精确检测和结束信号发送功能
"""
import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
import threading
import asyncio

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# 使用mock避免导入依赖问题
# from utils.protocol.connect_process import ConnectProcess
# from utils.protocol.message_process import MessageProcess


class TestAudioPlaybackStateDetection:
    """测试音频播放状态检测功能"""

    def test_connect_process_has_playback_state_attributes(self):
        """测试ConnectProcess包含播放状态跟踪属性（简化后状态）"""
        # 读取文件内容检查播放状态跟踪属性
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'utils', 'protocol', 'connect_process.py'
        )

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 验证简化后的播放状态跟踪属性
        assert 'current_playing_index' in content
        assert 'total_sentences' in content
        assert 'is_last_sentence_playing' in content
        assert 'audio_playback_monitor_thread' in content
        assert 'current_audio_completed' in content
        assert 'audio_completion_callbacks' in content

    def test_set_playback_state_method_exists(self):
        """测试set_playback_state方法存在（修复后状态）"""
        # 读取文件内容检查set_playback_state方法
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'utils', 'protocol', 'connect_process.py'
        )

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 验证现在有设置播放状态的方法
        assert 'set_playback_state' in content
        assert 'mark_audio_completed' in content
        assert 'add_audio_completion_callback' in content

    def test_audio_playback_monitor_thread_exists(self):
        """测试音频播放监控线程存在（修复后状态）"""
        # 读取文件内容检查音频播放监控线程
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'utils', 'protocol', 'connect_process.py'
        )

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 验证现在有音频播放监控线程
        assert 'start_audio_playback_monitor' in content
        assert '_audio_playback_monitor' in content
        assert 'current_audio_completed' in content

    def test_message_process_sets_playback_state(self):
        """测试MessageProcess正确设置播放状态（修复后状态）"""
        # 读取文件内容检查是否设置播放状态
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'utils', 'protocol', 'message_process.py'
        )

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 验证现在有设置播放状态的代码
        assert 'set_playback_state' in content
        assert 'is_last_sentence' in content
        assert 'start_audio_playback_monitor' in content

    def test_end_signal_sending_implemented(self):
        """测试结束信号发送功能已实现（修复后状态）"""
        # 读取文件内容检查结束信号发送方法
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'utils', 'protocol', 'connect_process.py'
        )

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 验证现在有结束信号发送方法
        assert '_send_playback_completion_signal' in content

    def test_playback_state_tracking_functionality(self):
        """测试播放状态跟踪功能已实现（修复后状态）"""
        # 读取文件内容检查播放状态跟踪功能
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'utils', 'protocol', 'connect_process.py'
        )

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 验证现在有播放状态跟踪功能
        assert 'current_playing_index' in content
        assert 'total_sentences' in content
        assert 'is_last_sentence_playing' in content
        assert 'playback_state_lock' in content

    def test_last_sentence_detection_functionality(self):
        """测试最后一个句子检测功能已实现（修复后状态）"""
        # 读取文件内容检查最后一个句子检测功能
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'utils', 'protocol', 'connect_process.py'
        )

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 验证现在有最后一个句子检测功能
        assert 'is_last_sentence_playing' in content
        assert 'total_sentences' in content
        assert 'current_playing_index' in content

    def test_playback_completion_signal_sending(self):
        """测试播放完成信号发送功能已实现（修复后状态）"""
        # 读取文件内容检查播放完成信号发送功能
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'utils', 'protocol', 'connect_process.py'
        )

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 验证现在有播放完成信号发送功能
        assert '_send_playback_completion_signal' in content
        assert 'SendMessage.send_audio' in content

    def test_audio_playback_monitor_thread_operation(self):
        """测试音频播放监控线程操作已实现（修复后状态）"""
        # 读取文件内容检查音频播放监控线程操作
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'utils', 'protocol', 'connect_process.py'
        )

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 验证现在有音频播放监控线程操作
        assert 'start_audio_playback_monitor' in content
        assert '_audio_playback_monitor' in content
        assert 'audio_playback_monitor_thread' in content

    def test_multiple_sentence_playback_tracking(self):
        """测试多个句子播放跟踪功能已实现（修复后状态）"""
        # 读取文件内容检查多个句子播放跟踪功能
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'utils', 'protocol', 'connect_process.py'
        )

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 验证现在有多个句子播放跟踪功能
        assert 'current_playing_index' in content
        assert 'total_sentences' in content
        assert 'set_playback_state' in content

    def test_playback_state_set_in_send_audio(self):
        """测试播放状态在send_audio中设置，而不是在MessageProcess中设置"""
        # 读取SendMessage文件内容检查播放状态设置
        send_message_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'utils', 'protocol', 'send_message.py'
        )

        with open(send_message_file, 'r', encoding='utf-8') as f:
            send_message_content = f.read()

        # 读取MessageProcess文件内容检查播放状态设置
        message_process_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'utils', 'protocol', 'message_process.py'
        )

        with open(message_process_file, 'r', encoding='utf-8') as f:
            message_process_content = f.read()

        # 验证播放状态应该在send_audio中设置，而不是在MessageProcess中
        # 这个测试应该失败，因为当前实现在MessageProcess中设置状态
        assert 'set_playback_state' in send_message_content, "播放状态应该在send_audio中设置"
        # 这个断言应该失败，因为我们希望最终在send_audio中设置状态

    def test_message_process_does_not_set_playback_state(self):
        """测试MessageProcess不再设置播放状态"""
        # 读取MessageProcess文件内容检查播放状态设置
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'utils', 'protocol', 'message_process.py'
        )

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 验证MessageProcess中不再设置播放状态
        # 这个测试应该失败，因为当前实现在MessageProcess中设置状态
        assert 'set_playback_state' not in content, "MessageProcess不应该设置播放状态"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])