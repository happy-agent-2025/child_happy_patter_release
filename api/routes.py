from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 使用绝对导入
from agents.meta_agent import MetaAgent
from agents.safety_agent import SafetyAgent
from agents.edu_agent import EduAgent
from agents.memory_agent import MemoryAgent
from agents.emotion_agent import EmotionAgent
from db.database import get_db
from db.database_service import DatabaseService

router = APIRouter()

# 初始化各代理
meta_agent = MetaAgent()
safety_agent = SafetyAgent()
edu_agent = EduAgent()
memory_agent = MemoryAgent()
emotion_agent = EmotionAgent()


@router.post("/chat")
async def chat(request: Dict[str, Any], db: Session = Depends(get_db)):
    """
    主要的聊天接口
    """
    user_id = request.get("user_id", 1)  # 默认用户ID为1
    session_id = request.get("session_id")  # 可选的会话ID
    
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
    elif agent_type == "emotion":
        result = emotion_agent.process_request(request)
    else:
        result = {"agent": agent_type, "message": "请求已接收，正在处理中"}
    
    # 记录对话到数据库
    if "content" in request:
        # 根据不同代理的响应格式存储对话
        agent_response = ""
        if "answer" in result:
            agent_response = result["answer"]
        elif "response" in result:
            agent_response = result["response"]
        elif "result" in result:
            agent_response = str(result["result"])
        else:
            agent_response = str(result)
            
        # 对于emotion_agent，同时记录情感分析结果
        if agent_type == "emotion" and "emotion_analysis" in result:
            emotion_data = {
                "emotion_response": agent_response,
                "emotion_analysis": result["emotion_analysis"]
            }
            agent_response = json.dumps(emotion_data, ensure_ascii=False)
            
        DatabaseService.create_conversation(
            db, 
            user_id, 
            request["content"], 
            agent_response, 
            agent_type,
            session_id
        )
    
    return result


@router.post("/safety/check")
async def safety_check(request: Dict[str, Any], db: Session = Depends(get_db)):
    """
    内容安全检查接口
    """
    user_id = request.get("user_id", 1)  # 默认用户ID为1
    session_id = request.get("session_id")  # 可选的会话ID
    result = safety_agent.process_request(request)
    
    # 记录安全检查到数据库
    if "content" in request and "result" in result:
        safety_result = result["result"]
        DatabaseService.create_security_log(
            db,
            user_id,
            request["content"],
            safety_result["is_safe"],
            safety_result["filtered_content"]
        )
        
        # 同时记录到对话表中
        DatabaseService.create_conversation(
            db,
            user_id,
            request["content"],
            json.dumps(safety_result, ensure_ascii=False),
            "safety",
            session_id
        )
    
    return result


@router.post("/edu/ask")
async def edu_ask(request: Dict[str, Any], db: Session = Depends(get_db)):
    """
    教育问答接口
    """
    user_id = request.get("user_id", 1)  # 默认用户ID为1
    session_id = request.get("session_id")  # 可选的会话ID
    result = edu_agent.process_request(request)
    
    # 记录对话到数据库
    if "content" in request and "answer" in result:
        DatabaseService.create_conversation(
            db, 
            user_id, 
            request["content"], 
            result["answer"], 
            "edu",
            session_id
        )
    
    return result


@router.post("/emotion/support")
async def emotion_support(request: Dict[str, Any], db: Session = Depends(get_db)):
    """
    情感支持接口
    """
    user_id = request.get("user_id", 1)  # 默认用户ID为1
    session_id = request.get("session_id")  # 可选的会话ID
    result = emotion_agent.process_request(request)
    
    # 记录对话到数据库
    if "content" in request:
        # 对于emotion_agent，同时记录情感分析结果
        emotion_data = {
            "emotion_response": result.get("response", str(result)),
            "emotion_analysis": result.get("emotion_analysis", {})
        }
        agent_response = json.dumps(emotion_data, ensure_ascii=False)
        
        DatabaseService.create_conversation(
            db, 
            user_id, 
            request["content"], 
            agent_response, 
            "emotion",
            session_id
        )
    
    return result


@router.post("/memory/manage")
async def memory_manage(request: Dict[str, Any], db: Session = Depends(get_db)):
    """
    记忆管理接口
    """
    user_id = request.get("user_id", 1)  # 默认用户ID为1
    session_id = request.get("session_id")  # 可选的会话ID
    result = memory_agent.process_request(request)
    
    # 如果是存储操作，记录对话到数据库
    if request.get("action") == "store" and "conversation" in request:
        conversation = request["conversation"]
        DatabaseService.create_conversation(
            db, 
            user_id, 
            conversation.get("user_input", ""), 
            conversation.get("agent_response", ""), 
            "memory",
            session_id
        )
    elif "content" in request:
        # 记录其他memory操作到数据库
        DatabaseService.create_conversation(
            db,
            user_id,
            request["content"],
            json.dumps(result, ensure_ascii=False),
            "memory",
            session_id
        )
    
    return result


@router.get("/users/{user_id}/conversations")
async def get_user_conversations(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """
    获取用户对话历史
    """
    conversations = DatabaseService.get_conversations_by_user_id(db, user_id, limit)
    return {
        "user_id": user_id,
        "conversations": [
            {
                "id": conv.id,
                "user_input": conv.user_input,
                "agent_response": conv.agent_response,
                "agent_type": conv.agent_type,
                "session_id": conv.session_id,
                "created_at": conv.created_at
            }
            for conv in conversations
        ]
    }


@router.get("/users/{user_id}/conversations/recent")
async def get_user_recent_conversations(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """
    获取用户最近的对话记录
    """
    conversations = DatabaseService.get_recent_conversations_by_user(db, user_id, limit)
    return {
        "user_id": user_id,
        "conversations": [
            {
                "id": conv.id,
                "user_id": conv.user_id,
                "session_id": conv.session_id,
                "agent_type": conv.agent_type,
                "conversation_history": conv.conversation_history,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at
            }
            for conv in conversations
        ]
    }


@router.get("/users/{user_id}/conversations/{agent_type}")
async def get_user_conversation_by_agent(user_id: int, agent_type: str, db: Session = Depends(get_db)):
    """
    根据用户ID和代理类型获取对话记录
    """
    conversation = DatabaseService.get_conversation_by_user_and_agent(db, user_id, agent_type)
    if not conversation:
        return {
            "user_id": user_id,
            "agent_type": agent_type,
            "conversation": None
        }
    
    return {
        "user_id": user_id,
        "agent_type": agent_type,
        "conversation": {
            "id": conversation.id,
            "user_id": conversation.user_id,
            "session_id": conversation.session_id,
            "agent_type": conversation.agent_type,
            "conversation_history": conversation.conversation_history,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at
        }
    }


@router.get("/users/{user_id}/security-logs")
async def get_user_security_logs(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """
    获取用户安全日志
    """
    logs = DatabaseService.get_security_logs_by_user_id(db, user_id, limit)
    return {
        "user_id": user_id,
        "security_logs": [
            {
                "id": log.id,
                "content": log.content,
                "is_safe": bool(log.is_safe),
                "filtered_content": log.filtered_content,
                "created_at": log.created_at
            }
            for log in logs
        ]
    }


@router.post("/users/{user_id}/sessions")
async def create_session(user_id: int, title: str, db: Session = Depends(get_db)):
    """
    创建新会话
    """
    session = DatabaseService.create_session(db, user_id, title)
    return {
        "session_id": session.id,
        "user_id": user_id,
        "title": session.title,
        "created_at": session.created_at
    }


@router.get("/users/{user_id}/sessions")
async def get_user_sessions(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户的所有活跃会话
    """
    sessions = DatabaseService.get_active_sessions_by_user_id(db, user_id)
    return {
        "user_id": user_id,
        "sessions": [
            {
                "id": session.id,
                "title": session.title,
                "created_at": session.created_at,
                "updated_at": session.updated_at
            }
            for session in sessions
        ]
    }


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: int, db: Session = Depends(get_db)):
    """
    删除会话（标记为非活跃）
    """
    success = DatabaseService.delete_session(db, session_id)
    return {
        "session_id": session_id,
        "deleted": success
    }


@router.get("/sessions/{session_id}/conversations")
async def get_session_conversations(session_id: int, db: Session = Depends(get_db)):
    """
    获取会话中的所有对话
    """
    # 检查会话是否存在且活跃
    session = DatabaseService.get_session_by_id(db, session_id)
    if not session or session.is_active == 0: # type: ignore
        raise HTTPException(status_code=404, detail="会话未找到或已删除")
    
    conversations = DatabaseService.get_conversations_by_session(db, session_id)
    return {
        "session_id": session_id,
        "conversations": [
            {
                "id": conv.id,
                "user_id": conv.user_id,
                "session_id": conv.session_id,
                "agent_type": conv.agent_type,
                "conversation_history": conv.conversation_history,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at
            }
            for conv in conversations
        ]
    }