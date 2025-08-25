from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
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

# 导入Schema
from schemas import (
    ChatRequest, SafetyCheckRequest, SafetyCheckResponse,
    EduQuestionRequest, EduQuestionResponse,
    EmotionSupportRequest, EmotionSupportResponse,
    AudioTranscribeRequest, AudioTranscribeResponse,
    AudioSynthesizeRequest, AudioSynthesizeResponse,
    AudioProcessRequest, AudioProcessResponse,
    VoiceRegisterRequest, VoiceRegisterResponse,
    VoiceVerifyRequest, VoiceVerifyResponse,
    MemoryActionRequest, MemoryActionResponse,
    ConversationListResponse, SecurityLogListResponse,
    ConversationItem, SecurityLogItem
)
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


@router.post("/chat", response_model=Dict[str, Any])
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    主要的聊天接口
    
    - **user_id**: 用户ID，默认为1
    - **session_id**: 可选的会话ID
    - **content**: 用户输入的聊天内容
    
    返回对应代理的处理结果
    """
    # 通过MetaAgent路由请求
    request_dict = request.dict()
    routing_result = meta_agent.process_request(request_dict)
    agent_type = routing_result["agent"]
    
    # 根据路由结果分发到对应代理处理
    if agent_type == "safety":
        result = safety_agent.process_request(request_dict)
    elif agent_type == "edu":
        result = edu_agent.process_request(request_dict)
    elif agent_type == "memory":
        result = memory_agent.process_request(request_dict)
    elif agent_type == "emotion":
        result = emotion_agent.process_request(request_dict)
    else:
        # 默认使用EduAgent处理
        result = edu_agent.process_request(request_dict)
        agent_type = "edu"
    
    # 存储对话历史
    DatabaseService.create_conversation(
        db, 
        user_id=request.user_id if request.user_id is not None else 1, 
        session_id=request.session_id, 
        agent_type=agent_type, 
        user_input=request.content, 
        agent_response=json.dumps(result, ensure_ascii=False)
    )
    
    return result


@router.post("/safety/check", response_model=SafetyCheckResponse)
async def safety_check(request: SafetyCheckRequest, db: Session = Depends(get_db)):
    """
    内容安全检查接口
    
    - **user_id**: 用户ID，默认为1
    - **content**: 需要检查的内容
    
    返回安全检查结果，包括是否安全、原因和置信度
    """
    # 执行安全检查
    request_dict = request.dict()
    result = safety_agent.process_request(request_dict)
    
    # 记录安全日志
    DatabaseService.create_security_log(
        db,
        user_id=request.user_id if request.user_id is not None else 1,
        content=request.content,
        is_safe=result.get("is_safe", True),
        filtered_content=result.get("filtered_content", request.content)
    )
    
    return result


@router.post("/edu/ask", response_model=EduQuestionResponse)
async def edu_ask(request: EduQuestionRequest, db: Session = Depends(get_db)):
    """
    教育问答接口
    
    - **user_id**: 用户ID，默认为1
    - **question**: 教育相关问题
    - **grade_level**: 年级水平，可选
    
    返回教育问题的答案和解释
    """
    # 执行教育问答
    request_dict = request.dict()
    result = edu_agent.process_request(request_dict)
    
    # 存储对话历史
    DatabaseService.create_conversation(
        db,
        user_id=request.user_id if request.user_id is not None else 1,
        session_id=None,  # 教育问答通常不需要会话
        agent_type="edu",
        user_input=request.question,
        agent_response=json.dumps(result, ensure_ascii=False)
    )
    
    return result


@router.post("/emotion/support", response_model=EmotionSupportResponse)
async def emotion_support(request: EmotionSupportRequest, db: Session = Depends(get_db)):
    """
    情感支持接口
    
    - **user_id**: 用户ID，默认为1
    - **content**: 情感表达内容
    - **emotion_type**: 情感类型，可选
    
    返回情感支持回复和建议
    """
    # 执行情感支持
    request_dict = request.dict()
    result = emotion_agent.process_request(request_dict)
    
    # 存储对话历史，包括情感分析
    DatabaseService.create_conversation(
        db,
        user_id=request.user_id if request.user_id is not None else 1,
        session_id=None,  # 情感支持通常不需要会话
        agent_type="emotion",
        user_input=request.content,
        agent_response=json.dumps(result, ensure_ascii=False)
    )
    
    return result


@router.post("/memory/manage", response_model=MemoryActionResponse)
async def memory_manage(request: MemoryActionRequest, db: Session = Depends(get_db)):
    """
    记忆管理接口
    
    - **action**: 操作类型 (store|retrieve|delete)
    - **user_id**: 用户ID，默认为1
    - **session_id**: 会话ID，可选
    - **content**: 记忆内容，存储操作时必需
    - **memory_key**: 记忆键名，检索和删除操作时必需
    - **memory_type**: 记忆类型，可选
    
    返回记忆操作结果
    """
    # 将Pydantic模型转换为字典供memory_agent处理
    request_dict = request.dict()
    
    result = memory_agent.process_request(request_dict)
    
    # 对于存储操作，记录对话历史
    if request.action == "store":
        DatabaseService.create_conversation(
            db,
            user_id=request.user_id if request.user_id is not None else 1,
            session_id=request.session_id,
            agent_type="memory",
            user_input=request.content or "",
            agent_response=json.dumps(result, ensure_ascii=False)
        )
    
    # 将结果转换为MemoryActionResponse
    return MemoryActionResponse(
        success=result.get("success", True),
        action=request.action,
        memory_data=result,
        message=result.get("message", "操作完成"),
        timestamp=datetime.now()
    )


@router.get("/users/{user_id}/conversations", response_model=ConversationListResponse)
async def get_user_conversations(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """
    获取用户对话历史
    
    - **user_id**: 用户ID
    - **limit**: 返回的对话数量限制，默认为10
    
    返回用户的对话历史列表
    """
    conversations = DatabaseService.get_conversations_by_user_id(db, user_id, limit)
    
    return ConversationListResponse(
        user_id=user_id,
        conversations=[
            ConversationItem(
                id=getattr(conv, 'id', 0),
                user_id=getattr(conv, 'user_id', 0),
                session_id=getattr(conv, 'session_id', None),
                agent_type=getattr(conv, 'agent_type', ""),
                conversation_history=getattr(conv, 'conversation_history', ""),
                created_at=getattr(conv, 'created_at'),
                updated_at=getattr(conv, 'updated_at')
            )
            for conv in conversations
        ]
    )


@router.get("/users/{user_id}/conversations/recent", response_model=ConversationListResponse)
async def get_user_recent_conversations(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """
    获取用户最近的对话记录
    
    - **user_id**: 用户ID
    - **limit**: 返回的对话数量限制，默认为10
    
    返回用户最近的对话记录列表
    """
    conversations = DatabaseService.get_recent_conversations_by_user(db, user_id, limit)
    
    return ConversationListResponse(
        user_id=user_id,
        conversations=[
            ConversationItem(
                id=getattr(conv, 'id', 0),
                user_id=getattr(conv, 'user_id', 0),
                session_id=getattr(conv, 'session_id', None),
                agent_type=getattr(conv, 'agent_type', ""),
                conversation_history=getattr(conv, 'conversation_history', ""),
                created_at=getattr(conv, 'created_at'),
                updated_at=getattr(conv, 'updated_at')
            )
            for conv in conversations
        ]
    )


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
            "id": getattr(conversation, 'id', 0),
            "user_id": getattr(conversation, 'user_id', 0),
            "session_id": getattr(conversation, 'session_id', None),
            "agent_type": getattr(conversation, 'agent_type', ""),
            "conversation_history": getattr(conversation, 'conversation_history', ""),
            "created_at": getattr(conversation, 'created_at'),
            "updated_at": getattr(conversation, 'updated_at')
        }
    }


@router.get("/users/{user_id}/security-logs", response_model=SecurityLogListResponse)
async def get_user_security_logs(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """
    获取用户安全日志
    
    - **user_id**: 用户ID
    - **limit**: 返回的日志数量限制，默认为10
    
    返回用户的安全日志列表
    """
    logs = DatabaseService.get_security_logs_by_user_id(db, user_id, limit)
    
    return SecurityLogListResponse(
        user_id=user_id,
        security_logs=[
            SecurityLogItem(
                id=getattr(log, 'id', 0),
                content=getattr(log, 'content', ""),
                is_safe=bool(getattr(log, 'is_safe', True)),
                filtered_content=getattr(log, 'filtered_content', None),
                created_at=getattr(log, 'created_at')
            )
            for log in logs
        ]
    )


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
                "id": getattr(conv, 'id', 0),
                "user_id": getattr(conv, 'user_id', 0),
                "session_id": getattr(conv, 'session_id', None),
                "agent_type": getattr(conv, 'agent_type', ""),
                "conversation_history": getattr(conv, 'conversation_history', ""),
                "created_at": getattr(conv, 'created_at'),
                "updated_at": getattr(conv, 'updated_at')
            }
            for conv in conversations
        ]
    }


@router.post("/audio/transcribe", response_model=AudioTranscribeResponse)
async def transcribe_audio(file: UploadFile = File(...), 
                          preprocess: bool = True):
    """
    语音转文本接口
    
    - **file**: 上传的音频文件
    - **preprocess**: 是否对音频进行预处理以提高识别准确率，默认为True
    
    返回转录的文本内容、置信度和音频信息
    """
    try:
        # 读取上传的音频文件
        contents = await file.read()
        
        # 使用STT服务进行转录
        text = stt_service.transcribe_audio(contents, preprocess)  # type: ignore
        
        # 估算音频时长（假设采样率16kHz，单声道，16位）
        # 这是一个简化的估算，实际应用中应该从音频数据中获取准确信息
        audio_duration = len(contents) / (16000 * 2) if contents else 0
        
        return AudioTranscribeResponse(
            text=text,
            confidence=0.9,  # 默认置信度，实际应用中应从STT服务获取
            duration=audio_duration,
            language="zh-CN"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转录失败: {str(e)}")


@router.post("/audio/synthesize", response_model=AudioSynthesizeResponse)
async def synthesize_audio(request: AudioSynthesizeRequest):
    """
    文本转语音接口
    
    - **text**: 要合成的文本内容
    - **voice_type**: 语音类型，可选（female/male），默认为female
    - **speed**: 语速（0.5-2.0），默认为1.0
    - **volume**: 音量（0.0-1.0），默认为1.0
    
    返回合成的音频数据和相关信息
    """
    try:
        if not request.text:
            raise HTTPException(status_code=400, detail="文本内容不能为空")
        
        # 设置语音属性
        speed = request.speed if request.speed is not None else 1.0
        volume = request.volume if request.volume is not None else 1.0
        tts_service.set_voice_properties(rate=int(speed * 100), volume=volume)
        
        # 使用TTS服务合成语音
        audio_buffer = tts_service.synthesize_speech(request.text)
        
        # 估算音频时长（假设采样率16kHz）
        audio_data = audio_buffer.getvalue()
        audio_duration = len(audio_data) / (16000 * 2) if audio_data else 0
        
        return AudioSynthesizeResponse(
            audio_data=audio_data.hex(),  # 转换为十六进制字符串表示
            duration=audio_duration,
            format="wav",
            sample_rate=16000
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音合成失败: {str(e)}")


@router.post("/audio/process", response_model=AudioProcessResponse)
async def process_audio(file: UploadFile = File(...), 
                       target_rate: int = 16000,
                       target_rms: float = 0.1,
                       silence_threshold: float = 0.01):
    """
    音频预处理接口
    
    - **file**: 上传的音频文件
    - **target_rate**: 目标采样率，默认为16000Hz
    - **target_rms**: 目标均方根值，默认为0.1
    - **silence_threshold**: 静音阈值，默认为0.01
    
    返回处理后的音频数据和处理信息
    """
    try:
        # 读取上传的音频文件
        contents = await file.read()
        
        # 使用AudioCodecService解码音频文件
        try:
            # 明确类型断言，确保contents是bytes类型
            assert isinstance(contents, bytes), "File contents must be bytes"
            audio_data, original_rate = audio_codec_service.decode_wav(contents)
        except:
            # 如果WAV解码失败，尝试使用soundfile解码
            audio_buffer = io.BytesIO(contents) # type: ignore
            audio_data, original_rate = sf.read(audio_buffer)
        
        # 计算原始音频时长
        original_duration = len(audio_data) / original_rate if original_rate > 0 else 0
        
        # 使用音频处理服务进行预处理
        processed_audio = audio_processing_service.preprocess_audio(
            audio_data, original_rate, target_rate, target_rms, silence_threshold)
        
        # 计算处理后的音频时长
        processed_duration = len(processed_audio) / target_rate if target_rate > 0 else 0
        
        # 将处理后的音频编码为WAV格式
        processed_wav = audio_codec_service.encode_wav(processed_audio, target_rate)
        
        return AudioProcessResponse(
            processed_audio=processed_wav.hex(),  # 转换为十六进制字符串表示
            original_duration=original_duration,
            processed_duration=processed_duration,
            sample_rate=target_rate,
            processing_steps=["resampling", "normalization", "silence_removal"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"音频预处理失败: {str(e)}")


@router.post("/voice/register", response_model=VoiceRegisterResponse)
async def register_voiceprint(request: VoiceRegisterRequest):
    """
    注册用户声纹接口
    
    - **user_id**: 用户ID
    - **audio_data**: Base64编码的音频数据
    - **sample_rate**: 音频采样率，默认为16000Hz
    - **audio_duration**: 音频时长（毫秒），可选
    
    返回声纹注册结果和特征信息
    """
    try:
        if not request.user_id or not request.audio_data:
            raise HTTPException(status_code=400, detail="用户ID和音频数据不能为空")
        
        # 这里应该从音频数据中提取声纹特征
        # 目前使用模拟的特征数据
        features = [0.1, 0.2, 0.3, 0.4, 0.5]  # 模拟特征向量
        
        # 使用声纹验证服务注册声纹
        success = voice_verification_service.register_user_voiceprint(
            request.user_id, features, request.sample_rate
        )
        
        if success:
            return VoiceRegisterResponse(
                success=True,
                user_id=request.user_id,
                feature_dimension=len(features),
                message="声纹注册成功"
            )
        else:
            raise HTTPException(status_code=500, detail="声纹注册失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"声纹注册失败: {str(e)}")


@router.post("/voice/verify", response_model=VoiceVerifyResponse)
async def verify_voiceprint(request: VoiceVerifyRequest):
    """
    验证用户声纹接口
    
    - **user_id**: 用户ID
    - **audio_data**: Base64编码的音频数据
    - **sample_rate**: 音频采样率，默认为16000Hz
    - **threshold**: 验证阈值，默认为0.8
    - **audio_duration**: 音频时长（毫秒），可选
    
    返回声纹验证结果和相似度信息
    """
    try:
        if not request.user_id or not request.audio_data:
            raise HTTPException(status_code=400, detail="用户ID和音频数据不能为空")
        
        # 这里应该从音频数据中提取声纹特征
        # 目前使用模拟的特征数据和验证结果
        features = [0.1, 0.2, 0.3, 0.4, 0.5]  # 模拟特征向量
        similarity = 0.85  # 模拟相似度分数
        
        # 使用声纹验证服务验证声纹
        is_verified, actual_similarity = voice_verification_service.verify_user_voiceprint(
            request.user_id, features, request.threshold or 0.8, request.audio_duration or 0
        )
        
        # 使用实际相似度（如果服务返回）或模拟值
        final_similarity = actual_similarity if actual_similarity is not None else similarity
        
        return VoiceVerifyResponse(
            verified=is_verified,
            similarity=final_similarity,
            user_id=request.user_id,
            threshold=request.threshold or 0.8,  # 使用请求的阈值或默认值0.8
            confidence=0.9 if is_verified else 0.1
        )
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