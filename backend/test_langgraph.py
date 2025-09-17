#!/usr/bin/env python3
"""
LangGraph工作流测试脚本

测试Happy Partner多代理系统的LangGraph实现
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_langgraph_workflow():
    """测试LangGraph工作流"""
    print("=" * 60)
    print("🤖 Happy Partner LangGraph工作流测试")
    print("=" * 60)

    try:
        # 导入LangGraph工作流
        from agents.langgraph_workflow import happy_partner_graph

        # 测试用例
        test_cases = [
            {
                "name": "教育问答测试",
                "user_id": "test_student_1",
                "content": "1+1等于多少？",
                "session_id": "math_session_001"
            },
            {
                "name": "情感支持测试",
                "user_id": "test_student_2",
                "content": "我今天有点难过，因为考试没考好",
                "session_id": "emotion_session_001"
            },
            {
                "name": "记忆管理测试",
                "user_id": "test_student_3",
                "content": "帮我总结一下我们刚才聊了什么",
                "session_id": "memory_session_001"
            },
            {
                "name": "复杂问题测试",
                "user_id": "test_student_1",
                "content": "什么是光合作用？请用简单的语言解释一下。",
                "session_id": "science_session_001"
            }
        ]

        success_count = 0
        total_count = len(test_cases)

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 测试用例 {i}/{total_count}: {test_case['name']}")
            print("-" * 40)
            print(f"用户输入: {test_case['content']}")
            print(f"用户ID: {test_case['user_id']}")
            print(f"会话ID: {test_case['session_id']}")
            print()

            try:
                # 执行LangGraph工作流
                start_time = datetime.now()
                result = await happy_partner_graph.process_message(
                    user_id=test_case['user_id'],
                    content=test_case['content'],
                    session_id=test_case['session_id']
                )
                end_time = datetime.now()

                # 计算执行时间
                execution_time = (end_time - start_time).total_seconds()

                print("✅ 工作流执行成功！")
                print(f"⏱️  执行时间: {execution_time:.2f}秒")
                print()

                # 显示结果
                print("📊 处理结果:")
                print(f"   最终响应: {result['response'][:100]}...")
                print(f"   目标Agent: {result['metadata'].get('agent', 'unknown')}")
                print(f"   响应类型: {result['metadata'].get('type', 'unknown')}")

                # 显示安全信息
                safety_info = result.get('safety_info', {})
                if safety_info:
                    print(f"   安全检查: {'通过' if safety_info.get('passed', True) else '未通过'}")
                    if not safety_info.get('passed', True):
                        print(f"   安全问题: {safety_info.get('issues', [])}")

                # 显示Agent结果
                agent_results = result.get('agent_results', {})
                if agent_results:
                    print("   Agent处理结果:")
                    for agent_name, agent_result in agent_results.items():
                        print(f"     - {agent_name}: 处理完成")

                success_count += 1

            except Exception as e:
                print(f"❌ 测试失败: {str(e)}")
                import traceback
                traceback.print_exc()

            print("-" * 40)

        # 总结
        print(f"\n📈 测试总结:")
        print(f"   总测试用例: {total_count}")
        print(f"   成功数量: {success_count}")
        print(f"   失败数量: {total_count - success_count}")
        print(f"   成功率: {(success_count/total_count)*100:.1f}%")

        # 显示工作流信息
        print(f"\n🔧 LangGraph工作流信息:")
        try:
            workflow_info = happy_partner_graph.compiled_graph
            if hasattr(workflow_info, 'nodes'):
                print(f"   节点数量: {len(workflow_info.nodes)}")
                print(f"   节点列表: {list(workflow_info.nodes.keys())}")
        except Exception as e:
            print(f"   获取工作流信息失败: {e}")

        return success_count == total_count

    except ImportError as e:
        print(f"❌ 导入LangGraph模块失败: {e}")
        print("   请确保已安装 langgraph>=0.2.0")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_graph_structure():
    """测试图结构"""
    print(f"\n🏗️  测试LangGraph图结构")
    print("-" * 40)

    try:
        from agents.langgraph_workflow import happy_partner_graph

        # 获取图结构信息
        graph = happy_partner_graph.compiled_graph

        print(f"✅ 图对象创建成功")
        print(f"   图类型: {type(graph).__name__}")

        # 显示节点信息
        if hasattr(graph, 'nodes'):
            nodes = list(graph.nodes.keys())
            print(f"   节点数量: {len(nodes)}")
            print(f"   节点列表: {nodes}")

        # 显示边信息
        if hasattr(graph, 'edges'):
            edges = list(graph.edges)
            print(f"   边数量: {len(edges)}")
            for edge in edges[:5]:  # 显示前5条边
                if hasattr(edge, 'source') and hasattr(edge, 'target'):
                    print(f"     {edge.source} -> {edge.target}")
                else:
                    print(f"     {edge}")

        return True

    except Exception as e:
        print(f"❌ 图结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("🚀 开始LangGraph工作流测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 测试图结构
    structure_success = await test_graph_structure()

    # 测试工作流
    workflow_success = await test_langgraph_workflow()

    # 最终结果
    print(f"\n🎯 最终测试结果:")
    print(f"   图结构测试: {'✅ 通过' if structure_success else '❌ 失败'}")
    print(f"   工作流测试: {'✅ 通过' if workflow_success else '❌ 失败'}")

    if structure_success and workflow_success:
        print("\n🎉 所有测试通过！LangGraph实现工作正常。")
        print("\n📝 接下来你可以:")
        print("   1. 启动后端服务: python main.py")
        print("   2. 访问API文档: http://127.0.0.1:8001/docs")
        print("   3. 测试LangGraph接口: /api/langgraph/chat")
        return True
    else:
        print("\n⚠️  部分测试失败，请检查实现。")
        return False

if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(main())
    sys.exit(0 if success else 1)