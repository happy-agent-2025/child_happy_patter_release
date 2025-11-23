"""
记忆系统集成测试用例

严格遵循TDD模式，真实测试记忆系统的功能集成
"""

import pytest
import json

# 测试记忆系统导入和接口存在性
class TestMemorySystemImports:
    """测试记忆系统相关导入和接口存在性"""

    def test_memory_agent_import(self):
        """测试MemoryAgent导入"""
        try:
            from agents.memory_agent import MemoryAgent
            # 如果导入成功，验证基本方法存在
            assert hasattr(MemoryAgent, 'store_conversation')
            assert hasattr(MemoryAgent, 'get_conversation_history')
            assert hasattr(MemoryAgent, 'summarize_conversation_history')
            assert hasattr(MemoryAgent, 'process_request')
        except ImportError as e:
            # 这是预期的失败，符合TDD的红阶段
            pytest.fail(f"MemoryAgent导入失败: {e}")

    def test_memory_agent_initialization(self):
        """测试MemoryAgent初始化"""
        try:
            from agents.memory_agent import MemoryAgent
            memory_agent = MemoryAgent()

            # 验证初始化后的属性
            assert hasattr(memory_agent, 'conversation_history')
            assert isinstance(memory_agent.conversation_history, list)
        except ImportError as e:
            pytest.fail(f"MemoryAgent初始化测试失败: {e}")

# 测试记忆系统功能
class TestMemorySystemFunctionality:
    """测试记忆系统功能"""

    def test_store_conversation_functionality(self):
        """测试对话存储功能"""
        try:
            from agents.memory_agent import MemoryAgent
            memory_agent = MemoryAgent()

            # 测试存储对话记录
            conversation = {
                "user_id": "test_user_123",
                "session_id": "test_session_456",
                "content": "测试对话内容",
                "response": "测试AI响应",
                "timestamp": "2025-01-01T10:00:00Z",
                "agent": "general_chat"
            }

            memory_agent.store_conversation(conversation)

            # 验证对话已存储
            assert len(memory_agent.conversation_history) == 1
            stored_conversation = memory_agent.conversation_history[0]
            assert stored_conversation["user_id"] == "test_user_123"
            assert stored_conversation["content"] == "测试对话内容"
        except ImportError as e:
            pytest.fail(f"对话存储功能测试失败: {e}")

    def test_get_conversation_history_functionality(self):
        """测试获取对话历史功能"""
        try:
            from agents.memory_agent import MemoryAgent
            memory_agent = MemoryAgent()

            # 添加多个对话记录
            for i in range(5):
                conversation = {
                    "user_id": "test_user_123",
                    "session_id": "test_session_456",
                    "content": f"测试对话内容{i}",
                    "response": f"测试AI响应{i}",
                    "timestamp": f"2025-01-01T10:00:0{i}Z",
                    "agent": "general_chat"
                }
                memory_agent.store_conversation(conversation)

            # 测试获取历史记录
            history = memory_agent.get_conversation_history(limit=3)
            assert len(history) == 3
            assert history[0]["content"] == "测试对话内容4"  # 最新的记录
            assert history[2]["content"] == "测试对话内容2"  # 最旧的记录
        except ImportError as e:
            pytest.fail(f"获取对话历史功能测试失败: {e}")

    def test_clear_conversation_history_functionality(self):
        """测试清空对话历史功能"""
        try:
            from agents.memory_agent import MemoryAgent
            memory_agent = MemoryAgent()

            # 添加对话记录
            conversation = {
                "user_id": "test_user_123",
                "session_id": "test_session_456",
                "content": "测试对话内容",
                "response": "测试AI响应",
                "timestamp": "2025-01-01T10:00:00Z",
                "agent": "general_chat"
            }
            memory_agent.store_conversation(conversation)

            # 验证记录已添加
            assert len(memory_agent.conversation_history) == 1

            # 清空历史
            memory_agent.clear_conversation_history()

            # 验证历史已清空
            assert len(memory_agent.conversation_history) == 0
        except ImportError as e:
            pytest.fail(f"清空对话历史功能测试失败: {e}")

    def test_get_context_functionality(self):
        """测试获取上下文功能"""
        try:
            from agents.memory_agent import MemoryAgent
            memory_agent = MemoryAgent()

            # 添加对话记录
            for i in range(3):
                conversation = {
                    "user_id": "test_user_123",
                    "session_id": "test_session_456",
                    "content": f"测试对话内容{i}",
                    "response": f"测试AI响应{i}",
                    "timestamp": f"2025-01-01T10:00:0{i}Z",
                    "agent": "general_chat"
                }
                memory_agent.store_conversation(conversation)

            # 测试获取上下文
            context = memory_agent.get_context()

            assert "history_count" in context
            assert "recent_history" in context
            assert context["history_count"] == 3
            assert len(context["recent_history"]) == 3
        except ImportError as e:
            pytest.fail(f"获取上下文功能测试失败: {e}")

    def test_process_request_functionality(self):
        """测试处理请求功能"""
        try:
            from agents.memory_agent import MemoryAgent
            memory_agent = MemoryAgent()

            # 测试存储请求
            store_request = {
                "action": "store",
                "user_id": "test_user_123",
                "conversation": {
                    "content": "测试对话内容",
                    "response": "测试AI响应",
                    "agent": "general_chat"
                }
            }

            result = memory_agent.process_request(store_request)
            assert result["status"] == "processed"
            assert result["action"] == "store"

            # 测试获取历史请求
            get_history_request = {
                "action": "get_history",
                "user_id": "test_user_123",
                "limit": 5
            }

            result = memory_agent.process_request(get_history_request)
            assert result["status"] == "processed"
            assert result["action"] == "get_history"
            assert "history" in result
            assert len(result["history"]) == 1

        except ImportError as e:
            pytest.fail(f"处理请求功能测试失败: {e}")

# 测试记忆系统与LangGraph集成
class TestMemorySystemLangGraphIntegration:
    """测试记忆系统与LangGraph集成"""

    def test_langgraph_memory_update_method_exists(self):
        """测试LangGraph中记忆更新方法存在性"""
        from agents.langgraph_workflow import HappyPartnerGraph
        graph = HappyPartnerGraph()

        # 验证方法存在
        assert hasattr(graph, '_update_memory')
        assert hasattr(graph, '_update_session_memory')

    def test_langgraph_memory_update_method_signature(self):
        """测试LangGraph记忆更新方法签名"""
        from agents.langgraph_workflow import HappyPartnerGraph
        graph = HappyPartnerGraph()

        # 验证方法参数
        import inspect
        sig = inspect.signature(graph._update_memory)
        params = list(sig.parameters.keys())
        assert 'state' in params

    def test_langgraph_conversation_history_management(self):
        """测试LangGraph对话历史管理"""
        from agents.langgraph_workflow import HappyPartnerGraph
        graph = HappyPartnerGraph()

        # 创建测试状态
        test_state = {
            "user_id": "test_user_123",
            "session_id": "test_session_456",
            "original_content": "测试对话内容",
            "content": "测试对话内容",
            "final_response": "测试AI响应内容",
            "target_agent": "general_chat",
            "agent_results": {"intent": "test_intent"},
            "conversation_history": [],
            "session_memory": {}
        }

        # 测试记忆更新
        updated_state = graph._update_memory(test_state)

        # 验证对话历史已更新
        assert len(updated_state["conversation_history"]) == 1
        conversation_record = updated_state["conversation_history"][0]
        assert conversation_record["user_id"] == "test_user_123"
        assert conversation_record["original_content"] == "测试对话内容"

# 运行所有测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])