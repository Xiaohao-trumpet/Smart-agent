"""
Pytest configuration and shared fixtures.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    with patch('backend.models.universal_chat.OpenAI') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        
        # Mock chat completion response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_instance.chat.completions.create.return_value = mock_response
        
        yield mock


@pytest.fixture
def test_client():
    """Create a test client for FastAPI."""
    from backend.main import app
    return TestClient(app)


@pytest.fixture
def sample_chat_request():
    """Sample chat request data."""
    return {
        "user_id": "test_user",
        "message": "Hello, how are you?"
    }


@pytest.fixture
def sample_chat_state():
    """Sample chat state for graph testing."""
    return {
        "user_id": "test_user",
        "user_message": "Hello",
        "response": None
    }
