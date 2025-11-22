#!/usr/bin/env python3
"""
MetaMindIQTrain - Run Client

This script launches the PyGame client for the MetaMindIQTrain platform.
It configures the client and connects to the server.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure project dir is in path
project_dir = Path(__file__).resolve().parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

# Import configuration
try:
    # Try relative import first
    from config import SCREEN_WIDTH, SCREEN_HEIGHT
except ImportError:
    # Fall back to absolute import
    try:
        from MetaMindIQTrain.config import SCREEN_WIDTH, SCREEN_HEIGHT
    except ImportError:
        logger.error("Failed to import configuration. Using default values.")
        SCREEN_WIDTH = 1440
        SCREEN_HEIGHT = 1024

def check_dependencies():
    """Check if required dependencies are installed."""
    missing_deps = []
    optional_missing = []
    
    # Check for pygame
    try:
        import pygame
    except ImportError:
        missing_deps.append("pygame")
    
    # Check for socketio
    try:
        import socketio
    except ImportError:
        optional_missing.append("python-socketio (real-time updates won't be available)")
    
    # Check for other dependencies
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    # Report missing dependencies
    if missing_deps:
        logger.error(f"Required dependencies missing: {', '.join(missing_deps)}")
        logger.error("Please install them with: pip install " + " ".join(missing_deps))
        return False
    
    if optional_missing:
        logger.warning(f"Optional dependencies missing: {', '.join(optional_missing)}")
        logger.warning("For full functionality, install them with: pip install " + " ".join([d.split()[0] for d in optional_missing]))
    
    return True

def run_client(args):
    """Run the client with the given arguments.
    
    Args:
        args: Command line arguments
        
    Returns:
        Return code from the client process
    """
    if not check_dependencies():
        return 1
    
    try:
        # Import the client class
        try:
            from clients.pygame.client import ModularPyGameClient
        except ImportError:
            from MetaMindIQTrain.clients.pygame.client import ModularPyGameClient
        
        # Configure client settings
        client_options = {
            'server_url': f"http://{args.host}:{args.port}",
            'window_size': (args.width, args.height),
            'fullscreen': args.fullscreen,
            'polling_interval': args.polling_interval,
            'debug': args.debug
        }
        
        # Create and run the client
        client = ModularPyGameClient(client_options)
        return client.run()
    
    except ImportError as e:
        logger.error(f"Failed to import client: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error running client: {e}")
        return 1

def main():
    """Main entry point for the client runner."""
    parser = argparse.ArgumentParser(description='Run the MetaMindIQTrain client')
    parser.add_argument('--host', default='localhost', help='Server host address')
    parser.add_argument('--port', type=int, default=8080, help='Server port')
    parser.add_argument('--width', type=int, default=SCREEN_WIDTH, help='Window width')
    parser.add_argument('--height', type=int, default=SCREEN_HEIGHT, help='Window height')
    parser.add_argument('--fullscreen', action='store_true', help='Run in fullscreen mode')
    parser.add_argument('--module', help='Auto-select module on startup')
    parser.add_argument('--polling-interval', type=float, default=0.5, help='Polling interval for HTTP fallback (seconds)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Enable debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    return run_client(args)

if __name__ == '__main__':
    sys.exit(main()) 