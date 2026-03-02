"""
Tests for configuration module.
"""

import pytest
import os
from backend.config import ModelConfig, AppConfig, get_model_config, get_app_config


def test_model_config_initialization():
    """Test ModelConfig initialization."""
    config = ModelConfig(
        model_name="test-model",
        base_url="http://localhost:8000",
        api_key="test-key",
        default_temperature=0.8,
        default_max_tokens=2048
    )
    
    assert config.model_name == "test-model"
    assert config.base_url == "http://localhost:8000"
    assert config.api_key == "test-key"
    assert config.default_temperature == 0.8
    assert config.default_max_tokens == 2048


def test_get_model_config():
    """Test getting default model config."""
    config = get_model_config()
    
    assert config is not None
    assert hasattr(config, 'model_name')
    assert hasattr(config, 'base_url')
    assert hasattr(config, 'api_key')


def test_app_config_defaults():
    """Test AppConfig default values."""
    config = AppConfig()
    
    assert config.HOST == os.getenv("HOST", "0.0.0.0")
    assert config.PORT == int(os.getenv("PORT", "8000"))
    assert config.LOG_LEVEL == os.getenv("LOG_LEVEL", "INFO")
    assert config.SESSION_TTL_SECONDS > 0
    assert config.RATE_LIMIT_REQUESTS > 0


def test_get_app_config():
    """Test getting app config."""
    config = get_app_config()
    
    assert config is not None
    assert hasattr(config, 'HOST')
    assert hasattr(config, 'PORT')
    assert hasattr(config, 'LOG_LEVEL')
