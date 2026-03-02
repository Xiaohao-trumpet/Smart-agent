"""
Tests for the UniversalChat model abstraction.
"""

import pytest
from unittest.mock import Mock, patch
from backend.models.universal_chat import UniversalChat


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client."""
    with patch('backend.models.universal_chat.OpenAI') as mock:
        yield mock


@pytest.fixture
def chat_client(mock_openai_client):
    """Create a UniversalChat instance with mocked client."""
    return UniversalChat(
        model_name="test-model",
        base_url="http://localhost:8000",
        api_key="test-key",
        system_prompt="You are a test assistant.",
        default_temperature=0.7,
        default_max_tokens=100
    )


def test_initialization(chat_client):
    """Test that UniversalChat initializes correctly."""
    assert chat_client.model_name == "test-model"
    assert chat_client.base_url == "http://localhost:8000"
    assert chat_client.api_key == "test-key"
    assert chat_client.system_prompt == "You are a test assistant."
    assert chat_client.default_temperature == 0.7
    assert chat_client.default_max_tokens == 100


def test_get_messages_new_user(chat_client):
    """Test message building for a new user."""
    messages = chat_client._get_messages("user1", "Hello")
    
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "You are a test assistant."
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "Hello"


def test_update_history(chat_client):
    """Test conversation history update."""
    chat_client._update_history("user1", "Hello", "Hi there!")
    
    history = chat_client.get_history("user1")
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Hi there!"


def test_clear_history(chat_client):
    """Test clearing conversation history."""
    chat_client._update_history("user1", "Hello", "Hi there!")
    assert len(chat_client.get_history("user1")) == 2
    
    chat_client.clear_history("user1")
    assert len(chat_client.get_history("user1")) == 0


def test_chat_with_mock_response(chat_client):
    """Test chat method with mocked API response."""
    # Mock the API response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Test response"
    
    chat_client.client.chat.completions.create = Mock(return_value=mock_response)
    
    # Call chat
    response = chat_client.chat("user1", "Test message")
    
    assert response == "Test response"
    assert len(chat_client.get_history("user1")) == 2


def test_estimate_tokens(chat_client):
    """Test token estimation."""
    text = "This is a test message"
    tokens = chat_client.estimate_tokens(text)
    
    # Simple approximation: ~4 chars per token
    expected = len(text) // 4
    assert tokens == expected
