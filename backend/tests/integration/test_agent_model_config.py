"""
Agent模型配置集成测试用例

严格遵循TDD模式，真实测试agents系统的独立模型配置功能
"""

import pytest

# 测试统一的LLM客户端接口
class TestLLMClientImports:
    """测试统一的LLM客户端导入和接口存在性"""

    def test_llm_client_import(self):
        """测试LLMClient导入"""
        try:
            from ai_core.llm_client import LLMClient
            # 如果导入成功，验证基本方法存在
            assert hasattr(LLMClient, 'chat_completion')
            assert hasattr(LLMClient, '_call_deepseek')
            assert hasattr(LLMClient, '_call_ollama')
        except ImportError as e:
            # 这是预期的失败，符合TDD的红阶段
            pytest.fail(f"LLMClient导入失败: {e}")

    def test_llm_client_initialization(self):
        """测试LLMClient初始化"""
        try:
            from ai_core.llm_client import LLMClient
            llm_client = LLMClient()

            # 验证初始化后的属性
            assert hasattr(llm_client, 'config')
            assert llm_client._initialized == True
        except ImportError as e:
            pytest.fail(f"LLMClient初始化测试失败: {e}")

    def test_llm_client_singleton(self):
        """测试LLMClient单例模式"""
        try:
            from ai_core.llm_client import LLMClient
            client1 = LLMClient()
            client2 = LLMClient()

            # 验证是同一个实例
            assert client1 is client2
        except ImportError as e:
            pytest.fail(f"LLMClient单例测试失败: {e}")

# 测试Agent模型管理器
class TestAgentModelManager:
    """测试Agent模型管理器"""

    def test_agent_model_manager_import(self):
        """测试AgentModelManager导入"""
        try:
            from utils.agent_model_manager import AgentModelManager
            # 如果导入成功，验证基本方法存在
            assert hasattr(AgentModelManager, 'get_agent_config')
            assert hasattr(AgentModelManager, 'chat_completion')
        except ImportError as e:
            # 这是预期的失败，符合TDD的红阶段
            pytest.fail(f"AgentModelManager导入失败: {e}")

    def test_agent_model_manager_initialization(self):
        """测试AgentModelManager初始化"""
        try:
            from utils.agent_model_manager import AgentModelManager
            manager = AgentModelManager()

            # 验证初始化后的属性
            assert hasattr(manager, 'config')
            assert hasattr(manager, '_initialized')
        except ImportError as e:
            pytest.fail(f"AgentModelManager初始化测试失败: {e}")

    def test_get_agent_config_method_exists(self):
        """测试获取agent配置方法存在性"""
        try:
            from utils.agent_model_manager import AgentModelManager
            manager = AgentModelManager()

            # 验证方法存在
            assert hasattr(manager, 'get_agent_config')
        except ImportError as e:
            pytest.fail(f"获取agent配置方法测试失败: {e}")

# 测试agent特定配置
class TestAgentSpecificConfig:
    """测试agent特定配置功能"""

    def test_safety_agent_config_loading(self):
        """测试safety_agent配置加载"""
        try:
            from utils.agent_model_manager import AgentModelManager
            manager = AgentModelManager()

            # 测试获取safety_agent配置
            config = manager.get_agent_config("safety_agent")

            # 验证配置结构
            assert "provider" in config
            assert "model" in config
            assert "temperature" in config
            assert "max_tokens" in config
        except ImportError as e:
            pytest.fail(f"safety_agent配置加载测试失败: {e}")

    def test_emotion_agent_config_loading(self):
        """测试emotion_agent配置加载"""
        try:
            from utils.agent_model_manager import AgentModelManager
            manager = AgentModelManager()

            # 测试获取emotion_agent配置
            config = manager.get_agent_config("emotion_agent")

            # 验证配置结构
            assert "provider" in config
            assert "model" in config
            assert "temperature" in config
            assert "max_tokens" in config
        except ImportError as e:
            pytest.fail(f"emotion_agent配置加载测试失败: {e}")

    def test_default_agent_config_fallback(self):
        """测试默认配置回退机制"""
        try:
            from utils.agent_model_manager import AgentModelManager
            manager = AgentModelManager()

            # 测试获取不存在的agent配置（应该回退到默认配置）
            config = manager.get_agent_config("nonexistent_agent")

            # 验证配置结构
            assert "provider" in config
            assert "model" in config
            assert "temperature" in config
            assert "max_tokens" in config
        except ImportError as e:
            pytest.fail(f"默认配置回退测试失败: {e}")

# 测试向后兼容性
class TestBackwardCompatibility:
    """测试向后兼容性"""

    def test_old_openai_client_removed(self):
        """测试旧的openai_client已被移除"""
        try:
            from ai_core import openai_client
            # 如果导入成功，说明文件还存在，应该失败
            pytest.fail("openai_client.py文件应该已被移除")
        except ImportError:
            # 这是预期的成功，文件已被移除
            assert True

    def test_old_ollama_client_removed(self):
        """测试旧的ollama_client已被移除"""
        try:
            from ai_core import ollama_client
            # 如果导入成功，说明文件还存在，应该失败
            pytest.fail("ollama_client.py文件应该已被移除")
        except ImportError:
            # 这是预期的成功，文件已被移除
            assert True

    def test_agents_use_new_system(self):
        """测试agents使用新系统"""
        try:
            # 测试safety_agent使用新系统
            from agents.safety_agent import SafetyAgent
            safety_agent = SafetyAgent()

            # 验证不再直接使用openai_client
            assert not hasattr(safety_agent, 'openai_client')

            # 测试emotion_agent使用新系统
            from agents.emotion_agent import EmotionAgent
            emotion_agent = EmotionAgent()

            # 验证不再直接使用openai_client
            assert not hasattr(emotion_agent, 'openai_client')

        except ImportError as e:
            pytest.fail(f"agents使用新系统测试失败: {e}")

# 测试完整的模型调用流程
class TestCompleteModelCallFlow:
    """测试完整的模型调用流程"""

    def test_agent_model_manager_chat_completion(self):
        """测试AgentModelManager的chat_completion方法"""
        try:
            from utils.agent_model_manager import AgentModelManager
            manager = AgentModelManager()

            # 测试调用方法存在
            assert hasattr(manager, 'chat_completion')

            # 测试方法签名
            import inspect
            sig = inspect.signature(manager.chat_completion)
            params = list(sig.parameters.keys())
            assert 'agent_name' in params
            assert 'messages' in params

        except ImportError as e:
            pytest.fail(f"AgentModelManager chat_completion测试失败: {e}")

    def test_llm_client_chat_completion_signature(self):
        """测试LLMClient的chat_completion方法签名"""
        try:
            from ai_core.llm_client import LLMClient
            llm_client = LLMClient()

            # 测试方法签名
            import inspect
            sig = inspect.signature(llm_client.chat_completion)
            params = list(sig.parameters.keys())
            assert 'messages' in params
            assert 'provider' in params
            assert 'model' in params
            assert 'temperature' in params
            assert 'max_tokens' in params

        except ImportError as e:
            pytest.fail(f"LLMClient chat_completion签名测试失败: {e}")

# 运行所有测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])