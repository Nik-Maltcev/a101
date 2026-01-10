"""Application configuration settings."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Base paths
    BASE_DIR: Path = Path(__file__).parent.parent
    UPLOADS_DIR: Path = BASE_DIR / "uploads"
    RESULTS_DIR: Path = BASE_DIR / "results"
    DATA_DIR: Path = BASE_DIR / "data"
    STATIC_DIR: Path = BASE_DIR / "static"
    
    # Categories reference file
    CATEGORIES_FILE: Path = DATA_DIR / "categories.xlsx"
    
    # Redis configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # LLM configuration
    LLM_API_KEY: str = ""
    LLM_API_URL: str = "https://api.deepseek.com"
    LLM_MODEL: str = "deepseek-chat"
    
    # Processing settings
    SPLIT_BATCH_SIZE: int = 30
    CLASSIFY_BATCH_SIZE: int = 50
    CATEGORY_TOP_N: int = 10
    
    # File settings
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS: set = {".xlsx"}
    
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
settings.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.STATIC_DIR.mkdir(parents=True, exist_ok=True)
