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


def test_graph_executes_memory_write_after_model():
    mock_model = Mock()
    mock_model.chat = Mock(return_value="Assistant reply")

    mock_memory = Mock()
    mock_memory.search_memories = Mock(return_value=[])
    mock_memory.extract_and_store = Mock(return_value=Mock(id="mem_123"))

    graph = create_chat_graph(
        model_client=mock_model,
        short_term_manager=None,
        memory_service=mock_memory,
        memory_enabled=True,
        memory_write_enabled=True,
        memory_top_k=3,
    )

    result = graph.invoke(
        {
            "user_id": "u1",
            "user_message": "My name is Xiaohao",
            "response": None,
            "session": None,
            "temperature": None,
            "max_tokens": None,
        }
    )

    assert result["response"] == "Assistant reply"
    assert result["auto_memory"] == "mem_123"
    mock_memory.extract_and_store.assert_called_once_with(
        user_id="u1",
        user_message="My name is Xiaohao",
    )


def test_graph_skips_memory_write_when_disabled():
    mock_model = Mock()
    mock_model.chat = Mock(return_value="Assistant reply")

    mock_memory = Mock()
    mock_memory.search_memories = Mock(return_value=[])
    mock_memory.extract_and_store = Mock(return_value=Mock(id="mem_123"))

    graph = create_chat_graph(
        model_client=mock_model,
        short_term_manager=None,
        memory_service=mock_memory,
        memory_enabled=True,
        memory_write_enabled=False,
        memory_top_k=3,
    )

    result = graph.invoke(
        {
            "user_id": "u2",
            "user_message": "My shoe size is 30",
            "response": None,
            "session": None,
            "temperature": None,
            "max_tokens": None,
        }
    )

    assert result["auto_memory"] is None
    mock_memory.extract_and_store.assert_not_called()
