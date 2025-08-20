from pydantic import BaseSettings


class Settings(BaseSettings):
    # 数据库配置
    database_url: str = "sqlite:///./happy_partner.db"
    
    # 安全配置
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 音频配置
    audio_sample_rate: int = 16000
    
    class Config:
        env_file = ".env"


settings = Settings()