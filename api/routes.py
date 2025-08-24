from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
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
from services.stt_service import STTService
from services.tts_service import TTSService
from services.processing import AudioProcessingService
from services.verification import VoiceVerificationService
from services.codecs import AudioCodecService
from auth.auth_utils import get_password_hash, verify_password, create_access_token, get_current_user
from schemas.auth import UserCreate, UserLogin, Token, UserResponse
import io
import soundfile as sf

router = APIRouter()

# 初始化各代理
meta_agent = MetaAgent()
safety_agent = SafetyAgent()
edu_agent = EduAgent()
memory_agent = MemoryAgent()
emotion_agent = EmotionAgent()

# 初始化音频服务
stt_service = STTService()
tts_service = TTSService()
audio_processing_service = AudioProcessingService()
voice_verification_service = VoiceVerificationService()
audio_codec_service = AudioCodecService()


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
        # 默认使用EduAgent处理
        result = edu_agent.process_request(request)
        agent_type = "edu"
    
    # 存储对话历史
    DatabaseService.create_conversation(
        db, 
        user_id=user_id, 
        session_id=session_id, 
        agent_type=agent_type, 
        user_input=request.get("content", ""), 
        agent_response=json.dumps(result, ensure_ascii=False)
    )
    
    return result


@router.post("/safety/check")
async def safety_check(request: Dict[str, Any], db: Session = Depends(get_db)):
    """
    内容安全检查接口
    """
    user_id = request.get("user_id", 1)
    content = request.get("content", "")
    
    # 执行安全检查
    result = safety_agent.process_request(request)
    
    # 记录安全日志
    DatabaseService.create_security_log(
        db,
        user_id=user_id,
        content=content,
        is_safe=result.get("is_safe", True),
        filtered_content=result.get("filtered_content", content)
    )
    
    return result


@router.post("/edu/ask")
async def edu_ask(request: Dict[str, Any], db: Session = Depends(get_db)):
    """
    教育问答接口
    """
    user_id = request.get("user_id", 1)
    session_id = request.get("session_id")
    
    result = edu_agent.process_request(request)
    
    # 存储对话历史
    DatabaseService.create_conversation(
        db,
        user_id=user_id,
        session_id=session_id,
        agent_type="edu",
        user_input=request.get("content", ""),
        agent_response=json.dumps(result, ensure_ascii=False)
    )
    
    return result


@router.post("/emotion/support")
async def emotion_support(request: Dict[str, Any], db: Session = Depends(get_db)):
    """
    情感支持接口
    """
    user_id = request.get("user_id", 1)
    session_id = request.get("session_id")
    
    result = emotion_agent.process_request(request)
    
    # 存储对话历史，包括情感分析
    DatabaseService.create_conversation(
        db,
        user_id=user_id,
        session_id=session_id,
        agent_type="emotion",
        user_input=request.get("content", ""),
        agent_response=json.dumps(result, ensure_ascii=False)
    )
    
    return result


@router.post("/memory/manage")
async def memory_manage(request: Dict[str, Any], db: Session = Depends(get_db)):
    """
    记忆管理接口
    """
    user_id = request.get("user_id", 1)
    session_id = request.get("session_id")
    
    result = memory_agent.process_request(request)
    
    # 对于存储操作，记录对话历史
    if request.get("action") == "store":
        DatabaseService.create_conversation(
            db,
            user_id=user_id,
            session_id=session_id,
            agent_type="memory",
            user_input=request.get("content", ""),
            agent_response=json.dumps(result, ensure_ascii=False)
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
async def create_user_session(
    user_id: int, 
    title: str = "默认会话", 
    db: Session = Depends(get_db)
):
    """
    为用户创建新会话
    """
    # 确保标题使用UTF-8编码
    encoded_title = title.encode('utf-8').decode('utf-8')
    
    # 使用查询参数创建会话
    session = DatabaseService.create_session(db, user_id=user_id, title=encoded_title)
    
    return {
        "session_id": session.id,
        "user_id": session.user_id,
        "title": session.title,
        "created_at": session.created_at,
        "is_active": bool(session.is_active)
    }


@router.get("/users/{user_id}/sessions")
async def get_user_sessions(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """
    获取用户的会话列表
    
    Args:
        user_id: 用户ID
        limit: 返回的会话数量限制
        db: 数据库会话
        
    Returns:
        用户的会话列表
    """
    sessions = DatabaseService.get_sessions_by_user_id(db, user_id, limit)
    
    return {
        "user_id": user_id,
        "sessions": [
            {
                "id": session.id,
                "title": session.title,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "is_active": bool(session.is_active)
            }
            for session in sessions
        ]
    }


@router.get("/sessions/{session_id}")
async def get_session_info(session_id: int, db: Session = Depends(get_db)):
    """
    获取会话信息
    """
    session = DatabaseService.get_session_by_id(db, session_id)
    if not session or session.is_active == 0: # type: ignore
        raise HTTPException(status_code=404, detail="会话未找到或已删除")
    
    return {
        "session_id": session.id,
        "user_id": session.user_id,
        "title": session.title,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "is_active": bool(session.is_active)
    }


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: int, db: Session = Depends(get_db)):
    """
    删除会话（软删除）
    """
    success = DatabaseService.delete_session(db, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="会话未找到")
    
    return {"deleted": True, "message": "会话删除成功"}


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


@router.post("/audio/transcribe")
async def transcribe_audio(file: UploadFile = File(...), 
                          preprocess: bool = True):
    """
    语音转文本接口
    
    Args:
        file: 上传的音频文件
        preprocess: 是否对音频进行预处理以提高识别准确率
    """
    try:
        # 读取上传的音频文件
        contents = await file.read()
        
        # 使用STT服务进行转录
        text = stt_service.transcribe_audio(contents, preprocess)  # type: ignore
        
        return {
            "filename": file.filename,
            "transcribed_text": text,
            "preprocess_applied": preprocess
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转录失败: {str(e)}")


@router.post("/audio/synthesize")
async def synthesize_audio(request: Dict[str, Any]):
    """
    文本转语音接口
    """
    try:
        text = request.get("text", "")
        rate = request.get("rate", 150)
        volume = request.get("volume", 0.9)
        
        if not text:
            raise HTTPException(status_code=400, detail="文本内容不能为空")
        
        # 设置语音属性
        tts_service.set_voice_properties(rate=rate, volume=volume)
        
        # 使用TTS服务合成语音
        audio_buffer = tts_service.synthesize_speech(text)
        
        # 返回音频数据
        return {
            "text": text,
            "rate": rate,
            "volume": volume,
            "audio_data": audio_buffer.getvalue()  # 获取字节数据
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音合成失败: {str(e)}")


@router.post("/audio/process")
async def process_audio(file: UploadFile = File(...), 
                       target_rate: int = 16000,
                       target_rms: float = 0.1,
                       silence_threshold: float = 0.01):
    """
    音频预处理接口
    
    Args:
        file: 上传的音频文件
        target_rate: 目标采样率
        target_rms: 目标均方根值
        silence_threshold: 静音阈值
    """
    try:
        # 读取上传的音频文件
        contents = await file.read()
        
        # 使用AudioCodecService解码音频文件
        try:
            audio_data, original_rate = audio_codec_service.decode_wav(contents)
        except:
            # 如果WAV解码失败，尝试使用soundfile解码
            audio_buffer = io.BytesIO(contents) # type: ignore
            audio_data, original_rate = sf.read(audio_buffer)
        
        # 使用音频处理服务进行预处理
        processed_audio = audio_processing_service.preprocess_audio(
            audio_data, original_rate, target_rate, target_rms, silence_threshold)
        
        # 将处理后的音频编码为WAV格式
        processed_wav = audio_codec_service.encode_wav(processed_audio, target_rate)
        
        return {
            "filename": file.filename,
            "original_length": len(audio_data),
            "processed_length": len(processed_audio),
            "original_rate": original_rate,
            "target_rate": target_rate,
            "processed_audio": processed_wav,
            "message": "音频预处理完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"音频预处理失败: {str(e)}")


@router.post("/voice/register")
async def register_voiceprint(request: Dict[str, Any]):
    """
    注册用户声纹接口
    """
    try:
        user_id = request.get("user_id")
        features = request.get("features")
        sample_rate = request.get("sample_rate", 16000)  # 默认采样率16kHz
        
        if not user_id or not features:
            raise HTTPException(status_code=400, detail="用户ID和声纹特征不能为空")
        
        # 使用声纹验证服务注册声纹
        success = voice_verification_service.register_user_voiceprint(user_id, features, sample_rate)
        
        if success:
            return {
                "user_id": user_id,
                "sample_rate": sample_rate,
                "message": "声纹注册成功"
            }
        else:
            raise HTTPException(status_code=500, detail="声纹注册失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"声纹注册失败: {str(e)}")


@router.post("/voice/verify")
async def verify_voiceprint(request: Dict[str, Any]):
    """
    验证用户声纹接口
    """
    try:
        user_id = request.get("user_id")
        features = request.get("features")
        threshold = request.get("threshold", 0.8)  # 默认阈值0.8
        audio_duration = request.get("audio_duration", 0)  # 音频时长(毫秒)
        
        if not user_id or not features:
            raise HTTPException(status_code=400, detail="用户ID和声纹特征不能为空")
        
        # 使用声纹验证服务验证声纹
        is_verified, similarity = voice_verification_service.verify_user_voiceprint(
            user_id, features, threshold, audio_duration
        )
        
        return {
            "user_id": user_id,
            "is_verified": is_verified,
            "similarity": similarity,
            "threshold": threshold,
            "audio_duration": audio_duration,
            "message": "声纹验证成功" if is_verified else "声纹验证失败"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"声纹验证失败: {str(e)}")


# 认证路由
@router.post("/auth/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    """
    # 检查用户名是否已存在
    if DatabaseService.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=400,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if DatabaseService.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=400,
            detail="邮箱已存在"
        )
    
    # 加密密码
    hashed_password = get_password_hash(user.password)
    
    # 创建用户
    db_user = DatabaseService.create_user(db, user.username, user.email, hashed_password)
    
    return db_user


@router.post("/auth/login", response_model=Token)
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录接口
    """
    # 验证用户
    db_user = DatabaseService.get_user_by_username(db, user.username)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token = create_access_token(data={"sub": db_user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """
    获取当前用户信息
    """
    return current_user


# 会话管理增强功能
@router.put("/sessions/{session_id}/title")
async def update_session_title(
    session_id: int, 
    title: str, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    更新会话标题
    """
    session = DatabaseService.get_session_by_id(db, session_id, include_inactive=True)
    if not session:
        raise HTTPException(status_code=404, detail="会话未找到")
    
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改此会话")
    
    session.title = title # type: ignore
    db.commit()
    db.refresh(session)
    
    return {
        "session_id": session.id,
        "title": session.title,
        "message": "会话标题更新成功"
    }


@router.post("/sessions/{session_id}/activate")
async def activate_session(
    session_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    激活会话
    """
    session = DatabaseService.get_session_by_id(db, session_id, include_inactive=True)
    if not session:
        raise HTTPException(status_code=404, detail="会话未找到")
    
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此会话")
    
    session.is_active = 1 # type: ignore
    db.commit()
    db.refresh(session)
    
    return {
        "session_id": session.id,
        "is_active": bool(session.is_active),
        "message": "会话已激活"
    }


@router.post("/sessions/{session_id}/deactivate")
async def deactivate_session(
    session_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    停用会话
    """
    session = DatabaseService.get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话未找到")
    
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此会话")
    
    session.is_active = 0 # type: ignore
    db.commit()
    db.refresh(session)
    
    return {
        "session_id": session.id,
        "is_active": bool(session.is_active),
        "message": "会话已停用"
    }


@router.get("/")
async def root():
    """
    根端点
    """
    return {"message": "儿童教育AI系统API服务", "version": "1.0.0"}