import os
from typing import Optional
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    应用配置设置
    支持环境变量和.env文件配置
    """

    # 应用配置
    app_name: str = "Happy Partner - 儿童教育AI系统"
    app_version: str = "0.2.0"
    app_description: str = "一个多代理架构的儿童教育AI系统，专注于教育辅助和情感陪伴"

    # 服务器配置
    host: str = "127.0.0.1"
    port: int = 8001
    debug: bool = False
    reload: bool = False

    # 数据库配置
    database_url: str = "sqlite:///./happy_partner.db"

    # 安全配置
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # 音频配置
    audio_sample_rate: int = 16000
    audio_channels: int = 1
    audio_format: str = "wav"
    max_audio_duration: int = 300  # 最大音频时长（秒）

    # OpenAI配置
    openai_api_key: str = "sk-054b723c3a1b4e21839f560466cf6f3d"
    openai_base_url: str = "https://api.deepseek.com"
    openai_default_model: str = "qwen-turbo"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 2000
    openai_timeout: int = 30

    # Ollama配置
    use_ollama: bool = True
    ollama_base_url: str = "http://localhost:11436"
    ollama_default_model: str = "qwen2.5:0.5b"
    ollama_timeout: int = 60

    # Mem0记忆系统配置
    mem0_enabled: bool = True
    mem0_vector_store_provider: str = "qdrant"
    mem0_qdrant_path: str = "./qdrant_db"
    mem0_collection_name: str = "happy_partner"
    mem0_embedding_model: str = "text-embedding-3-small"
    mem0_embedding_dims: int = 1536
    mem0_cache_ttl: int = 300  # 缓存5分钟

    # TTS语音合成配置
    tts_provider: str = "edge-tts"  # edge-tts, gtts, pyttsx3, fish-speech, chattts
    tts_voice: str = "zh-CN-XiaoxiaoNeural"
    tts_rate: int = 0
    tts_volume: int = 100

    # STT语音识别配置
    stt_provider: str = "whisper"  # whisper, speech_recognition
    stt_model: str = "base"
    stt_language: str = "zh"

    # 多代理系统配置
    multi_agent_enabled: bool = True
    intent_agent_enabled: bool = True
    safety_agent_enabled: bool = True
    emotion_agent_enabled: bool = True
    edu_agent_enabled: bool = True
    memory_agent_enabled: bool = True
    world_agent_enabled: bool = True
    role_agent_enabled: bool = True
    role_factory_enabled: bool = True
    chapter_manager_enabled: bool = True

    # 故事系统配置
    story_max_chapters: int = 10
    story_max_roles: int = 5
    story_session_timeout: int = 3600  # 会话超时时间（秒）

    # 教育系统配置
    edu_max_questions: int = 5
    edu_subjects: list = ["数学", "语文", "英语", "科学", "历史", "地理", "艺术", "音乐", "体育", "生活常识"]

    # 情感分析配置
    emotion_categories: list = ["快乐", "悲伤", "愤怒", "恐惧", "惊讶", "厌恶", "平静", "兴奋", "困惑", "期待"]

    # 安全系统配置
    safety_check_enabled: bool = True
    safety_filter_level: str = "strict"  # strict, moderate, lenient
    safety_blocked_keywords: list = ["暴力", "色情", "赌博", "毒品", "诈骗"]

    # 日志配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None

    # 性能配置
    max_concurrent_requests: int = 10
    request_timeout: int = 60
    cache_enabled: bool = True
    cache_ttl: int = 300

    # CORS配置
    cors_allow_origins: list = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# 全局配置实例
settings = Settings()
