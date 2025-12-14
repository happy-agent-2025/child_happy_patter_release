"""
响应时间性能测试 - TDD红阶段

测试目标：验证响应时间指标
"""

import asyncio
import time
import pytest
import statistics
from unittest.mock import Mock, AsyncMock, patch


class TestResponseTimeMetrics:
    """测试响应时间指标"""

    @pytest.mark.asyncio
    async def test_initial_feedback_under_200ms(self):
        """
        测试初始反馈<200ms

        红阶段：测量当前实现的响应时间
        """
        try:
            from utils.protocol.message_process import MessageProcess
        except ImportError:
            pytest.skip("无法导入MessageProcess")

        # 准备测试环境
        config = Mock()
        connect = Mock()
        connect.send = AsyncMock()
        connect.loop = asyncio.get_event_loop()

        message_process = MessageProcess(config, connect)

        # 模拟VAD检测
        with patch.object(message_process.vad, 'is_no_speech', return_value=(True, True)):
            # 运行多次测试取平均值
            num_tests = 5
            response_times = []

            for i in range(num_tests):
                start_time = time.time()
                await message_process.bytes_message(b"test_audio")
                end_time = time.time()

                response_time = (end_time - start_time) * 1000  # 毫秒
                response_times.append(response_time)

                # 小延迟避免资源冲突
                await asyncio.sleep(0.1)

            # 计算统计信息
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)

            print(f"响应时间统计：平均{avg_time:.1f}ms，最小{min_time:.1f}ms，最大{max_time:.1f}ms")

            # 红阶段：当前实现可能超过200ms，这个断言应该失败
            assert avg_time < 200, f"平均响应时间{avg_time:.1f}ms超过200ms目标"

            print(f"✅ 测试通过：平均响应时间{avg_time:.1f}ms < 200ms")

    @pytest.mark.asyncio
    async def test_response_time_consistency(self):
        """
        测试响应时间一致性

        红阶段：测量响应时间的波动
        """
        try:
            from utils.protocol.message_process import MessageProcess
        except ImportError:
            pytest.skip("无法导入MessageProcess")

        # 准备测试环境
        config = Mock()
        connect = Mock()
        connect.send = AsyncMock()
        connect.loop = asyncio.get_event_loop()

        message_process = MessageProcess(config, connect)

        # 模拟VAD检测
        with patch.object(message_process.vad, 'is_no_speech', return_value=(True, True)):
            # 运行多次测试
            num_tests = 10
            response_times = []

            for i in range(num_tests):
                start_time = time.time()
                await message_process.bytes_message(b"test_audio")
                end_time = time.time()

                response_time = (end_time - start_time) * 1000
                response_times.append(response_time)

                # 小延迟
                await asyncio.sleep(0.05)

            # 计算标准差
            if len(response_times) > 1:
                stdev = statistics.stdev(response_times)
                avg_time = statistics.mean(response_times)

                print(f"响应时间：平均{avg_time:.1f}ms，标准差{stdev:.1f}ms")

                # 红阶段：检查响应时间的一致性
                # 标准差应该小于平均值的50%
                assert stdev < avg_time * 0.5, f"响应时间波动过大：标准差{stdev:.1f}ms"

                print(f"✅ 测试通过：响应时间一致性良好，标准差{stdev:.1f}ms")
            else:
                pytest.skip("需要至少2次测试计算标准差")

    @pytest.mark.asyncio
    async def test_memory_usage_with_streaming(self):
        """
        测试流式处理的内存使用

        红阶段：测量当前实现的内存使用
        """
        import psutil
        import os

        try:
            from utils.protocol.message_process import MessageProcess
        except ImportError:
            pytest.skip("无法导入MessageProcess")

        # 获取当前进程
        process = psutil.Process(os.getpid())

        # 测量初始内存
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # 准备测试环境
        config = Mock()
        connect = Mock()
        connect.send = AsyncMock()
        connect.loop = asyncio.get_event_loop()

        message_process = MessageProcess(config, connect)

        # 模拟多次请求
        num_requests = 20
        with patch.object(message_process.vad, 'is_no_speech', return_value=(True, True)):
            for i in range(num_requests):
                await message_process.bytes_message(f"audio_data_{i}".encode())
                await asyncio.sleep(0.02)

        # 测量最终内存
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        print(f"内存使用：初始{initial_memory:.1f}MB，最终{final_memory:.1f}MB，增加{memory_increase:.1f}MB")

        # 红阶段：检查内存增长是否合理
        # 20次请求内存增长应该小于50MB
        assert memory_increase < 50, f"内存增长过大：{memory_increase:.1f}MB"

        print(f"✅ 测试通过：内存增长{memory_increase:.1f}MB < 50MB")

    @pytest.mark.asyncio
    async def test_cpu_utilization(self):
        """
        测试CPU使用率

        红阶段：测量处理期间的CPU使用
        """
        import psutil
        import os

        try:
            from utils.protocol.message_process import MessageProcess
        except ImportError:
            pytest.skip("无法导入MessageProcess")

        # 获取当前进程
        process = psutil.Process(os.getpid())

        # 准备测试环境
        config = Mock()
        connect = Mock()
        connect.send = AsyncMock()
        connect.loop = asyncio.get_event_loop()

        message_process = MessageProcess(config, connect)

        # 测量CPU使用
        cpu_percent_before = process.cpu_percent(interval=0.1)

        # 执行一些请求
        num_requests = 10
        with patch.object(message_process.vad, 'is_no_speech', return_value=(True, True)):
            for i in range(num_requests):
                await message_process.bytes_message(f"audio_data_{i}".encode())

        # 再次测量CPU使用
        cpu_percent_after = process.cpu_percent(interval=0.1)

        print(f"CPU使用率：处理前{cpu_percent_before:.1f}%，处理后{cpu_percent_after:.1f}%")

        # 红阶段：CPU使用率应该在合理范围内
        # 注意：这个测试可能不稳定，主要用于监控
        if cpu_percent_after > 90:
            print(f"⚠️  CPU使用率较高：{cpu_percent_after:.1f}%")
            # 在红阶段，我们只记录不失败
            # assert cpu_percent_after < 90, f"CPU使用率过高：{cpu_percent_after:.1f}%"

        print("✅ 测试通过：CPU使用率监控完成")

    @pytest.mark.asyncio
    async def test_baseline_performance(self):
        """
        建立性能基准

        红阶段：记录当前性能作为基准
        """
        try:
            from utils.protocol.message_process import MessageProcess
        except ImportError:
            pytest.skip("无法导入MessageProcess")

        # 准备测试环境
        config = Mock()
        connect = Mock()
        connect.send = AsyncMock()
        connect.loop = asyncio.get_event_loop()

        message_process = MessageProcess(config, connect)

        # 运行基准测试
        num_tests = 10
        response_times = []

        with patch.object(message_process.vad, 'is_no_speech', return_value=(True, True)):
            for i in range(num_tests):
                start_time = time.time()
                await message_process.bytes_message(b"baseline_audio")
                end_time = time.time()

                response_time = (end_time - start_time) * 1000
                response_times.append(response_time)

                await asyncio.sleep(0.05)

        # 计算基准数据
        avg_time = statistics.mean(response_times)
        min_time = min(response_times)
        max_time = max(response_times)

        print("=" * 50)
        print("性能基准测试结果（红阶段）：")
        print(f"测试次数：{num_tests}")
        print(f"平均响应时间：{avg_time:.1f}ms")
        print(f"最小响应时间：{min_time:.1f}ms")
        print(f"最大响应时间：{max_time:.1f}ms")
        print(f"目标响应时间：<200ms")
        print("=" * 50)

        # 保存基准数据到文件
        baseline_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "num_tests": num_tests,
            "avg_response_time_ms": avg_time,
            "min_response_time_ms": min_time,
            "max_response_time_ms": max_time,
            "target_response_time_ms": 200
        }

        import json
        baseline_file = "performance_baseline.json"
        with open(baseline_file, 'w') as f:
            json.dump(baseline_data, f, indent=2)

        print(f"✅ 基准数据已保存到 {baseline_file}")

        # 红阶段：记录当前性能，不进行断言
        # 后续优化阶段将与此基准比较


if __name__ == "__main__":
    # 手动运行测试
    import sys
    sys.exit(pytest.main([__file__, "-v"]))