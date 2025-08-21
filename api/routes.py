from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 使用绝对导入
from agents.meta_agent import MetaAgent
from agents.safety_agent import SafetyAgent
from agents.edu_agent import EduAgent
from agents.memory_agent import MemoryAgent

router = APIRouter()

# 初始化各代理
meta_agent = MetaAgent()
safety_agent = SafetyAgent()
edu_agent = EduAgent()
memory_agent = MemoryAgent()


@router.post("/chat")
async def chat(request: Dict[str, Any]):
    """
    主要的聊天接口
    """
    # 通过MetaAgent路由请求
    routing_result = meta_agent.process_request(request)
    agent_type = routing_result["agent"]
    
    # 根据路由结果分发到对应代理处理
    if agent_type == "safety":
        result = safety_agent.process_request(request)
    elif agent_type == "edu":
        result = edu_agent.process_request(request)
    elif agent_type == "memory":
        result = memory_agent.process_request(request)
    else:
        result = {"agent": agent_type, "message": "请求已接收，正在处理中"}
    
    return result


@router.post("/safety/check")
async def safety_check(request: Dict[str, Any]):
    """
    内容安全检查接口
    """
    result = safety_agent.process_request(request)
    return result


@router.post("/edu/ask")
async def edu_ask(request: Dict[str, Any]):
    """
    教育问答接口
    """
    result = edu_agent.process_request(request)
    return result


@router.post("/memory/manage")
async def memory_manage(request: Dict[str, Any]):
    """
    记忆管理接口
    """
    result = memory_agent.process_request(request)
    return result