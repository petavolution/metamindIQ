"""
Optimized Server Implementation for MetaMindIQTrain

This package provides optimized server implementations for the MetaMindIQTrain
platform, with specialized handlers for different module types.
"""

# Import the music module loader
try:
    from MetaMindIQTrain.server.optimized.music_module_loader import (
        MusicModuleLoader,
        get_music_module_loader
    )
    
    # Initialize the music module loader
    music_loader = get_music_module_loader()
    MUSIC_MODULES_AVAILABLE = True
except ImportError:
    MUSIC_MODULES_AVAILABLE = False

# Export public API
__all__ = [
    'MusicModuleLoader',
    'get_music_module_loader',
    'MUSIC_MODULES_AVAILABLE'
] 