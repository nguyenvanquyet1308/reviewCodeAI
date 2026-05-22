import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_NAME: str = "AI GitHub Code Review Platform"
    
    DATABASE_URL: str = "postgresql://postgres:123456@localhost:5432/reviewAI"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    GITHUB_TOKEN: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""
    
    REVIEW_DRAFT_PR: bool = False
    MAX_DIFF_CHARS: int = 50000
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
