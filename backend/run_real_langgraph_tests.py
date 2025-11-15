#!/usr/bin/env python3
"""
LangGraph Routes 真实接口测试运行器

运行真实的API接口测试，不使用Mock对象
"""

import sys
import argparse
import subprocess
import os
import time


def run_tests(args):
    """运行测试"""
    # 设置测试文件路径
    test_file = "tests/test_langgraph_routes_real.py"

    # 构建pytest命令
    cmd = ["python", "-m", "pytest", test_file]

    if args.verbose:
        cmd.append("-v")

    if args.class_name:
        cmd.extend(["-k", args.class_name])

    if args.coverage:
        cmd.extend([
            "--cov=api.langgraph_routes",
            "--cov=agents.multi_agent",
            "--cov=agents",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])

    if args.markers:
        cmd.extend(["-m", args.markers])

    if args.slow:
        cmd.extend(["-m", "not slow"])  # 跳过慢速测试

    # 运行测试
    print(f"运行真实接口测试...")
    print(f"命令: {' '.join(cmd)}")
    print("=" * 60)

    start_time = time.time()
    try:
        result = subprocess.run(cmd, cwd=os.path.dirname(__file__))
        end_time = time.time()

        print("=" * 60)
        print(f"测试完成，耗时: {end_time - start_time:.2f}秒")
        return result.returncode
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        return 1
    except Exception as e:
        print(f"运行测试时出错: {e}")
        return 1


def check_dependencies():
    """检查依赖"""
    required_packages = [
        "pytest",
        "fastapi",
        "sqlalchemy",
        "pydantic"
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"错误: 缺少依赖包: {', '.join(missing)}")
        print("请运行: pip install " + " ".join(missing))
        return False

    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="LangGraph Routes 真实接口测试运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                              # 运行所有真实接口测试
  %(prog)s --verbose                    # 详细输出
  %(prog)s --class TestChatReal        # 只运行聊天测试
  %(prog)s --coverage                   # 生成覆盖率报告
  %(prog)s --slow                       # 跳过慢速测试
        """
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出测试结果"
    )

    parser.add_argument(
        "--class", "-c",
        dest="class_name",
        help="只运行指定的测试类 (例如: TestChatReal)"
    )

    parser.add_argument(
        "--coverage",
        action="store_true",
        help="生成测试覆盖率报告"
    )

    parser.add_argument(
        "--markers", "-m",
        help="按标记运行测试 (例如: 'not slow')"
    )

    parser.add_argument(
        "--slow",
        action="store_true",
        help="跳过慢速测试"
    )

    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="检查依赖包"
    )

    parser.add_argument(
        "--list-tests",
        action="store_true",
        help="列出所有可用的测试"
    )

    args = parser.parse_args()

    if args.check_deps:
        if check_dependencies():
            print("✅ 所有依赖都已安装")
            return 0
        else:
            return 1

    if args.list_tests:
        # 列出所有测试
        cmd = ["python", "-m", "pytest", "tests/test_langgraph_routes_real.py", "--collect-only"]
        subprocess.run(cmd, cwd=os.path.dirname(__file__))
        return 0

    # 检查依赖
    if not check_dependencies():
        return 1

    # 检查测试文件是否存在
    test_file = os.path.join(os.path.dirname(__file__), "tests/test_langgraph_routes_real.py")
    if not os.path.exists(test_file):
        print(f"错误: 测试文件不存在: {test_file}")
        return 1

    # 检查API服务是否可用
    print("检查API服务...")
    try:
        from main import app
        print("✅ API应用加载成功")
    except Exception as e:
        print(f"❌ API应用加载失败: {e}")
        return 1

    # 运行测试
    return run_tests(args)


if __name__ == "__main__":
    sys.exit(main())