#!/usr/bin/env python3
"""
轻量级LangGraph多智能体系统测试脚本

使用魔搭社区API调用真实模型，优化资源消耗：
1. 简化日志输出，减少emoji使用
2. 优化模型调用参数，降低token消耗
3. 提供清晰的处理流程展示

运行方式：
cd backend && .venv/Scripts/python lightweight_system_test.py
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys
import os

# 设置UTF-8编码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_processing.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class LightweightSystemTester:
    """轻量级系统测试器"""

    def __init__(self):
        self.test_user_id = "lightweight_user_001"
        self.test_session_id = f"session_{int(time.time())}"
        self.conversation_history = []

        # 初始化系统组件
        try:
            from agents.multi_agent import multi_agent, InputType
            from memory.mem0 import story_memory_manager
            from config.settings import settings

            self.multi_agent = multi_agent
            self.memory_manager = story_memory_manager
            self.settings = settings
            self.InputType = InputType

            logger.info("系统组件初始化成功")
            logger.info(f"使用API: {self.settings.openai_base_url}")
            logger.info(f"使用模型: deepseek-chat")

        except Exception as e:
            logger.error(f"系统初始化失败: {e}")
            raise

    async def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        处理用户输入，经过完整的LangGraph状态图处理

        Args:
            user_input: 用户输入文本

        Returns:
            处理结果
        """
        logger.info("=" * 60)
        logger.info(f"开始处理用户输入: '{user_input}'")
        logger.info("=" * 60)

        start_time = time.time()

        try:
            # 记录处理开始
            logger.info("步骤1: 输入预处理")
            logger.info(f"   用户ID: {self.test_user_id}")
            logger.info(f"   会话ID: {self.test_session_id}")
            logger.info(f"   输入长度: {len(user_input)} 字符")

            # 调用多智能体系统处理
            logger.info("步骤2: LangGraph状态图处理开始")
            logger.info("   将输入传递给多智能体系统...")

            result = await self.multi_agent.process_message(
                user_message=user_input,
                user_id=self.test_user_id,
                session_id=self.test_session_id,
                input_type=self.InputType.TEXT
            )

            processing_time = time.time() - start_time

            # 记录处理结果
            logger.info("步骤3: 处理结果分析")
            logger.info(f"   处理成功: {result.get('success', False)}")
            logger.info(f"   响应模式: {result.get('mode', 'unknown')}")
            logger.info(f"   识别意图: {result.get('intent', 'unknown')}")
            logger.info(f"   处理耗时: {processing_time:.2f} 秒")

            # 分析安全检查
            safety_check = result.get('safety_check', {})
            if safety_check:
                logger.info("   安全检查结果:")
                logger.info(f"     内容安全: {safety_check.get('is_safe', True)}")
                if not safety_check.get('is_safe', True):
                    logger.warning(f"     安全问题: {safety_check.get('reasons', [])}")

            # 分析情感状态
            emotion_analysis = result.get('emotion_analysis', {})
            if emotion_analysis:
                logger.info("   情感分析结果:")
                logger.info(f"     情感类型: {emotion_analysis.get('emotion_type', 'unknown')}")
                logger.info(f"     置信度: {emotion_analysis.get('confidence', 0):.2f}")

            # 检查是否有世界观创建
            world_context = result.get('world_context')
            if world_context:
                logger.info("世界观数据:")
                logger.info(f"   世界名称: {world_context.get('world_name', '未知')}")
                logger.info(f"   世界类型: {world_context.get('world_type', '未知')}")
                logger.info(f"   包含角色: {', '.join(world_context.get('roles', []))}")

            # 检查是否有角色互动
            role_context = result.get('role_context')
            if role_context:
                logger.info("角色数据:")
                active_roles = role_context.get('active_roles', [])
                logger.info(f"   活跃角色数量: {len(active_roles)}")
                for i, role in enumerate(active_roles[:2], 1):  # 只显示前2个角色
                    logger.info(f"   角色{i}: {role.get('name', '未知')}")

            # 记录最终响应
            response = result.get('response', '无响应')
            logger.info("最终响应:")
            logger.info(f"   响应长度: {len(response)} 字符")
            logger.info(f"   响应内容: {response[:150]}{'...' if len(response) > 150 else ''}")

            # 记录到对话历史
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "system_response": response,
                "processing_time": processing_time,
                "mode": result.get('mode', 'unknown'),
                "intent": result.get('intent', 'unknown'),
                "success": result.get('success', False)
            })

            logger.info("=" * 60)
            logger.info("处理完成")
            logger.info("=" * 60)

            return result

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"处理失败: {e}")
            logger.error(f"   处理耗时: {processing_time:.2f} 秒")

            error_result = {
                "success": False,
                "response": f"处理失败: {str(e)}",
                "error": str(e),
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            }

            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "system_response": error_result["response"],
                "processing_time": processing_time,
                "mode": "error",
                "intent": "error",
                "success": False
            })

            return error_result

    def print_model_usage_info(self):
        """打印模型使用信息"""
        logger.info("模型调用信息:")
        logger.info("   所有智能体都通过openai_client调用模型")
        logger.info("   配置来源: backend/.env")
        logger.info("   API_KEY: 魔搭社区API密钥")
        logger.info("   BASE_URL: https://api.modelscope.cn/v1")
        logger.info("   模型名称: deepseek-chat")

    def print_system_info(self):
        """打印系统信息"""
        logger.info("系统信息:")
        logger.info(f"   用户ID: {self.test_user_id}")
        logger.info(f"   会话ID: {self.test_session_id}")
        logger.info(f"   API地址: {self.settings.openai_base_url}")
        logger.info(f"   使用Ollama: {self.settings.use_ollama}")

        # 打印模型调用统计
        logger.info("   模型调用统计:")
        logger.info("     意图识别智能体: 使用AI模型进行意图分析")
        logger.info("     世界观智能体: 使用AI模型生成世界观")
        logger.info("     角色智能体: 使用AI模型进行角色回应")
        logger.info("     安全智能体: 使用AI模型进行内容检查")
        logger.info("     情感智能体: 使用AI模型进行情感分析")

    def print_conversation_summary(self):
        """打印对话总结"""
        if not self.conversation_history:
            logger.info("暂无对话历史")
            return

        logger.info("对话总结:")
        total_messages = len(self.conversation_history)
        successful_messages = sum(1 for msg in self.conversation_history if msg['success'])
        avg_time = sum(msg['processing_time'] for msg in self.conversation_history) / total_messages

        logger.info(f"   总对话轮数: {total_messages}")
        logger.info(f"   成功处理: {successful_messages}")
        logger.info(f"   成功率: {successful_messages/total_messages*100:.1f}%")
        logger.info(f"   平均处理时间: {avg_time:.2f} 秒")

        # 按模式统计
        mode_stats = {}
        for msg in self.conversation_history:
            mode = msg['mode']
            if mode not in mode_stats:
                mode_stats[mode] = {'count': 0, 'success': 0}
            mode_stats[mode]['count'] += 1
            if msg['success']:
                mode_stats[mode]['success'] += 1

        logger.info("   按模式统计:")
        for mode, stats in mode_stats.items():
            success_rate = stats['success'] / stats['count'] * 100
            logger.info(f"     {mode}: {stats['success']}/{stats['count']} ({success_rate:.1f}%)")

    async def interactive_mode(self):
        """交互式模式"""
        logger.info("进入交互式测试模式")
        logger.info("可用命令:")
        logger.info("   - 输入任意文本与系统对话")
        logger.info("   - 输入 'model_info' 查看模型调用信息")
        logger.info("   - 输入 'system_info' 查看系统信息")
        logger.info("   - 输入 'summary' 查看对话总结")
        logger.info("   - 输入 'quit' 或 'exit' 退出")
        logger.info("=" * 60)

        self.print_system_info()

        while True:
            try:
                # 获取用户输入
                user_input = input("\n请输入您的消息 (或输入命令): ").strip()

                if not user_input:
                    continue

                # 处理命令
                if user_input.lower() in ['quit', 'exit', '退出']:
                    logger.info("感谢使用，再见！")
                    break

                elif user_input.lower() == 'model_info':
                    self.print_model_usage_info()

                elif user_input.lower() == 'system_info':
                    self.print_system_info()

                elif user_input.lower() == 'summary':
                    self.print_conversation_summary()

                else:
                    # 正常对话处理
                    await self.process_user_input(user_input)

            except KeyboardInterrupt:
                logger.info("\n检测到中断信号，退出程序")
                break
            except EOFError:
                logger.info("\n检测到输入结束，继续运行程序")
                continue
            except Exception as e:
                logger.error(f"处理输入时发生错误: {e}")
                continue

        # 程序结束时的总结
        logger.info("=" * 60)
        logger.info("最终测试总结")
        logger.info("=" * 60)
        self.print_conversation_summary()
        logger.info(f"详细日志已保存到: system_processing.log")

async def main():
    """主函数"""
    logger.info("启动轻量级LangGraph多智能体系统测试")
    logger.info("=" * 60)

    try:
        tester = LightweightSystemTester()
        await tester.interactive_mode()

    except Exception as e:
        logger.error(f"系统启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())