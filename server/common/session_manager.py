"""
Session Manager for MetaMindIQTrain

This module provides session management functionality for the server implementations.
It handles session creation, retrieval, and cleanup.
"""

import logging
import time
from typing import Dict, Any, Optional, Set, List

# Import the module registry
from MetaMindIQTrain.module_registry import create_module_instance

# Configure logging
logger = logging.getLogger(__name__)

class SessionManager:
    """Session manager for the MetaMindIQTrain server.
    
    This class manages training sessions, providing methods to create, retrieve,
    and clean up sessions.
    """
    
    def __init__(self):
        """Initialize the session manager."""
        # Sessions dictionary maps session_id to module instance
        self.sessions: Dict[str, Any] = {}
        
        # Client tracking - maps session_id to set of client_ids
        self.clients: Dict[str, Set[str]] = {}
        
        # Cache maps session_id to cached state and timestamp
        self.cache: Dict[str, Dict[str, Any]] = {}
        
    def create_session(self, session_id: str, module: Any, client_id: str) -> bool:
        """Create a new training session with the given module and client.
        
        Args:
            session_id: The ID of the session to create
            module: The module instance
            client_id: The ID of the client creating the session
            
        Returns:
            True if session created successfully, False otherwise.
        """
        try:
            # Validate inputs
            if not session_id or not isinstance(session_id, str):
                logger.error("Invalid session_id provided to create_session")
                return False
            
            if not module:
                logger.error(f"Invalid module instance provided for session {session_id}")
                return False
            
            if not client_id or not isinstance(client_id, str):
                logger.error(f"Invalid client_id provided for session {session_id}")
                return False
            
            # Check if session already exists
            if session_id in self.sessions:
                logger.warning(f"Session {session_id} already exists, ending old session first")
                self.end_session(session_id)
            
            # Verify module has required methods
            if not hasattr(module, 'get_state') or not callable(getattr(module, 'get_state')):
                logger.error(f"Module instance for session {session_id} lacks required 'get_state' method")
                return False
            
            # Store the module instance
            self.sessions[session_id] = module
            
            # Initialize client set
            self.clients[session_id] = {client_id}
            
            # Record module activity time
            if hasattr(module, '__dict__'):
                module.last_activity = time.time()
            
            # Get initial state
            try:
                state = module.get_state()
                
                # Update cache
                self.update_cache(session_id, state)
                
                logger.info(f"Created session {session_id} with client {client_id}")
                return True
            except Exception as e:
                logger.error(f"Error getting initial state for session {session_id}: {e}")
                # Clean up the failed session
                self.sessions.pop(session_id, None)
                self.clients.pop(session_id, None)
                return False
            
        except Exception as e:
            logger.error(f"Error creating session {session_id}: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Any]:
        """Get a session by ID.
        
        Args:
            session_id: The ID of the session to retrieve
            
        Returns:
            The session module instance, or None if not found
        """
        return self.sessions.get(session_id)
    
    def add_client_to_session(self, session_id: str, client_id: str) -> bool:
        """Add a client to an existing session.
        
        Args:
            session_id: The ID of the session
            client_id: The ID of the client to add
            
        Returns:
            True if the client was added, False if the session wasn't found
        """
        if session_id in self.sessions:
            if session_id not in self.clients:
                self.clients[session_id] = set()
            
            self.clients[session_id].add(client_id)
            logger.info(f"Added client {client_id} to session {session_id}")
            return True
        
        return False
    
    def remove_client_from_session(self, session_id: str, client_id: str) -> bool:
        """Remove a client from a session.
        
        Args:
            session_id: The ID of the session
            client_id: The ID of the client to remove
            
        Returns:
            True if the client was removed, False if the session or client wasn't found
        """
        if session_id in self.clients and client_id in self.clients[session_id]:
            self.clients[session_id].remove(client_id)
            logger.info(f"Removed client {client_id} from session {session_id}")
            
            # If no clients left, end the session
            if not self.clients[session_id]:
                logger.info(f"No clients left in session {session_id}, ending it")
                return self.end_session(session_id)
            
            return True
        
        return False
    
    def validate_session(self, session_id: str) -> bool:
        """Validate that a session exists and is in a good state.
        
        Args:
            session_id: The ID of the session to validate
            
        Returns:
            True if the session is valid, False otherwise
        """
        if not session_id or not isinstance(session_id, str):
            logger.warning("Invalid session ID (empty or not a string)")
            return False
        
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found")
            return False
        
        module = self.sessions[session_id]
        if not module:
            logger.warning(f"Module for session {session_id} is None")
            return False
        
        # Check if module has essential methods
        if not hasattr(module, 'get_state') or not callable(getattr(module, 'get_state')):
            logger.warning(f"Module for session {session_id} lacks essential method 'get_state'")
            return False
        
        return True

    def end_session(self, session_id: str) -> bool:
        """End a session with improved error handling.
        
        Args:
            session_id: The ID of the session to end
            
        Returns:
            True if the session was ended, False if it wasn't found
        """
        if session_id not in self.sessions:
            # Session already gone, consider it ended successfully
            logger.info(f"Session {session_id} already ended")
            return True
        
        try:
            module = self.sessions[session_id]
            
            # Call end method if available
            if hasattr(module, 'end') and callable(getattr(module, 'end')):
                try:
                    module.end()
                except Exception as e:
                    logger.error(f"Error in module.end() for session {session_id}: {e}")
                    # Continue with cleanup despite the error
            
            # Remove from sessions and cache
            self.sessions.pop(session_id, None)
            self.cache.pop(session_id, None)
            
            # Clear client tracking
            self.clients.pop(session_id, None)
            
            logger.info(f"Ended session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error ending session {session_id}: {e}")
            # Try to clean up anyway to prevent resource leaks
            try:
                self.sessions.pop(session_id, None)
                self.cache.pop(session_id, None)
                self.clients.pop(session_id, None)
            except Exception:
                pass
            return False
    
    def cleanup_sessions(self, max_idle_time: int = 3600) -> int:
        """Clean up idle sessions.
        
        Args:
            max_idle_time: Maximum idle time in seconds before a session is cleaned up
            
        Returns:
            Number of sessions cleaned up
        """
        now = time.time()
        idle_sessions = []
        
        for session_id, module in self.sessions.items():
            if hasattr(module, 'last_activity'):
                idle_time = now - module.last_activity
                if idle_time > max_idle_time:
                    idle_sessions.append(session_id)
        
        for session_id in idle_sessions:
            logger.info(f"Cleaning up idle session {session_id}")
            self.end_session(session_id)
        
        return len(idle_sessions)
    
    def get_sessions_by_client(self, client_id: str) -> List[str]:
        """Get all sessions for a client.
        
        Args:
            client_id: The ID of the client
            
        Returns:
            List of session IDs
        """
        sessions = []
        for session_id, clients in self.clients.items():
            if client_id in clients:
                sessions.append(session_id)
        return sessions
    
    def update_cache(self, session_id: str, state: Dict[str, Any]) -> None:
        """Update the cache with the latest state.
        
        Args:
            session_id: Session ID
            state: Module state
        """
        self.cache[session_id] = {
            'state': state,
            'timestamp': time.time()
        }
    
    def get_cached_state(self, session_id: str, max_age: float = 1.0) -> Optional[Dict[str, Any]]:
        """Get cached state if available and recent.
        
        Args:
            session_id: Session ID
            max_age: Maximum age of cached state in seconds
            
        Returns:
            Cached state or None if not available or too old
        """
        if session_id in self.cache:
            entry = self.cache[session_id]
            age = time.time() - entry['timestamp']
            if age <= max_age:
                return entry['state']
        
        return None
    
    def get_active_sessions_count(self) -> int:
        """Get the number of active sessions.
        
        Returns:
            Number of active sessions
        """
        return len(self.sessions) 