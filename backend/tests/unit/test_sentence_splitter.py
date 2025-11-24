"""
智能分句功能测试用例
遵循TDD红-绿-重构流程
"""
import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.sentence_splitter import SmartSentenceSplitter



class TestSentenceSplitter:
    """测试智能分句功能"""

    def test_chinese_sentence_splitting(self):
        """测试中文句子分句"""
        # 准备测试数据
        text_buffer = ["哇，你像一个小科学家一样提出了一个很棒的问题呢！不过，我好像没有看到你具体想问什么科学问题哦。你是想知道为什么天空是蓝色的？还是好奇为什么树叶会变颜色？"]

        # 调用分句函数
        splitter = SmartSentenceSplitter()
        remaining_buffer, complete_sentence = splitter.get_complete_sentence(text_buffer)

        # 验证结果
        assert complete_sentence == "哇，你像一个小科学家一样提出了一个很棒的问题呢！"
        assert remaining_buffer == ["不过，我好像没有看到你具体想问什么科学问题哦。你是想知道为什么天空是蓝色的？还是好奇为什么树叶会变颜色？"]

    def test_english_sentence_splitting(self):
        """测试英文句子分句"""
        text_buffer = ["Hello! How are you today? I'm doing great. What about you?"]

        splitter = SmartSentenceSplitter()
        remaining_buffer, complete_sentence = splitter.get_complete_sentence(text_buffer)

        assert complete_sentence == "Hello!"
        assert remaining_buffer == [" How are you today? I'm doing great. What about you?"]

    def test_mixed_chinese_english_splitting(self):
        """测试中英文混合句子分句"""
        text_buffer = ["哇，你像一个小科学家一样提出了一个很棒的问题呢！Hello! How are you today? 不过，我好像没有看到你具体想问什么科学问题哦。"]

        splitter = SmartSentenceSplitter()
        remaining_buffer, complete_sentence = splitter.get_complete_sentence(text_buffer)

        assert complete_sentence == "哇，你像一个小科学家一样提出了一个很棒的问题呢！"
        assert remaining_buffer == ["Hello! How are you today? 不过，我好像没有看到你具体想问什么科学问题哦。"]

    def test_multiple_sentence_endings(self):
        """测试多种句子结束符"""
        text_buffer = ["这是一个句子。这是另一个句子！这是第三个句子？这是第四个句子。"]

        splitter = SmartSentenceSplitter()
        remaining_buffer, complete_sentence = splitter.get_complete_sentence(text_buffer)

        assert complete_sentence == "这是一个句子。"
        assert remaining_buffer == ["这是另一个句子！这是第三个句子？这是第四个句子。"]

    def test_no_sentence_endings(self):
        """测试没有句子结束符的情况"""
        text_buffer = ["这是一个没有结束的句子"]

        splitter = SmartSentenceSplitter()
        remaining_buffer, complete_sentence = splitter.get_complete_sentence(text_buffer)

        assert complete_sentence == ""
        assert remaining_buffer == ["这是一个没有结束的句子"]

    def test_empty_buffer(self):
        """测试空缓冲区"""
        text_buffer = []

        splitter = SmartSentenceSplitter()
        remaining_buffer, complete_sentence = splitter.get_complete_sentence(text_buffer)

        assert complete_sentence == ""
        assert remaining_buffer == []

    def test_json_structure_handling(self):
        """测试JSON结构处理"""
        text_buffer = ["这是一个句子。{\"type\": \"json\", \"data\": \"value\"} 这是另一个句子。"]

        splitter = SmartSentenceSplitter()
        remaining_buffer, complete_sentence = splitter.get_complete_sentence(text_buffer)

        assert complete_sentence == "这是一个句子。"
        assert remaining_buffer == ["{\"type\": \"json\", \"data\": \"value\"} 这是另一个句子。"]

    def test_complex_mixed_content(self):
        """测试复杂混合内容"""
        text_buffer = ["Hello! 你好！这是一个混合的句子。How are you? 我很好！{\"data\": \"test\"} 这是结尾。"]

        splitter = SmartSentenceSplitter()
        remaining_buffer, complete_sentence = splitter.get_complete_sentence(text_buffer)

        assert complete_sentence == "Hello!"
        assert remaining_buffer == [" 你好！这是一个混合的句子。How are you? 我很好！{\"data\": \"test\"} 这是结尾。"]

    def test_ellipsis_handling(self):
        """测试省略号处理"""
        text_buffer = ["这是一个句子... 这是另一个句子。"]

        splitter = SmartSentenceSplitter()
        remaining_buffer, complete_sentence = splitter.get_complete_sentence(text_buffer)

        # 期望结果：正确处理省略号，找到真正的句子结束符
        assert complete_sentence == "这是一个句子... 这是另一个句子。"
        assert remaining_buffer == []

    def test_quotation_marks_handling(self):
        """测试引号处理"""
        text_buffer = ["他说：\"你好！\" 然后离开了。"]

        splitter = SmartSentenceSplitter()
        remaining_buffer, complete_sentence = splitter.get_complete_sentence(text_buffer)

        # 期望结果：正确处理引号内的感叹号
        assert complete_sentence == "他说：\"你好！\""
        assert remaining_buffer == [" 然后离开了。"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])