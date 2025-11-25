"""
MessageProcess长句拆分问题测试用例
验证长句子被正确拆分成多个短句子发送到前端硬件
"""
import pytest
import sys
import os
import asyncio
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.protocol.message_process import MessageProcess


class TestMessageProcessSentenceSplitting:
    """测试MessageProcess长句拆分功能"""

    def test_single_sentence_processing(self):
        """测试单句文本处理"""
        config = Mock()
        connect = Mock()
        connect.connect_thread_pool = Mock()
        connect.audio_send_queue = Mock()
        connect.loop = asyncio.new_event_loop()

        message_process = MessageProcess(config, connect)

        # 模拟单句AI响应
        single_sentence = "这是一个单句。"

        with patch.object(message_process, '_process_with_agents', return_value=single_sentence):
            with patch.object(message_process.ai.tts, 'text_to_opus_data') as mock_tts:
                mock_tts.return_value = (b'audio_data', 1.0, single_sentence)

                # 调用start_chat方法
                message_process.start_chat("用户输入")

                # 验证音频任务被正确提交
                assert mock_tts.call_count == 1

    def test_multiple_sentence_splitting(self):
        """测试多句长文本分句"""
        config = Mock()
        connect = Mock()
        connect.connect_thread_pool = Mock()
        connect.audio_send_queue = Mock()
        connect.loop = asyncio.new_event_loop()

        message_process = MessageProcess(config, connect)

        # 模拟多句AI响应
        long_response = "这是第一个句子。这是第二个句子！这是第三个句子？"

        with patch.object(message_process, '_process_with_agents', return_value=long_response):
            with patch.object(message_process.ai.tts, 'text_to_opus_data') as mock_tts:
                mock_tts.return_value = (b'audio_data', 1.0, "test")

                # 调用start_chat方法
                message_process.start_chat("用户输入")

                # 验证多个音频任务被提交（应该拆分成3个句子）
                assert mock_tts.call_count == 3

    def test_mixed_chinese_english_splitting(self):
        """测试中英文混合文本分句"""
        config = Mock()
        connect = Mock()
        connect.connect_thread_pool = Mock()
        connect.audio_send_queue = Mock()
        connect.loop = asyncio.new_event_loop()

        message_process = MessageProcess(config, connect)

        # 模拟中英文混合响应
        mixed_response = "Hello! 你好！这是一个混合的句子。How are you? 我很好！"

        with patch.object(message_process, '_process_with_agents', return_value=mixed_response):
            with patch.object(message_process.ai.tts, 'text_to_opus_data') as mock_tts:
                mock_tts.return_value = (b'audio_data', 1.0, "test")

                # 调用start_chat方法
                message_process.start_chat("用户输入")

                # 验证多个音频任务被提交
                assert mock_tts.call_count > 1

    def test_json_structure_handling(self):
        """测试JSON结构处理"""
        config = Mock()
        connect = Mock()
        connect.connect_thread_pool = Mock()
        connect.audio_send_queue = Mock()
        connect.loop = asyncio.new_event_loop()

        message_process = MessageProcess(config, connect)

        # 模拟包含JSON的响应
        json_response = "这是一个句子。{\"type\": \"json\", \"data\": \"value\"} 这是另一个句子。"

        with patch.object(message_process, '_process_with_agents', return_value=json_response):
            with patch.object(message_process.ai.tts, 'text_to_opus_data') as mock_tts:
                mock_tts.return_value = (b'audio_data', 1.0, "test")

                # 调用start_chat方法
                message_process.start_chat("用户输入")

                # 验证音频任务被提交（应该排除JSON部分）
                assert mock_tts.call_count == 2

    def test_special_characters_handling(self):
        """测试特殊字符处理"""
        config = Mock()
        connect = Mock()
        connect.connect_thread_pool = Mock()
        connect.audio_send_queue = Mock()
        connect.loop = asyncio.new_event_loop()

        message_process = MessageProcess(config, connect)

        # 模拟包含特殊字符的响应
        special_response = "他说：\"你好！\" 然后离开了。这是一个句子... 这是另一个句子。"

        with patch.object(message_process, '_process_with_agents', return_value=special_response):
            with patch.object(message_process.ai.tts, 'text_to_opus_data') as mock_tts:
                mock_tts.return_value = (b'audio_data', 1.0, "test")

                # 调用start_chat方法
                message_process.start_chat("用户输入")

                # 验证音频任务被正确提交
                assert mock_tts.call_count > 0

    def test_empty_text_handling(self):
        """测试空文本处理"""
        config = Mock()
        connect = Mock()
        connect.connect_thread_pool = Mock()
        connect.audio_send_queue = Mock()
        connect.loop = asyncio.new_event_loop()

        message_process = MessageProcess(config, connect)

        # 模拟空响应
        empty_response = ""

        with patch.object(message_process, '_process_with_agents', return_value=empty_response):
            with patch.object(message_process.ai.tts, 'text_to_opus_data') as mock_tts:
                mock_tts.return_value = (b'audio_data', 1.0, "test")

                # 调用start_chat方法
                message_process.start_chat("用户输入")

                # 验证没有音频任务被提交
                assert mock_tts.call_count == 0

    def test_very_long_sentence_splitting(self):
        """测试非常长的句子拆分"""
        config = Mock()
        connect = Mock()
        connect.connect_thread_pool = Mock()
        connect.audio_send_queue = Mock()
        connect.loop = asyncio.new_event_loop()

        message_process = MessageProcess(config, connect)

        # 模拟非常长的AI响应
        very_long_response = """哇，你像一个小科学家一样提出了一个很棒的问题呢！不过，我好像没有看到你具体想问什么科学问题哦。你是想知道为什么天空是蓝色的？还是好奇为什么树叶会变颜色？或者你想了解小动物们是怎么生活的？

让我来举个例子吧：如果你想知道"为什么船能浮在水上"，我们可以一起做一个小实验！你只需要一个碗、一些水和一张铝箔纸。把铝箔纸捏成小船的形状放在水里，看看它会不会浮起来？然后我们再捏成一个紧实的小球放进去，看看会发生什么？这样我们就能一起发现"浮力"的小秘密啦！

或者，如果你喜欢听故事，我可以讲一个关于"小水滴的旅行"的故事，告诉你雨水是怎么形成的。

请告诉我你最感兴趣的问题是什么，我们就像真正的科学家一样，用有趣的实验或者好玩的故事来寻找答案！记住，科学家都是爱提问、爱动手尝试的，你提出的每一个问题都很棒哦！"""

        with patch.object(message_process, '_process_with_agents', return_value=very_long_response):
            with patch.object(message_process.ai.tts, 'text_to_opus_data') as mock_tts:
                mock_tts.return_value = (b'audio_data', 1.0, "test")

                # 调用start_chat方法
                message_process.start_chat("用户输入")

                # 验证多个音频任务被提交（长文本应该被拆分成多个句子）
                assert mock_tts.call_count > 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])