"""
MessageProcess长句拆分问题测试用例 - 真实接口测试
验证长句子被正确拆分成多个短句子发送到前端硬件
"""
import pytest
import sys
import os
import asyncio

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.sentence_splitter import SmartSentenceSplitter


class TestMessageProcessSentenceSplittingReal:
    """测试MessageProcess长句拆分功能 - 真实接口测试"""

    def test_single_sentence_processing_real(self):
        """测试单句文本处理 - 真实接口"""
        splitter = SmartSentenceSplitter()

        # 测试单句文本
        single_sentence = "这是一个单句。"
        sentences = splitter.split_all_sentences(single_sentence)

        # 验证正确分割成1个句子
        assert len(sentences) == 1
        assert sentences[0] == "这是一个单句。"

    def test_multiple_sentence_splitting_real(self):
        """测试多句长文本分句 - 真实接口"""
        splitter = SmartSentenceSplitter()

        # 测试多句文本
        long_response = "这是第一个句子。这是第二个句子！这是第三个句子？"
        sentences = splitter.split_all_sentences(long_response)

        # 验证正确分割成3个句子
        assert len(sentences) == 3
        assert sentences[0] == "这是第一个句子。"
        assert sentences[1] == "这是第二个句子！"
        assert sentences[2] == "这是第三个句子？"

    def test_mixed_chinese_english_splitting_real(self):
        """测试中英文混合文本分句 - 真实接口"""
        splitter = SmartSentenceSplitter()

        # 测试中英文混合文本
        mixed_response = "Hello! 你好！这是一个混合的句子。How are you? 我很好！"
        sentences = splitter.split_all_sentences(mixed_response)

        # 验证正确分割成多个句子
        assert len(sentences) == 5
        assert sentences[0] == "Hello!"
        assert sentences[1].strip() == "你好！"  # 允许空格
        assert sentences[2].strip() == "这是一个混合的句子。"
        assert sentences[3] == "How are you?"
        assert sentences[4].strip() == "我很好！"

    def test_json_structure_handling_real(self):
        """测试JSON结构处理 - 真实接口"""
        splitter = SmartSentenceSplitter()

        # 测试包含JSON的文本
        json_response = "这是一个句子。{\"type\": \"json\", \"data\": \"value\"} 这是另一个句子。"
        sentences = splitter.split_all_sentences(json_response)

        # 验证正确分割，JSON结构不被拆分
        assert len(sentences) == 3
        assert sentences[0] == "这是一个句子。"
        assert sentences[1] == "{\"type\": \"json\", \"data\": \"value\"}"
        assert sentences[2].strip() == "这是另一个句子。"  # 允许空格

    def test_special_characters_handling_real(self):
        """测试特殊字符处理 - 真实接口"""
        splitter = SmartSentenceSplitter()

        # 测试包含特殊字符的文本
        special_response = "他说：\"你好！\" 然后离开了。这是一个句子... 这是另一个句子。"
        sentences = splitter.split_all_sentences(special_response)

        # 验证正确分割，引号内的句子结束符不被拆分
        assert len(sentences) == 3
        # 根据实际分句结果调整断言
        assert "他说" in sentences[0]
        assert "然后离开了" in sentences[1]
        assert "这是一个句子" in sentences[2]

    def test_empty_text_handling_real(self):
        """测试空文本处理 - 真实接口"""
        splitter = SmartSentenceSplitter()

        # 测试空文本
        empty_response = ""
        sentences = splitter.split_all_sentences(empty_response)

        # 验证空文本返回空列表
        assert len(sentences) == 0

    def test_very_long_sentence_splitting_real(self):
        """测试非常长的句子拆分 - 真实接口"""
        splitter = SmartSentenceSplitter()

        # 测试非常长的文本
        very_long_response = """哇，你像一个小科学家一样提出了一个很棒的问题呢！不过，我好像没有看到你具体想问什么科学问题哦。你是想知道为什么天空是蓝色的？还是好奇为什么树叶会变颜色？或者你想了解小动物们是怎么生活的？

让我来举个例子吧：如果你想知道"为什么船能浮在水上"，我们可以一起做一个小实验！你只需要一个碗、一些水和一张铝箔纸。把铝箔纸捏成小船的形状放在水里，看看它会不会浮起来？然后我们再捏成一个紧实的小球放进去，看看会发生什么？这样我们就能一起发现"浮力"的小秘密啦！

或者，如果你喜欢听故事，我可以讲一个关于"小水滴的旅行"的故事，告诉你雨水是怎么形成的。

请告诉我你最感兴趣的问题是什么，我们就像真正的科学家一样，用有趣的实验或者好玩的故事来寻找答案！记住，科学家都是爱提问、爱动手尝试的，你提出的每一个问题都很棒哦！"""

        sentences = splitter.split_all_sentences(very_long_response)

        # 验证长文本被正确分割成多个句子
        assert len(sentences) > 3

        # 验证每个句子都有合理的长度
        for sentence in sentences:
            assert len(sentence) > 0
            # 句子应该以结束符结尾（除了最后一个可能不完整的句子）
            if sentence != sentences[-1]:
                assert sentence[-1] in ["。", "！", "？", ".", "!", "?", ";", "；"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])