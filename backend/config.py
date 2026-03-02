"""
Configuration module for the conversational AI system.
Centralizes all configuration and environment variable handling.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ModelConfig:
    """Configuration for the model backend."""
    
    def __init__(
        self,
        model_name: str,
        base_url: str,
        api_key: str,
        default_temperature: float = 0.7,
        default_max_tokens: int = 1024,
        system_prompt_scene: str = "default"
    ):
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key
        self.default_temperature = default_temperature
        self.default_max_tokens = default_max_tokens
        self.system_prompt_scene = system_prompt_scene


# Default model configuration from environment variables
DEFAULT_MODEL_CONFIG = ModelConfig(
    model_name=os.getenv("MODEL_NAME", "qwen-plus"),
    base_url=os.getenv("BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
    api_key=os.getenv("API_KEY", ""),
    default_temperature=float(os.getenv("DEFAULT_TEMPERATURE", "0.7")),
    default_max_tokens=int(os.getenv("DEFAULT_MAX_TOKENS", "1024")),
    system_prompt_scene=os.getenv("SYSTEM_PROMPT_SCENE", "default")
)


class AppConfig:
    """Application-level configuration."""
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")  # json or text
    
    # Session settings
    SESSION_TTL_SECONDS: int = int(os.getenv("SESSION_TTL_SECONDS", "3600"))
    SESSION_CLEANUP_INTERVAL: int = int(os.getenv("SESSION_CLEANUP_INTERVAL", "300"))
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    
    # CORS settings
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")


def get_model_config() -> ModelConfig:
    """Get the default model configuration."""
    return DEFAULT_MODEL_CONFIG


def get_app_config() -> AppConfig:
    """Get the application configuration."""
    return AppConfig()
