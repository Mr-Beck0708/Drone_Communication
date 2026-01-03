"""
Session management for secure communication sessions.
"""

import time
from typing import Optional
from enum import Enum


class SessionState(Enum):
    """Session state enumeration."""
    INITIALIZED = "initialized"
    HANDSHAKE = "handshake"
    ACTIVE = "active"
    CLOSED = "closed"


class Session:
    """Manages a secure communication session."""
    
    def __init__(self, session_id: str):
        """
        Initialize a new session.
        
        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id
        self.state = SessionState.INITIALIZED
        self.created_at = time.time()
        self.last_activity = self.created_at
        self.shared_secret: Optional[bytes] = None
        self.peer_id: Optional[str] = None
        self.metadata = {}
    
    def start_handshake(self):
        """Start the handshake process."""
        self.state = SessionState.HANDSHAKE
        self.last_activity = time.time()
    
    def complete_handshake(self, shared_secret: bytes, peer_id: str):
        """
        Complete handshake and activate session.
        
        Args:
            shared_secret: Established shared secret
            peer_id: Peer identifier
        """
        self.shared_secret = shared_secret
        self.peer_id = peer_id
        self.state = SessionState.ACTIVE
        self.last_activity = time.time()
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = time.time()
    
    def close(self):
        """Close the session."""
        self.state = SessionState.CLOSED
        self.last_activity = time.time()
    
    def is_active(self) -> bool:
        """Check if session is active."""
        return self.state == SessionState.ACTIVE
    
    def is_expired(self, timeout: float = 3600.0) -> bool:
        """
        Check if session has expired.
        
        Args:
            timeout: Timeout in seconds (default: 1 hour)
            
        Returns:
            True if session has expired
        """
        if self.state == SessionState.CLOSED:
            return True
        
        elapsed = time.time() - self.last_activity
        return elapsed > timeout
    
    def get_session_info(self) -> dict:
        """Get session information."""
        return {
            "session_id": self.session_id,
            "state": self.state.value,
            "peer_id": self.peer_id,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "duration": time.time() - self.created_at,
        }
