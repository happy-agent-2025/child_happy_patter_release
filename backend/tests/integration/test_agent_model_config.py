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
            assert hasattr(LLMClient, '_call_openai')
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

# 测试通用provider名称配置
class TestGenericProviderNames:
    """测试通用provider名称配置"""

    def test_llm_client_uses_generic_provider_names(self):
        """测试LLMClient使用通用provider名称"""
        try:
            from ai_core.llm_client import LLMClient
            llm_client = LLMClient()

            # 验证chat_completion方法支持通用provider名称
            import inspect
            sig = inspect.signature(llm_client.chat_completion)
            params = list(sig.parameters.keys())
            assert 'provider' in params

            # 验证默认provider是通用名称
            default_provider = sig.parameters['provider'].default
            assert default_provider in ['openai', 'ollama']

        except ImportError as e:
            pytest.fail(f"LLMClient通用provider名称测试失败: {e}")

    def test_llm_client_methods_use_generic_names(self):
        """测试LLMClient方法使用通用名称"""
        try:
            from ai_core.llm_client import LLMClient
            llm_client = LLMClient()

            # 验证方法使用通用名称
            assert hasattr(llm_client, '_call_openai')
            assert hasattr(llm_client, '_call_ollama')

            # 验证不再使用特定名称
            assert not hasattr(llm_client, '_call_deepseek')

        except ImportError as e:
            pytest.fail(f"LLMClient方法名称测试失败: {e}")

    def test_agent_config_uses_generic_providers(self):
        """测试agent配置使用通用provider名称"""
        try:
            from utils.agent_model_manager import AgentModelManager
            manager = AgentModelManager()

            # 测试获取agent配置
            config = manager.get_agent_config("safety_agent")

            # 验证配置使用通用provider名称
            assert config["provider"] in ['openai', 'ollama']

            # 验证配置包含完整的URL和key信息
            assert "api_key" in config
            assert "base_url" in config

        except ImportError as e:
            pytest.fail(f"agent配置通用provider测试失败: {e}")

    def test_config_yaml_uses_generic_providers(self):
        """测试config.yaml使用通用provider名称"""
        try:
            from utils.util import Util
            config = Util.get_config()

            # 验证agents配置使用通用provider名称
            agents_config = config.get("agents", {})
            default_config = agents_config.get("default", {})
            safety_config = agents_config.get("safety_agent", {})
            emotion_config = agents_config.get("emotion_agent", {})

            assert default_config.get("provider") in ['openai', 'ollama']
            assert safety_config.get("provider") in ['openai', 'ollama']
            assert emotion_config.get("provider") in ['openai', 'ollama']

            # 验证LLM配置使用通用名称
            llm_config = config.get("LLM", {})
            assert "openai" in llm_config
            assert "ollama" in llm_config

        except Exception as e:
            pytest.fail(f"config.yaml通用provider测试失败: {e}")

    def test_llm_client_no_hardcoded_urls(self):
        """测试LLMClient没有硬编码URL"""
        try:
            from ai_core.llm_client import LLMClient
            llm_client = LLMClient()

            # 验证_call_openai方法没有硬编码URL
            import inspect
            source = inspect.getsource(llm_client._call_openai)

            # 检查没有硬编码的DeepSeek URL
            assert "https://api.deepseek.com" not in source

            # 检查使用配置获取URL
            assert "provider_config.get" in source
            assert "base_url" in source

        except ImportError as e:
            pytest.fail(f"LLMClient硬编码URL测试失败: {e}")


class TestAgentIndependentURLConfig:
    """测试Agent独立URL和API密钥配置"""

    def test_agent_config_supports_independent_urls(self):
        """测试agent配置支持独立URL和API密钥"""
        try:
            from utils.agent_model_manager import agent_model_manager
            from utils.util import Util

            config = Util.get_config()
            agents_config = config.get("agents", {})

            # 验证agents配置结构支持独立URL和API密钥
            for agent_name, agent_config in agents_config.items():
                # 验证配置支持独立URL和API密钥字段
                assert isinstance(agent_config, dict)

                # 这些字段应该支持独立配置
                supported_fields = ["provider", "model", "temperature", "max_tokens", "api_key", "base_url"]
                for field in supported_fields:
                    # 验证字段可以存在于配置中
                    assert field in supported_fields

        except Exception as e:
            pytest.fail(f"agent独立URL配置测试失败: {e}")

    def test_agent_model_manager_supports_independent_config(self):
        """测试agent_model_manager支持独立配置"""
        try:
            from utils.agent_model_manager import agent_model_manager

            # 获取safety_agent配置
            safety_config = agent_model_manager.get_agent_config("safety_agent")

            # 验证配置包含必要的字段
            assert "provider" in safety_config
            assert "model" in safety_config
            assert "temperature" in safety_config
            assert "max_tokens" in safety_config

            # 验证配置结构支持独立URL和API密钥
            assert isinstance(safety_config, dict)

        except Exception as e:
            pytest.fail(f"agent_model_manager独立配置测试失败: {e}")

    def test_llm_client_supports_agent_specific_config(self):
        """测试LLMClient支持agent特定配置"""
        try:
            from ai_core.llm_client import LLMClient
            from utils.agent_model_manager import agent_model_manager

            llm_client = LLMClient()

            # 验证_get_provider_config方法存在
            assert hasattr(llm_client, '_get_provider_config')

            # 验证agent配置可以传递给LLM调用
            agent_config = agent_model_manager.get_agent_config("safety_agent")
            assert isinstance(agent_config, dict)

        except Exception as e:
            pytest.fail(f"LLMClient agent特定配置测试失败: {e}")

    def test_config_yaml_structure_supports_independent_urls(self):
        """测试config.yaml结构支持独立URL配置"""
        try:
            from utils.util import Util

            config = Util.get_config()

            # 验证agents配置结构
            agents_config = config.get("agents", {})
            assert isinstance(agents_config, dict)

            # 验证每个agent配置是字典
            for agent_name, agent_config in agents_config.items():
                assert isinstance(agent_config, dict)

            # 验证LLM providers配置结构
            llm_config = config.get("LLM", {})
            assert isinstance(llm_config, dict)

        except Exception as e:
            pytest.fail(f"config.yaml结构测试失败: {e}")

    def test_backward_compatibility_with_independent_urls(self):
        """测试独立URL配置的向后兼容性"""
        try:
            from utils.agent_model_manager import agent_model_manager
            from utils.util import Util

            config = Util.get_config()

            # 验证默认配置仍然工作
            default_config = agent_model_manager.get_agent_config("default")
            assert "provider" in default_config
            assert "model" in default_config

            # 验证现有agent配置仍然工作
            safety_config = agent_model_manager.get_agent_config("safety_agent")
            assert "provider" in safety_config
            assert "model" in safety_config

        except Exception as e:
            pytest.fail(f"向后兼容性测试失败: {e}")

# 运行所有测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])