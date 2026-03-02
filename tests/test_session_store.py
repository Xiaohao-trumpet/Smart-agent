"""
Tests for the session store.
"""

import pytest
import time
from backend.session_store import SessionStore, Session


@pytest.fixture
def session_store():
    """Create a session store with short TTL for testing."""
    return SessionStore(ttl_seconds=2)


def test_create_session(session_store):
    """Test creating a new session."""
    session = session_store.create_session("user1")
    
    assert session.user_id == "user1"
    assert len(session.conversation_history) == 0


def test_get_existing_session(session_store):
    """Test retrieving an existing session."""
    session_store.create_session("user1")
    retrieved = session_store.get_session("user1")
    
    assert retrieved is not None
    assert retrieved.user_id == "user1"


def test_get_nonexistent_session(session_store):
    """Test retrieving a non-existent session."""
    session = session_store.get_session("nonexistent")
    assert session is None


def test_delete_session(session_store):
    """Test deleting a session."""
    session_store.create_session("user1")
    deleted = session_store.delete_session("user1")
    
    assert deleted is True
    assert session_store.get_session("user1") is None


def test_session_expiration(session_store):
    """Test that sessions expire after TTL."""
    session_store.create_session("user1")
    
    # Wait for TTL to expire
    time.sleep(2.5)
    
    # Session should be expired
    session = session_store.get_session("user1")
    assert session is None


def test_cleanup_expired_sessions(session_store):
    """Test cleanup of expired sessions."""
    session_store.create_session("user1")
    session_store.create_session("user2")
    
    # Wait for expiration
    time.sleep(2.5)
    
    # Cleanup
    cleaned = session_store.cleanup_expired_sessions()
    assert cleaned == 2
    assert session_store.get_session_count() == 0
