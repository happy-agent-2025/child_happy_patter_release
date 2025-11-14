
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from agents.multi_agent import multi_agent
from db.database import get_db
from db.database_service import DatabaseService
from models.user import Conversation
from schemas import (
    ChatRequest, ChatResponse,
    SessionCreateRequest, SessionResponse
)

router = APIRouter(prefix="/langgraph", tags=["LangGraph"])


@router.post("/chat", response_model=ChatResponse)
async def langgraph_chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    多代理系统驱动的智能聊天接口

    - **user_id**: 用户ID，默认为1
    - **session_id**: 可选的会话ID
    - **content**: 用户输入的聊天内容
    - **context**: 额外的上下文信息，可选

    返回多代理系统处理结果，包含智能路由和协作代理的响应
    """
    try:
        # 执行多代理系统
        result = await multi_agent.process_message(
            user_message=request.content,
            user_id=str(request.user_id or 1),
            session_id=str(request.session_id) if request.session_id is not None else None
        )

        # 存储到数据库
        DatabaseService.create_conversation(
            db=db,
            user_id=request.user_id or 1,
            session_id=request.session_id,
            agent_type=result.get("mode", "unknown"),
            user_input=request.content,
            agent_response=json.dumps(result, ensure_ascii=False)
        )

        # 构建响应
        response = ChatResponse(
            response=result.get("response", ""),
            agent_type=result.get("mode", "unknown"),
            session_id=request.session_id, # type: ignore
            timestamp=datetime.now(),
            metadata={ # type: ignore
                "intent": result.get("intent"),
                "safety_check": result.get("safety_check"),
                "emotion_analysis": result.get("emotion_analysis"),
                "world_context": result.get("world_context"),
                "role_context": result.get("role_context"),
                "voice_metadata": result.get("voice_metadata")
            }
        )

        return response

    except Exception as e:
        logger.error(f"LangGraph聊天处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"聊天处理失败: {str(e)}")


@router.post("/chat/stream")
async def langgraph_chat_stream(
    request: ChatRequest
):
    """
    多代理系统流式聊天接口（实验性）

    提供实时的agent处理状态更新
    """
    try:
        # 这里可以实现流式响应
        # 目前返回完整结果作为演示
        result = await multi_agent.process_message(
            user_message=request.content,
            user_id=str(request.user_id or 1),
            session_id=str(request.session_id) if request.session_id is not None else None
        )

        return {
            "type": "complete",
            "data": result,
            "session_id": request.session_id
        }

    except Exception as e:
        logger.error(f"多代理系统流式聊天失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"流式聊天失败: {str(e)}")


@router.get("/workflow/state")
async def get_workflow_state(
    user_id: str,
    session_id: Optional[str] = Query(None)
):
    """
    获取工作流状态信息

    返回当前LangGraph多代理系统的配置和状态
    """
    try:
        # 获取图的结构信息
        graph_structure = {
            "nodes": list(multi_agent.graph.nodes.keys()),
            "edges": [],
            "entry_point": "input_processor",
            "end_point": "END"
        }

        # 构建边信息（简化版）
        graph_structure["edges"] = [
            {"source": "input_processor", "target": "intent_router"},
            {"source": "intent_router", "target": "safety_checker"},
            {"source": "intent_router", "target": "chat_handler"},
            {"source": "intent_router", "target": "story_world_builder"},
            {"source": "safety_checker", "target": "emotion_analyzer"},
            {"source": "safety_checker", "target": "response_formatter"},
            {"source": "emotion_analyzer", "target": "chat_handler"},
            {"source": "emotion_analyzer", "target": "story_world_builder"},
            {"source": "chat_handler", "target": "memory_updater"},
            {"source": "story_world_builder", "target": "story_role_manager"},
            {"source": "story_role_manager", "target": "story_interactive"},
            {"source": "story_interactive", "target": "memory_updater"},
            {"source": "memory_updater", "target": "response_formatter"},
            {"source": "response_formatter", "target": "voice_output_processor"},
            {"source": "response_formatter", "target": "END"},
            {"source": "voice_output_processor", "target": "END"}
        ]

        return {
            "workflow_info": {
                "name": "Happy Partner Multi-Agent System",
                "version": "2.0.0",
                "description": "基于LangGraph的儿童教育AI多代理系统"
            },
            "graph_structure": graph_structure,
            "current_session": {
                "user_id": user_id,
                "session_id": session_id
            },
            "system_stats": await multi_agent.get_system_statistics()
        }

    except Exception as e:
        logger.error(f"获取工作流状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取工作流状态失败: {str(e)}")


@router.get("/analytics/conversation-flow")
async def get_conversation_flow_analytics(
    user_id: int = Query(..., description="用户ID"),
    days: int = Query(7, ge=1, le=365, description="分析天数"),
    db: Session = Depends(get_db)
):
    """
    获取用户对话流分析
    
    - **user_id**: 用户ID
    - **days**: 分析天数，默认7天
    """
    try:
        # 获取用户对话数据
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)

        conversations = db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.created_at >= cutoff_date
        ).order_by(Conversation.created_at).all()

        # 分析agent使用模式
        agent_flow = []
        agent_transitions = {}

        for i, conv in enumerate(conversations):
            agent_type = getattr(conv, 'agent_type', 'unknown')
            timestamp = getattr(conv, 'created_at', datetime.now())

            agent_flow.append({
                "agent": agent_type,
                "timestamp": timestamp.isoformat(),
                "content_preview": getattr(conv, 'user_input', '')[:50] + "..."
            })

            # 分析agent转换
            if i > 0:
                prev_agent = getattr(conversations[i-1], 'agent_type', 'unknown')
                transition_key = f"{prev_agent} -> {agent_type}"
                agent_transitions[transition_key] = agent_transitions.get(transition_key, 0) + 1

        # 统计信息
        agent_stats = {}
        for conv in conversations:
            agent_type = getattr(conv, 'agent_type', 'unknown')
            agent_stats[agent_type] = agent_stats.get(agent_type, 0) + 1

        return {
            "analysis_period": f"{days}天",
            "total_conversations": len(conversations),
            "agent_usage": agent_stats,
            "agent_transitions": agent_transitions,
            "conversation_flow": agent_flow,
            "insights": {
                "most_used_agent": max(agent_stats.items(), key=lambda x: x[1])[0] if agent_stats else None,
                "flow_complexity": len(agent_transitions),
                "session_continuity": len(conversations) > 5
            }
        }

    except Exception as e:
        logger.error(f"对话流分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.post("/session/create", response_model=SessionResponse)
async def create_langgraph_session(
    request: SessionCreateRequest,
    db: Session = Depends(get_db)
):
    """
    创建新的LangGraph会话

    - **user_id**: 用户ID
    - **title**: 会话标题
    - **context**: 初始上下文，可选
    """
    try:
        session = DatabaseService.create_session(
            db=db,
            user_id=request.user_id,
            title=request.title or "新会话"
        )

        return SessionResponse(
            id=session.id,  # type: ignore
            user_id=session.user_id,  # type: ignore
            title=session.title,  # type: ignore
            created_at=session.created_at,  # type: ignore
            updated_at=session.updated_at,  # type: ignore
            is_active=bool(session.is_active)
        )

    except Exception as e:
        logger.error(f"创建会话失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建会话失败: {str(e)}")


@router.get("/session/{session_id}/history")
async def get_session_history(
    session_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    获取会话历史记录

    - **session_id**: 会话ID
    - **limit**: 返回记录数量限制
    """
    try:
        # 验证会话存在
        session = DatabaseService.get_session_by_id(db, session_id)
        if not session or not bool(session.is_active):
            raise HTTPException(status_code=404, detail="会话不存在或已停用")

        # 获取对话记录
        conversations = DatabaseService.get_conversations_by_session(db, session_id)

        # 手动应用限制
        if len(conversations) > limit:
            conversations = conversations[:limit]

        history = []
        for conv in conversations:
            try:
                agent_response = json.loads(getattr(conv, 'agent_response', '{}'))
            except json.JSONDecodeError:
                agent_response = {}

            history.append({
                "id": getattr(conv, 'id', 0),
                "timestamp": getattr(conv, 'created_at', datetime.now()).isoformat(),
                "user_input": getattr(conv, 'user_input', ''),
                "agent_type": getattr(conv, 'agent_type', 'unknown'),
                "response": agent_response.get('response', ''),
                "metadata": agent_response.get('metadata', {}),
                "safety_info": agent_response.get('safety_info', {})
            })

        return {
            "session_id": session_id,
            "total_conversations": len(history),
            "history": history
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取历史失败: {str(e)}")


@router.get("/users/{user_id}/insights")
async def get_user_insights(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户行为洞察

    - **user_id**: 用户ID
    """
    try:
        # 获取用户所有对话
        conversations = db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).all()

        # 分析模式
        insights = {
            "total_conversations": len(conversations),
            "agent_preferences": {},
            "safety_incidents": 0,
            "learning_progress": {},
            "emotional_patterns": {}
        }

        for conv in conversations:
            agent_type = getattr(conv, 'agent_type', 'unknown')
            insights["agent_preferences"][agent_type] = insights["agent_preferences"].get(agent_type, 0) + 1

            # 尝试解析agent_response获取更详细的信息
            try:
                agent_response = json.loads(getattr(conv, 'agent_response', '{}'))
                metadata = agent_response.get('metadata', {})
                safety_info = agent_response.get('safety_info', {})

                if not safety_info.get('passed', True):
                    insights["safety_incidents"] += 1

                # 根据agent类型分析不同模式
                if metadata.get('type') == 'educational':
                    subject = metadata.get('subject', '通用')
                    insights["learning_progress"][subject] = insights["learning_progress"].get(subject, 0) + 1

                elif metadata.get('type') == 'emotional':
                    emotion = metadata.get('emotion', '未知')
                    insights["emotional_patterns"][emotion] = insights["emotional_patterns"].get(emotion, 0) + 1

            except (json.JSONDecodeError, AttributeError):
                pass

        return insights

    except Exception as e:
        logger.error(f"获取用户洞察失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取洞察失败: {str(e)}")


@router.post("/test/workflow")
async def test_workflow():
    """
    测试多代理系统（仅用于开发调试）
    """
    try:
        # 简单的测试用例
        test_result = await multi_agent.process_message(
            user_message="你好，我想听个故事",
            user_id="test_user",
            session_id="test_session"
        )

        return {
            "test_status": "success",
            "workflow_result": test_result,
            "message": "LangGraph多代理系统测试完成"
        }

    except Exception as e:
        logger.error(f"多代理系统测试失败: {str(e)}")
        return {
            "test_status": "failed",
            "error": str(e),
            "message": "LangGraph多代理系统测试失败"
        }