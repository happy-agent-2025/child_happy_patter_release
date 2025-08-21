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
        """测试处理存储请求"""
        agent = MemoryAgent()
        request = {
            "action": "store",
            "conversation": {
                "user_input": "测试问题",
                "agent_response": "测试回答"
            }
        }
        result = agent.process_request(request)
        assert result["agent"] == "memory"
        assert result["action"] == "store"
        assert result["status"] == "success"
        assert len(agent.conversation_history) == 1
    
    def test_process_request_get_history(self):
        """测试处理获取历史请求"""
        agent = MemoryAgent()
        
        # 添加对话记录
        for i in range(3):
            conversation = {
                "user_input": f"问题{i}",
                "agent_response": f"回答{i}"
            }
            agent.store_conversation(conversation)
        
        request = {
            "action": "get_history",
            "limit": 2
        }
        result = agent.process_request(request)
        assert result["agent"] == "memory"
        assert result["action"] == "get_history"
        assert result["status"] == "success"
        assert len(result["history"]) == 2
    
    def test_process_request_clear(self):
        """测试处理清空历史请求"""
        agent = MemoryAgent()
        
        # 添加对话记录
        conversation = {
            "user_input": "测试问题",
            "agent_response": "测试回答"
        }
        agent.store_conversation(conversation)
        assert len(agent.conversation_history) == 1
        
        request = {
            "action": "clear"
        }
        result = agent.process_request(request)
        assert result["agent"] == "memory"
        assert result["action"] == "clear"
        assert result["status"] == "success"
        assert len(agent.conversation_history) == 0
    
    def test_process_request_default(self):
        """测试处理默认请求"""
        agent = MemoryAgent()
        request = {
            "action": "unknown_action"
        }
        result = agent.process_request(request)
        assert result["agent"] == "memory"
        assert result["action"] == "get_context"
        assert result["status"] == "success"
        assert "context" in result