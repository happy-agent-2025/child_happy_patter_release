"""
真实的儿童对话测试脚本

模拟儿童与系统的完整对话过程，测试故事创建、角色互动等功能。
"""

import asyncio
import logging
import time
from datetime import datetime

from agents.multi_agent import multi_agent, InputType
from agents.role_factory import role_factory

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_realistic_conversation():
    """测试真实的儿童对话流程"""

    user_id = "test_child_001"
    session_id = "story_session_001"

    # 对话场景：儿童创建魔法世界的完整流程
    conversation_scenarios = [
        {
            "name": "创建魔法世界",
            "messages": [
                "我想新创建一个魔法世界！",
                "有魔法师、巫婆、怪物、小矮人",
                "我是勇敢的魔法师，要打倒可怕的怪物",
            ],
        },
        {
            "name": "探索魔法世界",
            "messages": [
                "我想去魔法森林里冒险",
                "魔法森林里有什么神奇的东西？",
                "我想找到发光的魔法石",
                "用我的魔法棒可以找到吗？",
                "太棒了！我们一起去冒险吧！",
            ],
        },
        {
            "name": "角色互动",
            "messages": [
                "小魔法师，你教我魔法吧",
                "我想学飞行术",
                "我们可以骑着扫帚飞吗？",
                "我想和彩虹精灵做朋友",
                "魔法真有趣！",
            ],
        },
    ]

    logger.info("🎭 开始真实的儿童对话测试")
    logger.info("=" * 60)

    # 测试创建魔法世界场景
    scenario = conversation_scenarios[0]  # 创建魔法世界
    logger.info(f"📖 测试场景：{scenario['name']}")

    # 模拟对话流程
    for i, message in enumerate(scenario["messages"]):
        logger.info(f"👶 用户说：{message}")

        start_time = time.time()
        try:
            # 处理消息
            result = await multi_agent.process_message(
                user_message=message,
                user_id=user_id,
                session_id=session_id,
                input_type=InputType.TEXT,
            )

            response_time = time.time() - start_time

            if result["success"]:
                logger.info(f"🤖 系统回应：{result['response']}")
                logger.info(
                    f"📊 响应模式：{result['mode']} | 耗时：{response_time:.2f}秒"
                )

                # 如果是故事模式，显示额外的上下文信息
                if result["mode"] == "story":
                    world_context = result.get("world_context")
                    role_context = result.get("role_context")

                    if world_context:
                        logger.info(
                            f"🌍 世界信息：{world_context.get('world_name', '未知世界')}"
                        )

                    if role_context and role_context.get("active_roles"):
                        active_roles = [
                            role["name"] for role in role_context["active_roles"]
                        ]
                        logger.info(f"👥 活跃角色：{', '.join(active_roles)}")

            else:
                logger.error(f"❌ 处理失败：{result.get('error', '未知错误')}")

        except Exception as e:
            logger.error(f"💥 异常：{str(e)}")

        logger.info("-" * 40)

        # 对话间隔，模拟真实对话节奏
        if i < len(scenario["messages"]) - 1:
            await asyncio.sleep(1)

    # 显示最终状态
    logger.info("📋 对话完成，查看最终状态")

    # 获取会话信息
    session_info = multi_agent.get_session_info(session_id)
    if session_info:
        logger.info(f"📁 会话信息：")
        logger.info(f"   - 世界ID：{session_info['world_id']}")
        logger.info(f"   - 活跃角色数：{session_info['active_roles_count']}")
        logger.info(f"   - 创建时间：{session_info['created_at']}")

    # 获取系统统计
    stats = await multi_agent.get_system_statistics()
    logger.info(f"📊 系统统计：")
    logger.info(f"   - 活跃故事会话：{stats['active_story_sessions']}")
    logger.info(
        f"   - 角色工厂统计：{stats['role_factory_stats'].get('total_roles', 0)}个角色"
    )

    logger.info("✅ 儿童对话测试完成")


async def test_role_interaction():
    """专门测试角色交互功能"""

    logger.info("🎭 专门测试角色交互功能")
    logger.info("=" * 60)

    user_id = "test_child_002"
    session_id = "role_test_session"

    # 先创建一个故事世界
    create_world_msg = "创建一个有魔法师和小精灵的童话世界"

    logger.info(f"👶 用户说：{create_world_msg}")
    result = await multi_agent.process_message(
        user_message=create_world_msg, user_id=user_id, session_id=session_id
    )

    if result["success"]:
        logger.info(f"🤖 系统回应：{result['response']}")
        logger.info(f"📊 响应模式：{result['mode']}")

    # 等待一下，确保世界创建完成
    await asyncio.sleep(2)

    # 测试与角色直接对话
    role_test_messages = [
        "小魔法师，你好！",
        "你能教我什么魔法？",
        "我想学习变成小动物的魔法",
        "我们可以一起去冒险吗？",
        "谢谢你的帮助！",
    ]

    for message in role_test_messages:
        logger.info(f"👶 用户说：{message}")

        start_time = time.time()
        result = await multi_agent.process_message(
            user_message=message, user_id=user_id, session_id=session_id
        )
        response_time = time.time() - start_time

        if result["success"]:
            logger.info(f"🤖 系统回应：{result['response']}")
            logger.info(f"📊 耗时：{response_time:.2f}秒")
        else:
            logger.error(f"❌ 处理失败：{result.get('error', '未知错误')}")

        logger.info("-" * 40)
        await asyncio.sleep(1)

    # 清理会话
    await multi_agent.end_story_session(session_id)
    logger.info("🧹 角色交互测试完成，会话已清理")


async def main():
    """主测试函数"""
    try:
        logger.info("🚀 启动儿童对话系统测试")
        logger.info("=" * 60)

        # 等待系统初始化
        await asyncio.sleep(2)

        # 测试1：真实对话流程
        await test_realistic_conversation()

        logger.info("")

        # 测试2：角色交互
        await test_role_interaction()

        logger.info("")
        logger.info("🎉 所有测试完成！")

    except Exception as e:
        logger.error(f"💥 测试过程中发生异常：{str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
