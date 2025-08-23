import pytest
from agents.memory_agent import MemoryAgent
from typing import Dict, Any


class TestMemoryAgent:
    """测试MemoryAgent类"""
    
    def test_init(self):
        """测试MemoryAgent初始化"""
        agent = MemoryAgent()
        assert agent is not None
        assert isinstance(agent.conversation_history, list)
        assert len(agent.conversation_history) == 0
    
    def test_store_conversation(self):
        """测试存储对话"""
        agent = MemoryAgent()
        conversation = {
            "user_input": "你好",
            "agent_response": "你好！有什么可以帮助你的吗？"
        }
        agent.store_conversation(conversation)
        assert len(agent.conversation_history) == 1
        assert agent.conversation_history[0] == conversation
    
    def test_get_conversation_history(self):
        """测试获取对话历史"""
        agent = MemoryAgent()
        
        # 添加多个对话记录
        for i in range(5):
            conversation = {
                "user_input": f"问题{i}",
                "agent_response": f"回答{i}"
            }
            agent.store_conversation(conversation)
        
        # 获取所有历史
        history = agent.get_conversation_history()
        assert len(history) == 5
        
        # 限制返回数量
        limited_history = agent.get_conversation_history(3)
        assert len(limited_history) == 3
        # 检查是否是最近的记录
        assert limited_history[0]["user_input"] == "问题2"
    
    def test_clear_conversation_history(self):
        """测试清空对话历史"""
        agent = MemoryAgent()
        
        # 添加对话记录
        conversation = {
            "user_input": "你好",
            "agent_response": "你好！"
        }
        agent.store_conversation(conversation)
        assert len(agent.conversation_history) == 1
        
        # 清空历史
        agent.clear_conversation_history()
        assert len(agent.conversation_history) == 0
    
    def test_get_context(self):
        """测试获取上下文"""
        agent = MemoryAgent()
        
        # 添加对话记录
        for i in range(3):
            conversation = {
                "user_input": f"问题{i}",
                "agent_response": f"回答{i}"
            }
            agent.store_conversation(conversation)
        
        context = agent.get_context()
        assert "history_count" in context
        assert "recent_history" in context
        assert context["history_count"] == 3
        assert len(context["recent_history"]) == 3

    def test_process_request_store(self):
        """测试处理请求 - 存储操作"""
        agent = MemoryAgent()
        request = {
            "action": "store",
            "conversation": {
                "user_input": "测试问题",
                "agent_response": "测试回答"
            },
            "user_id": "test_user"
        }
        result = agent.process_request(request)
        
        assert result["agent"] == "memory"
        assert result["action"] == "store"
        assert "status" in result

    def test_process_request_get_history(self):
        """测试处理请求 - 获取历史"""
        agent = MemoryAgent()
        request = {
            "action": "get_history",
            "limit": 5,
            "user_id": "test_user"
        }
        result = agent.process_request(request)
        
        assert result["agent"] == "memory"
        assert result["action"] == "get_history"
        assert "status" in result
        assert "history" in result

    def test_process_request_clear(self):
        """测试处理请求 - 清空历史"""
        agent = MemoryAgent()
        request = {
            "action": "clear",
            "user_id": "test_user"
        }
        result = agent.process_request(request)
        
        assert result["agent"] == "memory"
        assert result["action"] == "clear"
        assert "status" in result

    def test_process_request_default(self):
        """测试处理请求 - 默认操作"""
        agent = MemoryAgent()
        request = {
            "action": "get_context",
            "user_id": "test_user"
        }
        result = agent.process_request(request)
        
        assert result["agent"] == "memory"
        assert result["action"] == "get_context"
        assert "status" in result
        assert "context" in result