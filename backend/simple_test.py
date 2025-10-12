#!/usr/bin/env python3
"""
简单系统测试脚本 - 解决编码问题
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys
import os

# 强制设置UTF-8编码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_test.log', encoding='utf-8', errors='replace'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SimpleSystemTester:
    """简化系统测试器"""

    def __init__(self):
        self.test_user_id = "simple_user_001"
        self.test_session_id = f"session_{int(time.time())}"

        # 初始化系统组件
        try:
            from agents.multi_agent import multi_agent, InputType
            from config.settings import settings

            self.multi_agent = multi_agent
            self.settings = settings
            self.InputType = InputType

            logger.info("系统组件初始化成功")
            logger.info(f"使用API: {self.settings.openai_base_url}")

        except Exception as e:
            logger.error(f"系统初始化失败: {e}")
            raise

    async def test_single_message(self, message: str) -> Dict[str, Any]:
        """测试单条消息处理"""
        logger.info("=" * 60)
        logger.info(f"测试消息: {message}")
        logger.info("=" * 60)

        start_time = time.time()

        try:
            # 调用多智能体系统
            result = await self.multi_agent.process_message(
                user_message=message,
                user_id=self.test_user_id,
                session_id=self.test_session_id,
                input_type=self.InputType.TEXT
            )

            processing_time = time.time() - start_time

            # 记录结果
            logger.info(f"处理成功: {result.get('success', False)}")
            logger.info(f"响应模式: {result.get('mode', 'unknown')}")
            logger.info(f"处理耗时: {processing_time:.2f} 秒")

            response = result.get('response', '无响应')
            logger.info(f"响应内容: {response[:200]}{'...' if len(response) > 200 else ''}")

            return result

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"处理失败: {e}")
            return {
                "success": False,
                "response": f"处理失败: {str(e)}",
                "processing_time": processing_time
            }

async def main():
    """主函数"""
    logger.info("启动简单系统测试")
    logger.info("=" * 60)

    try:
        tester = SimpleSystemTester()

        # 测试用例
        test_messages = [
            "你好",
            "我想听一个故事",
            "创建一个魔法世界",
            "再见"
        ]

        for msg in test_messages:
            await tester.test_single_message(msg)
            # 短暂延迟避免API频率限制
            await asyncio.sleep(1)

        logger.info("=" * 60)
        logger.info("测试完成")

    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())