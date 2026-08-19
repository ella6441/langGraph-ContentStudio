"""Configuration management"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    
    # LLM Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # ElevenLabs Configuration
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
    
    # LangSmith Configuration
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "true")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "notebooklm-studio")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./notebooklm_studio.db"
    )
    
    # Backend Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # LangGraph Configuration
    CHECKPOINTER_TYPE: str = os.getenv("CHECKPOINTER_TYPE", "sqlite")
    
    # Content limits
    TED_TALK_MAX_WORDS: int = int(os.getenv("TED_TALK_MAX_WORDS", "2250"))
    PODCAST_SEGMENT_MAX_WORDS: int = int(os.getenv("PODCAST_SEGMENT_MAX_WORDS", "800"))
    
    # Workflow configuration
    MAX_REVISIONS_TED: int = int(os.getenv("MAX_REVISIONS_TED", "3"))
    MAX_REVISIONS_PODCAST: int = int(os.getenv("MAX_REVISIONS_PODCAST", "2"))
    CRITIQUE_THRESHOLD: float = float(os.getenv("CRITIQUE_THRESHOLD", "7.0"))
    
    # Timeout settings
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "60"))
    APPROVAL_TIMEOUT: int = int(os.getenv("APPROVAL_TIMEOUT", "300"))  # 5 minutes


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LANGCHAIN_TRACING_V2 = "true"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    DATABASE_URL = "sqlite:///./test.db"
    OPENAI_MODEL = "gpt-3.5-turbo"  # Faster for testing


def get_config() -> Config:
    """Get appropriate config based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }
    
    return config_map.get(env, DevelopmentConfig)()


# Export singleton config instance
config = get_config()
