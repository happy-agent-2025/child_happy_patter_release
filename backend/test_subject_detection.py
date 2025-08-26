#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.edu_agent import EduAgent

def test_subject_detection():
    """测试学科判断功能"""
    agent = EduAgent()
    
    # 测试问题
    test_questions = [
        "1+1等于几？",
        "李白写过哪些诗？",
        "如何用英语说'你好'？",
        "植物是如何进行光合作用的？",
        "长城是哪个朝代修建的？",
        "中国的首都在哪里？",
        "钢琴有多少个键？",
        "梵高的代表作是什么？",
        "游泳有哪些好处？",
        "我们应该如何遵守交通规则？",
        "什么是人工智能？"
    ]
    
    print("测试学科判断功能:")
    print("=" * 50)
    
    for question in test_questions:
        subject = agent._get_subject_context(question)
        fallback_subject = agent._fallback_subject_detection(question)
        print(f"问题: {question}")
        print(f"大模型判断学科: {subject}")
        print(f"关键词匹配学科: {fallback_subject}")
        print("-" * 30)

if __name__ == "__main__":
    test_subject_detection()