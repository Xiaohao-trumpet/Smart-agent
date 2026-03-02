"""
Simple in-memory session store for managing user conversations.
In future phases, this will be replaced with Redis or a database backend.
"""

import time
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class Session:
    """Represents a user session with conversation history."""
    
    user_id: str
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def update_access_time(self) -> None:
        """Update the last accessed timestamp."""
        self.last_accessed = time.time()
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
        self.update_access_time()
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages in the conversation history."""
        return self.conversation_history.copy()
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history.clear()
        self.update_access_time()


class SessionStore:
    """
    In-memory session store with TTL support.
    
    Future enhancement: Replace with Redis or database for:
    - Persistence across restarts
    - Distributed deployment support
    - Better scalability
    """
    
    def __init__(self, ttl_seconds: int = 3600):
        self._sessions: Dict[str, Session] = {}
        self._lock = Lock()
        self._ttl_seconds = ttl_seconds
    
    def get_session(self, user_id: str) -> Optional[Session]:
        """
        Retrieve a session by user_id.
        Returns None if session doesn't exist or has expired.
        """
        with self._lock:
            session = self._sessions.get(user_id)
            if session:
                # Check if session has expired
                if time.time() - session.last_accessed > self._ttl_seconds:
                    del self._sessions[user_id]
                    return None
                session.update_access_time()
            return session
    
    def create_session(self, user_id: str) -> Session:
        """
        Create a new session for the given user_id.
        If a session already exists, return the existing one.
        """
        with self._lock:
            existing_session = self._sessions.get(user_id)
            if existing_session:
                existing_session.update_access_time()
                return existing_session
            
            new_session = Session(user_id=user_id)
            self._sessions[user_id] = new_session
            return new_session
    
    def delete_session(self, user_id: str) -> bool:
        """
        Delete a session by user_id.
        Returns True if session was deleted, False if it didn't exist.
        """
        with self._lock:
            if user_id in self._sessions:
                del self._sessions[user_id]
                return True
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove all expired sessions.
        Returns the number of sessions cleaned up.
        """
        current_time = time.time()
        expired_users = []
        
        with self._lock:
            for user_id, session in self._sessions.items():
                if current_time - session.last_accessed > self._ttl_seconds:
                    expired_users.append(user_id)
            
            for user_id in expired_users:
                del self._sessions[user_id]
        
        return len(expired_users)
    
    def get_session_count(self) -> int:
        """Get the total number of active sessions."""
        with self._lock:
            return len(self._sessions)


# Global session store instance
_session_store: Optional[SessionStore] = None


def get_session_store(ttl_seconds: int = 3600) -> SessionStore:
    """Get or create the global session store instance."""
    global _session_store
    if _session_store is None:
        _session_store = SessionStore(ttl_seconds=ttl_seconds)
    return _session_store
