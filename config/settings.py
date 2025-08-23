import os
from pydantic import BaseSettings


class Settings(BaseSettings): # type: ignore
    # 数据库配置
    database_url: str = "sqlite:///./happy_partner.db"
    
    # 安全配置
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 音频配置
    audio_sample_rate: int = 16000
    
    # OpenAI配置
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", "sk-7ac41405576e4ef59aab6ab769bc3ed3")
    openai_base_url: str = os.environ.get("OPENAI_BASE_URL", "https://api.deepseek.com/v1")
    
    class Config:
        env_file = ".env"


settings = Settings()