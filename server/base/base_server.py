"""
Base Server for MetaMindIQTrain

This module provides an abstract base class for all server implementations.
It defines the common interface that all servers must implement.
"""

import abc
import logging
import threading
from typing import Dict, Any, Optional

from MetaMindIQTrain.server.common.session_manager import SessionManager
from MetaMindIQTrain.server.common.metrics import MetricsCollector

# Configure logging
logger = logging.getLogger(__name__)

class BaseServer(abc.ABC):
    """Abstract base class for all server implementations.
    
    This class defines the common interface and functionality for all
    MetaMindIQTrain server implementations.
    """
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8080, debug: bool = False):
        """Initialize the base server.
        
        Args:
            host: Host address to bind to
            port: Port to listen on
            debug: Enable debug mode
        """
        self.host = host
        self.port = port
        self.debug = debug
        
        # Set up logging
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Initialize common components
        self.session_manager = SessionManager()
        self.metrics_collector = MetricsCollector()
        
        # Start session cleanup thread
        self.cleanup_thread = threading.Thread(target=self._run_session_cleanup)
        self.cleanup_thread.daemon = True
        
        # Server state
        self.running = False
    
    def _run_session_cleanup(self, interval: int = 300, max_idle_time: int = 3600) -> None:
        """Run a periodic session cleanup.
        
        Args:
            interval: Cleanup interval in seconds
            max_idle_time: Maximum idle time in seconds before a session is cleaned up
        """
        import time
        
        while self.running:
            time.sleep(interval)
            try:
                cleaned_up = self.session_manager.cleanup_sessions(max_idle_time)
                if cleaned_up > 0:
                    logger.info(f"Cleaned up {cleaned_up} idle sessions")
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")
    
    @abc.abstractmethod
    def start(self) -> None:
        """Start the server."""
        self.running = True
        self.cleanup_thread.start()
        logger.info(f"Starting server on {self.host}:{self.port}")
    
    @abc.abstractmethod
    def stop(self) -> None:
        """Stop the server."""
        self.running = False
        logger.info("Server shutting down...")
    
    def get_active_sessions_count(self) -> int:
        """Get the number of active sessions.
        
        Returns:
            Number of active sessions
        """
        return len(self.session_manager.sessions) 