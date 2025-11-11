#!/usr/bin/env python3
"""
交互式LangGraph多智能体系统测试脚本

使用魔搭社区API调用真实模型，验证完整的LangGraph状态图处理流程：
1. 终端交互式输入
2. LangGraph状态图处理
3. 多智能体协同工作
4. 详细流程日志记录

运行方式：
cd backend && .venv/Scripts/python interactive_system_test.py
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('langgraph_processing.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class InteractiveSystemTester:
    """交互式系统测试器"""

    def __init__(self):
        self.test_user_id = "interactive_user_001"
        self.test_session_id = f"session_{int(time.time())}"
        self.conversation_history = []

        # 初始化系统组件
        try:
            from agents.multi_agent import multi_agent
            from memory.mem0 import story_memory_manager
            from config.settings import settings

            self.multi_agent = multi_agent
            self.memory_manager = story_memory_manager
            self.settings = settings

            logger.info("✅ 系统组件初始化成功")
            logger.info(f"📊 使用API: {self.settings.openai_base_url}")
            logger.info(f"🔧 使用模型: deepseek-chat")

        except Exception as e:
            logger.error(f"❌ 系统初始化失败: {e}")
            raise

    async def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        处理用户输入，经过完整的LangGraph状态图处理

        Args:
            user_input: 用户输入文本

        Returns:
            处理结果
        """
        logger.info("=" * 80)
        logger.info(f"🚀 开始处理用户输入: '{user_input}'")
        logger.info("=" * 80)

        start_time = time.time()

        try:
            # 记录处理开始
            logger.info("📋 步骤1: 输入预处理")
            logger.info(f"   用户ID: {self.test_user_id}")
            logger.info(f"   会话ID: {self.test_session_id}")
            logger.info(f"   输入长度: {len(user_input)} 字符")

            # 调用多智能体系统处理
            logger.info("📋 步骤2: LangGraph状态图处理开始")
            logger.info("   将输入传递给多智能体系统...")

            result = await self.multi_agent.process_message(
                user_message=user_input,
                user_id=self.test_user_id,
                session_id=self.test_session_id,
                input_type=self.multi_agent.InputType.TEXT
            )

            processing_time = time.time() - start_time

            # 记录处理结果
            logger.info("📋 步骤3: 处理结果分析")
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
                logger.info("🎯 世界观创建检测:")
                logger.info(f"   世界名称: {world_context.get('world_name', '未知')}")
                logger.info(f"   世界类型: {world_context.get('world_type', '未知')}")
                logger.info(f"   包含角色: {', '.join(world_context.get('roles', []))}")

                # 记录世界观存储
                logger.info("📚 世界观记忆存储:")
                if self.memory_manager.memory_client:
                    try:
                        memory_id = self.memory_manager.store_world_memory(
                            world_data=world_context,
                            user_id=self.test_user_id,
                            story_id=self.test_session_id
                        )
                        logger.info(f"   记忆ID: {memory_id}")
                    except Exception as e:
                        logger.error(f"   世界观存储失败: {e}")

            # 检查是否有角色互动
            role_context = result.get('role_context')
            if role_context:
                logger.info("🎭 角色互动检测:")
                active_roles = role_context.get('active_roles', [])
                logger.info(f"   活跃角色数量: {len(active_roles)}")
                for i, role in enumerate(active_roles[:3], 1):  # 显示前3个角色
                    logger.info(f"   角色{i}: {role.get('name', '未知')} - {role.get('personality', '未知')}")

            # 记录最终响应
            response = result.get('response', '无响应')
            logger.info("💬 最终响应:")
            logger.info(f"   响应长度: {len(response)} 字符")
            logger.info(f"   响应内容: {response[:200]}{'...' if len(response) > 200 else ''}")

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

            # 检查语音元数据
            voice_metadata = result.get('voice_metadata')
            if voice_metadata:
                logger.info("🔊 语音处理信息:")
                logger.info(f"   输入类型: {voice_metadata.get('input_type', 'text')}")
                logger.info(f"   语音服务可用: {voice_metadata.get('stt_available', False)}")

            logger.info("=" * 80)
            logger.info("✅ 处理完成")
            logger.info("=" * 80)

            return result

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ 处理失败: {e}")
            logger.error(f"   处理耗时: {processing_time:.2f} 秒")

            # 记录错误结果
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

    async def test_intent_recognition_flow(self, test_input: str):
        """专门测试意图识别流程"""
        logger.info("🔍 专门测试意图识别流程")

        try:
            from agents.intent_agent import intent_agent

            # 预处理
            content_clean = intent_agent._preprocess_content(test_input)
            logger.info(f"预处理后内容: '{content_clean}'")

            # 检测唤醒词
            wakeup_detected = intent_agent._check_wakeup_words(content_clean)
            logger.info(f"唤醒词检测: {wakeup_detected}")

            # 提取实体
            entities = intent_agent._extract_entities(content_clean)
            logger.info(f"提取实体: {entities}")

            # 关键词分类
            keyword_intent = intent_agent._classify_by_keywords(content_clean)
            logger.info(f"关键词分类: {keyword_intent}")

            # AI分析
            ai_analysis = intent_agent._ai_intent_analysis(content_clean, self.test_user_id)
            logger.info(f"AI分析结果: {ai_analysis}")

            # 最终意图
            final_result = intent_agent.detect_intent(test_input, self.test_user_id)
            logger.info(f"最终意图识别: {final_result}")

        except Exception as e:
            logger.error(f"意图识别测试失败: {e}")

    async def test_memory_system(self):
        """测试记忆系统功能"""
        logger.info("🧠 测试记忆系统功能")

        if not self.memory_manager.memory_client:
            logger.warning("mem0客户端不可用，跳过记忆测试")
            return

        try:
            # 测试存储用户偏好
            preference_data = {
                "type": "story_theme",
                "content": "魔法主题",
                "value": "magic"
            }

            success = self.memory_manager.update_user_preferences(
                self.test_user_id, preference_data
            )
            logger.info(f"用户偏好存储: {'成功' if success else '失败'}")

            # 测试搜索记忆
            search_results = self.memory_manager.search_relevant_memories(
                query="用户喜欢什么类型的故事？",
                user_id=self.test_user_id,
                limit=3
            )
            logger.info(f"记忆搜索结果: 找到 {len(search_results)} 条相关记忆")
            for i, result in enumerate(search_results, 1):
                logger.info(f"  记忆{i}: {result.content[:50]}...")

        except Exception as e:
            logger.error(f"记忆系统测试失败: {e}")

    def print_system_info(self):
        """打印系统信息"""
        logger.info("📊 系统信息:")
        logger.info(f"   用户ID: {self.test_user_id}")
        logger.info(f"   会话ID: {self.test_session_id}")
        logger.info(f"   API地址: {self.settings.openai_base_url}")
        logger.info(f"   使用Ollama: {self.settings.use_ollama}")

        if hasattr(self.multi_agent, 'get_system_statistics'):
            stats = self.multi_agent.get_system_statistics()
            logger.info("   系统统计:")
            logger.info(f"     活跃故事会话: {stats.get('active_story_sessions', 0)}")
            logger.info(f"     总处理会话数: {stats.get('total_sessions_processed', 0)}")

    def print_conversation_summary(self):
        """打印对话总结"""
        if not self.conversation_history:
            logger.info("📝 暂无对话历史")
            return

        logger.info("📝 对话总结:")
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
        logger.info("🎮 进入交互式测试模式")
        logger.info("💡 输入提示:")
        logger.info("   - 输入任意文本与系统对话")
        logger.info("   - 输入 'test_intent' 测试意图识别")
        logger.info("   - 输入 'test_memory' 测试记忆系统")
        logger.info("   - 输入 'info' 查看系统信息")
        logger.info("   - 输入 'summary' 查看对话总结")
        logger.info("   - 输入 'quit' 或 'exit' 退出")
        logger.info("=" * 80)

        self.print_system_info()

        while True:
            try:
                # 获取用户输入
                user_input = input("\n🗣️  请输入您的消息 (或输入命令): ").strip()

                if not user_input:
                    continue

                # 处理命令
                if user_input.lower() in ['quit', 'exit', '退出']:
                    logger.info("👋 感谢使用，再见！")
                    break

                elif user_input.lower() == 'test_intent':
                    test_text = "我想创建一个魔法森林的世界"
                    logger.info(f"🧪 测试意图识别: '{test_text}'")
                    await self.test_intent_recognition_flow(test_text)

                elif user_input.lower() == 'test_memory':
                    await self.test_memory_system()

                elif user_input.lower() == 'info':
                    self.print_system_info()

                elif user_input.lower() == 'summary':
                    self.print_conversation_summary()

                else:
                    # 正常对话处理
                    await self.process_user_input(user_input)

            except KeyboardInterrupt:
                logger.info("\n👋 检测到中断信号，退出程序")
                break
            except EOFError:
                logger.info("\n👋 检测到输入结束，退出程序")
                break
            except Exception as e:
                logger.error(f"❌ 处理输入时发生错误: {e}")

        # 程序结束时的总结
        logger.info("=" * 80)
        logger.info("📊 最终测试总结")
        logger.info("=" * 80)
        self.print_conversation_summary()
        logger.info(f"📄 详细日志已保存到: langgraph_processing.log")

async def main():
    """主函数"""
    logger.info("🚀 启动交互式LangGraph多智能体系统测试")
    logger.info("=" * 80)

    try:
        tester = InteractiveSystemTester()
        await tester.interactive_mode()

    except Exception as e:
        logger.error(f"❌ 系统启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())