"""
智能中英文混合文本分句器
支持中英文混合文本的智能分句，处理特殊字符和嵌套结构
"""
import re
from typing import List, Tuple


class SmartSentenceSplitter:
    """智能中英文混合文本分句器"""

    def __init__(self):
        # 中英文句子结束符
        self.sentence_end_chars = {
            # 中文结束符
            '。', '！', '？', '；',
            # 英文结束符
            '.', '!', '?', ';'
        }

        # 特殊序列（不被视为句子结束符）
        self.special_sequences = {
            '...', '……', '--'  # 省略号和破折号
        }

        # 特殊字符处理
        self.special_chars = {
            'quotes': {'"', "'", '“', '”', '‘', '’'},
            'brackets': {'(', ')', '[', ']', '{', '}', '【', '】'},
            'ellipsis': {'...', '……'}
        }

        # 构建正则表达式模式
        self._build_patterns()

        # 性能优化：缓存
        self._quote_cache = {}
        self._bracket_cache = {}

    def clear_cache(self):
        """清理缓存，避免内存泄漏"""
        self._quote_cache.clear()
        self._bracket_cache.clear()

    def _build_patterns(self):
        """构建正则表达式模式"""
        # 句子结束符模式
        end_chars_pattern = '|'.join(re.escape(char) for char in self.sentence_end_chars)
        self.sentence_end_pattern = re.compile(f'({end_chars_pattern})')

        # 特殊字符模式
        quote_chars = ''.join(re.escape(char) for char in self.special_chars['quotes'])
        bracket_chars = ''.join(re.escape(char) for char in self.special_chars['brackets'])

        self.quote_pattern = re.compile(f'[{quote_chars}]')
        self.bracket_pattern = re.compile(f'[{bracket_chars}]')

        # JSON模式
        self.json_pattern = re.compile(r'\{[^{}]*\}|\[[^\[\]]*\]')

    def _is_in_quotes(self, text: str, position: int) -> bool:
        """检查指定位置是否在引号内"""
        # 使用缓存
        cache_key = f"{text[:position+1]}"
        if cache_key in self._quote_cache:
            return self._quote_cache[cache_key]

        quote_stack = []
        for i, char in enumerate(text[:position]):
            if char in self.special_chars['quotes']:
                if not quote_stack or quote_stack[-1] != char:
                    quote_stack.append(char)
                else:
                    quote_stack.pop()

        result = len(quote_stack) > 0
        self._quote_cache[cache_key] = result
        return result

    def _is_in_brackets(self, text: str, position: int) -> bool:
        """检查指定位置是否在括号内"""
        # 使用缓存
        cache_key = f"{text[:position+1]}"
        if cache_key in self._bracket_cache:
            return self._bracket_cache[cache_key]

        bracket_stack = []
        bracket_pairs = {'(': ')', '[': ']', '{': '}', '【': '】'}

        for i, char in enumerate(text[:position]):
            if char in bracket_pairs.keys():
                bracket_stack.append(char)
            elif char in bracket_pairs.values():
                if bracket_stack and bracket_pairs.get(bracket_stack[-1]) == char:
                    bracket_stack.pop()

        result = len(bracket_stack) > 0
        self._bracket_cache[cache_key] = result
        return result

    def _find_quote_end_position(self, text: str, start_pos: int) -> int:
        """查找引号结束位置"""
        if start_pos < 0 or start_pos >= len(text):
            return -1

        # 找到当前位置所在的引号
        quote_stack = []
        for i, char in enumerate(text[:start_pos + 1]):
            if char in self.special_chars['quotes']:
                if not quote_stack or quote_stack[-1] != char:
                    quote_stack.append(char)
                else:
                    quote_stack.pop()

        if not quote_stack:
            return -1

        opening_quote = quote_stack[-1]

        # 从当前位置开始查找匹配的结束引号
        for i in range(start_pos + 1, len(text)):
            if text[i] == opening_quote:
                return i

        return -1

    def _is_valid_sentence_end(self, text: str, position: int) -> bool:
        """检查是否是有效的句子结束位置"""
        if position < 0 or position >= len(text):
            return False

        char = text[position]

        # 检查是否在括号内（引号内的句子结束符应该被视为有效）
        if self._is_in_brackets(text, position):
            return False

        # 检查是否是特殊序列的一部分
        for seq in self.special_sequences:
            seq_len = len(seq)
            # 检查当前位置是否是特殊序列的起始位置
            if position + seq_len <= len(text) and text[position:position+seq_len] == seq:
                return False
            # 检查当前位置是否是特殊序列的中间位置
            for i in range(1, seq_len):
                if position >= i and position - i + seq_len <= len(text):
                    if text[position-i:position-i+seq_len] == seq:
                        return False

        # 检查是否是数字的一部分
        if char == '.' and position > 0 and text[position-1].isdigit():
            return False

        return True

    def _find_json_structures(self, text: str) -> List[Tuple[int, int]]:
        """查找JSON结构的位置"""
        json_positions = []

        # 查找完整的JSON对象
        stack = []
        start_pos = -1

        for i, char in enumerate(text):
            if char in '{[':
                if not stack:
                    start_pos = i
                stack.append(char)
            elif char in '}]':
                if stack:
                    opening_char = stack.pop()
                    if (opening_char == '{' and char == '}') or (opening_char == '[' and char == ']'):
                        if not stack:
                            json_positions.append((start_pos, i))
                            start_pos = -1

        return json_positions

    def get_complete_sentence(self, text_buffer: List[str]) -> Tuple[List[str], str]:
        """
        从文本缓冲区中获取完整的句子

        Args:
            text_buffer: 文本缓冲区列表

        Returns:
            tuple: (remaining_buffer, complete_sentence)
        """
        if not text_buffer:
            return [], ""

        buffer_str = "".join(text_buffer)

        # 首先查找JSON结构
        json_positions = self._find_json_structures(buffer_str)

        if json_positions:
            # 处理JSON结构
            start_pos, end_pos = json_positions[0]

            # 检查JSON结构之前是否有完整的句子
            prefix = buffer_str[:start_pos]
            json_part = buffer_str[start_pos:end_pos + 1]

            # 在prefix中查找句子结束位置
            sentence_end_pos = self._find_sentence_end_position(prefix)

            if sentence_end_pos >= 0:
                # 返回prefix中的完整句子
                complete_sentence = prefix[:sentence_end_pos + 1]
                remaining_text = prefix[sentence_end_pos + 1:] + json_part + buffer_str[end_pos + 1:]
                return [remaining_text] if remaining_text else [], complete_sentence
            else:
                # 返回整个JSON结构
                complete_sentence = json_part
                remaining_text = buffer_str[end_pos + 1:]
                return [remaining_text] if remaining_text else [], complete_sentence

        # 没有JSON结构，按普通文本处理
        sentence_end_pos = self._find_sentence_end_position(buffer_str)

        if sentence_end_pos >= 0:
            # 检查句子结束符是否在引号内
            if self._is_in_quotes(buffer_str, sentence_end_pos):
                # 如果在引号内，找到引号的结束位置
                quote_end_pos = self._find_quote_end_position(buffer_str, sentence_end_pos)
                if quote_end_pos > sentence_end_pos:
                    complete_sentence = buffer_str[:quote_end_pos + 1]
                    remaining_text = buffer_str[quote_end_pos + 1:]
                    return [remaining_text] if remaining_text else [], complete_sentence

            complete_sentence = buffer_str[:sentence_end_pos + 1]
            remaining_text = buffer_str[sentence_end_pos + 1:]
            return [remaining_text] if remaining_text else [], complete_sentence
        else:
            return [], ""

    def _find_sentence_end_position(self, text: str) -> int:
        """查找句子结束位置"""
        if not text:
            return -1

        # 查找所有可能的句子结束位置
        positions = []
        for match in self.sentence_end_pattern.finditer(text):
            position = match.start()
            if self._is_valid_sentence_end(text, position):
                positions.append(position)

        # 返回第一个有效的句子结束位置
        return min(positions) if positions else -1

    def split_all_sentences(self, text: str) -> List[str]:
        """
        将文本分割成所有完整的句子

        Args:
            text: 输入文本

        Returns:
            list: 句子列表
        """
        sentences = []
        buffer = [text]

        while buffer and buffer[0]:
            buffer, sentence = self.get_complete_sentence(buffer)
            if sentence:
                sentences.append(sentence)

        # 如果还有剩余文本，也作为最后一个句子
        if buffer and buffer[0]:
            sentences.append(buffer[0])

        return sentences