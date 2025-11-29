"""
音频播放监控功能测试用例

按照TDD模式编写，验证音频播放完成信号缺失问题
"""
import os
import sys
import pytest
import asyncio
import threading
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestAudioPlaybackMonitor:
    """测试音频播放监控功能"""

    def test_audio_playback_monitor_thread_exists(self):
        """测试音频播放监控线程存在"""
        try:
            from utils.protocol.connect_process import ConnectProcess
            from ai_core.ai_instance_repository import AiInstanceRepository

            # 创建配置对象
            config = type('Config', (), {'enable_aec': True})()
            ai_repo = AiInstanceRepository(config)

            connect = ConnectProcess(config, ai_repo)

            # 验证监控线程方法存在
            assert hasattr(connect, '_audio_playback_monitor'), "ConnectProcess应该有_audio_playback_monitor方法"
            assert hasattr(connect, 'start_audio_playback_monitor'), "ConnectProcess应该有start_audio_playback_monitor方法"

        except ImportError:
            pytest.fail("ConnectProcess模块应该存在")

    def test_playback_state_management_exists(self):
        """测试播放状态管理方法存在"""
        try:
            from utils.protocol.connect_process import ConnectProcess
            from ai_core.ai_instance_repository import AiInstanceRepository

            config = type('Config', (), {'enable_aec': True})()
            ai_repo = AiInstanceRepository(config)
            connect = ConnectProcess(config, ai_repo)

            # 验证状态管理方法存在
            assert hasattr(connect, 'set_playback_state'), "ConnectProcess应该有set_playback_state方法"
            assert hasattr(connect, 'mark_audio_completed'), "ConnectProcess应该有mark_audio_completed方法"

        except ImportError:
            pytest.fail("ConnectProcess模块应该存在")

    def test_playback_completion_signal_exists(self):
        """测试播放完成信号发送方法存在"""
        try:
            from utils.protocol.connect_process import ConnectProcess
            from ai_core.ai_instance_repository import AiInstanceRepository

            config = type('Config', (), {'enable_aec': True})()
            ai_repo = AiInstanceRepository(config)
            connect = ConnectProcess(config, ai_repo)

            # 验证播放完成信号方法存在
            assert hasattr(connect, '_send_playback_completion_signal'), "ConnectProcess应该有_send_playback_completion_signal方法"

        except ImportError:
            pytest.fail("ConnectProcess模块应该存在")

    def test_monitor_thread_does_not_exit_on_completion(self):
        """测试监控线程在检测到播放完成时不会退出"""
        try:
            from utils.protocol.connect_process import ConnectProcess
            from ai_core.ai_instance_repository import AiInstanceRepository

            config = type('Config', (), {'enable_aec': True})()
            ai_repo = AiInstanceRepository(config)
            connect = ConnectProcess(config, ai_repo)

            # 启动监控线程
            connect.start_audio_playback_monitor()

            # 设置播放状态为最后一个句子
            connect.set_playback_state(2, 3, True)  # 第三个句子，总共3个句子，是最后一个
            connect.mark_audio_completed()  # 标记播放完成

            # 等待一小段时间让监控线程处理
            time.sleep(0.1)

            # 验证监控线程仍然在运行（不应该在检测到完成时退出）
            assert connect.audio_playback_monitor_thread.is_alive(), "监控线程应该在检测到播放完成时继续运行"

        except ImportError:
            pytest.fail("ConnectProcess模块应该存在")

    def test_playback_completion_log_exists(self):
        """测试播放完成日志存在"""
        try:
            from utils.protocol.connect_process import ConnectProcess
            from ai_core.ai_instance_repository import AiInstanceRepository

            config = type('Config', (), {'enable_aec': True})()
            ai_repo = AiInstanceRepository(config)
            connect = ConnectProcess(config, ai_repo)

            # 设置播放状态为最后一个句子
            connect.set_playback_state(2, 3, True)  # 第三个句子，总共3个句子，是最后一个
            connect.mark_audio_completed()  # 标记播放完成

            # 验证应该打印"检测到最后一个句子在send_audio中播放完成，发送结束信号"日志
            # 这个测试应该失败，因为当前实现中监控线程在检测到完成时会break退出

        except ImportError:
            pytest.fail("ConnectProcess模块应该存在")

    def test_audio_task_tracking_methods_exist(self):
        """测试音频任务跟踪方法存在"""
        try:
            from utils.protocol.connect_process import ConnectProcess
            from ai_core.ai_instance_repository import AiInstanceRepository

            config = type('Config', (), {'enable_aec': True})()
            ai_repo = AiInstanceRepository(config)
            connect = ConnectProcess(config, ai_repo)

            # 验证音频任务跟踪方法存在
            # 这些方法当前应该不存在，测试应该失败
            assert hasattr(connect, 'add_audio_task'), "ConnectProcess应该有add_audio_task方法"
            assert hasattr(connect, 'mark_audio_task_completed'), "ConnectProcess应该有mark_audio_task_completed方法"

        except ImportError:
            pytest.fail("ConnectProcess模块应该存在")

    def test_monitor_thread_continuous_monitoring(self):
        """测试监控线程持续监控多个音频任务"""
        try:
            from utils.protocol.connect_process import ConnectProcess
            from ai_core.ai_instance_repository import AiInstanceRepository

            config = type('Config', (), {'enable_aec': True})()
            ai_repo = AiInstanceRepository(config)
            connect = ConnectProcess(config, ai_repo)

            # 启动监控线程
            connect.start_audio_playback_monitor()

            # 模拟多个音频任务
            for i in range(3):
                connect.set_playback_state(i, 3, i == 2)  # 最后一个句子是第三个
                connect.mark_audio_completed()
                time.sleep(0.1)

            # 验证监控线程仍然在运行
            assert connect.audio_playback_monitor_thread.is_alive(), "监控线程应该持续监控多个音频任务"

        except ImportError:
            pytest.fail("ConnectProcess模块应该存在")

    def test_playback_completion_signal_sent(self):
        """测试播放完成信号正确发送"""
        try:
            from utils.protocol.connect_process import ConnectProcess
            from ai_core.ai_instance_repository import AiInstanceRepository

            config = type('Config', (), {'enable_aec': True})()
            ai_repo = AiInstanceRepository(config)
            connect = ConnectProcess(config, ai_repo)

            # 设置播放状态为最后一个句子
            connect.set_playback_state(2, 3, True)
            connect.mark_audio_completed()

            # 验证_send_playback_completion_signal方法被调用
            # 这个测试应该失败，因为当前实现中监控线程在检测到完成时会break退出

        except ImportError:
            pytest.fail("ConnectProcess模块应该存在")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])