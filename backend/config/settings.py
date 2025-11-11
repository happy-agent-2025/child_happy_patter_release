import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):  # type: ignore
    # 数据库配置
    database_url: str = "sqlite:///./happy_partner.db"

    # 安全配置
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # 音频配置
    audio_sample_rate: int = 16000

    # OpenAI配置
    openai_api_key: str = ""
    openai_base_url: str = "https://api2.aigcbest.top/v1/"

    # Ollama配置
    use_ollama: bool = True
    ollama_base_url: str = "http://localhost:11434"
    ollama_default_model: str = "qwen2.5:0.5b"
    ollama_timeout: int = 60

    class Config:  # type: ignore
        env_file = ".env"


settings = Settings()
