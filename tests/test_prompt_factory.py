"""
Tests for the prompt factory.
"""

import pytest
from backend.prompts.prompt_factory import PromptFactory, get_prompt_factory


def test_get_system_prompt_default():
    """Test loading default system prompt."""
    factory = PromptFactory()
    prompt = factory.get_system_prompt("default")
    
    assert prompt is not None
    assert len(prompt) > 0
    assert "助手" in prompt or "assistant" in prompt.lower()


def test_get_system_prompt_it_helpdesk():
    """Test loading IT helpdesk prompt."""
    factory = PromptFactory()
    prompt = factory.get_system_prompt("it_helpdesk")
    
    assert prompt is not None
    assert len(prompt) > 0
    assert "IT" in prompt or "技术" in prompt


def test_get_system_prompt_caching():
    """Test that prompts are cached."""
    factory = PromptFactory()
    
    # First call
    prompt1 = factory.get_system_prompt("default")
    
    # Second call should use cache
    prompt2 = factory.get_system_prompt("default")
    
    assert prompt1 == prompt2
    assert "default" in factory._cache


def test_get_system_prompt_invalid_scene():
    """Test loading non-existent prompt."""
    factory = PromptFactory()
    
    with pytest.raises(FileNotFoundError):
        factory.get_system_prompt("nonexistent_scene")


def test_clear_cache():
    """Test clearing prompt cache."""
    factory = PromptFactory()
    
    # Load a prompt
    factory.get_system_prompt("default")
    assert len(factory._cache) > 0
    
    # Clear cache
    factory.clear_cache()
    assert len(factory._cache) == 0


def test_format_prompt():
    """Test prompt formatting."""
    factory = PromptFactory()
    
    # Without context
    prompt1 = factory.format_prompt("default")
    assert prompt1 is not None
    
    # With context (currently not used, but should not error)
    prompt2 = factory.format_prompt("default", {"user_name": "Test"})
    assert prompt2 is not None


def test_get_prompt_factory_singleton():
    """Test that get_prompt_factory returns singleton."""
    factory1 = get_prompt_factory()
    factory2 = get_prompt_factory()
    
    assert factory1 is factory2
