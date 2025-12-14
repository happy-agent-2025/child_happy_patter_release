#!/usr/bin/env python3
"""
测试导入修复的脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试所有关键导入"""
    print("测试导入修复...")

    try:
        # 测试utils.protocol模块导入
        from utils.protocol.message_process import MessageProcess
        print("✅ MessageProcess 导入成功")

        from utils.protocol.send_message import SendMessage
        print("✅ SendMessage 导入成功")

        from utils.protocol.connect_process import ConnectProcess
        print("✅ ConnectProcess 导入成功")

        from utils.protocol.messge_type import MessageState, MessageType
        print("✅ MessageState/MessageType 导入成功")

        from utils.logger import Logger
        print("✅ Logger 导入成功")

        from utils.Dialogue import Dialogue
        print("✅ Dialogue 导入成功")

        from utils.sentence_splitter import SmartSentenceSplitter
        print("✅ SmartSentenceSplitter 导入成功")

        # 测试agents模块导入
        from agents.langgraph_workflow import happy_partner_graph
        print("✅ happy_partner_graph 导入成功")

        print("\n🎉 所有导入测试通过！")
        return True

    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_message_process_instantiation():
    """测试MessageProcess实例化"""
    print("\n测试MessageProcess实例化...")

    try:
        from unittest.mock import Mock

        config = Mock()
        connect = Mock()

        # 创建MessageProcess实例
        mp = MessageProcess(config, connect)

        print("✅ MessageProcess 实例化成功")
        print(f"  类: {type(mp).__name__}")
        print(f"  方法: {[m for m in dir(mp) if not m.startswith('_')][:10]}...")

        return True

    except Exception as e:
        print(f"❌ 实例化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_immediate_feedback_methods():
    """测试即时反馈方法"""
    print("\n测试即时反馈方法...")

    try:
        from utils.protocol.message_process import MessageProcess
        from unittest.mock import Mock

        config = Mock()
        connect = Mock()
        connect.send = Mock()

        mp = MessageProcess(config, connect)

        # 检查方法是否存在
        methods_to_check = [
            '_send_thinking_message',
            '_play_thinking_audio',
            'bytes_message'
        ]

        for method_name in methods_to_check:
            if hasattr(mp, method_name):
                print(f"✅ 方法存在: {method_name}")
            else:
                print(f"❌ 方法不存在: {method_name}")
                return False

        print("✅ 所有即时反馈方法存在")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("导入修复测试")
    print("=" * 50)

    all_passed = True

    # 运行测试
    all_passed &= test_imports()
    all_passed &= test_message_process_instantiation()
    all_passed &= test_immediate_feedback_methods()

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！导入修复成功。")
    else:
        print("❌ 有些测试失败，请检查导入问题。")
    print("=" * 50)