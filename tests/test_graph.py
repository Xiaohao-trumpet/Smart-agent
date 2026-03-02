"""
Tests for the LangGraph chat flow.
"""

import pytest
from unittest.mock import Mock
from backend.agents.graph import create_chat_graph, ChatState


@pytest.fixture
def mock_model_client():
    """Create a mock model client."""
    client = Mock()
    client.chat = Mock(return_value="Test response from model")
    return client


def test_create_chat_graph(mock_model_client):
    """Test that chat graph is created successfully."""
    graph = create_chat_graph(mock_model_client)
    assert graph is not None


def test_graph_invoke(mock_model_client):
    """Test invoking the chat graph."""
    graph = create_chat_graph(mock_model_client)
    
    initial_state = {
        "user_id": "test_user",
        "user_message": "Hello",
        "response": None,
        "session": None,
        "temperature": None,
        "max_tokens": None,
    }
    
    result = graph.invoke(initial_state)
    
    assert result["user_id"] == "test_user"
    assert result["user_message"] == "Hello"
    assert result["response"] == "Test response from model"
    
    # Verify model client was called
    mock_model_client.chat.assert_called_once_with(
        user_id="test_user",
        message="Hello",
        temperature=None,
        max_tokens=None,
        use_history=False,
    )
