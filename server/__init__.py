"""
MetaMindIQTrain Server Package

This package provides server implementations for the MetaMindIQTrain platform.
It includes both a simple, reliable server and an optimized server with advanced features.
"""

# Version information
__version__ = '1.0.0'

# Import server implementations for convenience
from MetaMindIQTrain.server.simple import SimpleServer
from MetaMindIQTrain.server.optimized import OptimizedServer

# Import common utilities
from MetaMindIQTrain.server.common.session_manager import SessionManager
from MetaMindIQTrain.server.common.metrics import MetricsCollector

__all__ = [
    'SimpleServer', 
    'OptimizedServer',
    'SessionManager',
    'MetricsCollector'
]

# Server implementations
AVAILABLE_SERVERS = {
    'simple': {
        'name': 'Simple Server',
        'description': 'A reliable server implementation with minimal dependencies',
        'module': 'MetaMindIQTrain.server.simple.server'
    },
    'optimized': {
        'name': 'Optimized Server',
        'description': 'A high-performance server with advanced features like WebSockets and caching',
        'module': 'MetaMindIQTrain.server.optimized.server'
    },
    'flask': {
        'name': 'Flask Server',
        'description': 'Legacy Flask server implementation (maintained for reference)',
        'module': 'MetaMindIQTrain.server.flask_app'
    }
}

def get_available_servers():
    """Get the list of available server implementations.
    
    Returns:
        Dictionary of available servers with metadata
    """
    return AVAILABLE_SERVERS 