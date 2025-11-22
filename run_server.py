#!/usr/bin/env python3
"""
MetaMindIQTrain - Run Server

This script provides a convenience wrapper to run the MetaMindIQTrain server.
It initializes the module registry and configures display settings.
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

# Get the project root directory
project_dir = Path(__file__).resolve().parent.parent

# Ensure the project is in the path
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

# Import the module registry
try:
    # Try relative import first
    from module_registry import configure_modules_display, get_available_modules
    from config import SCREEN_WIDTH, SCREEN_HEIGHT
except ImportError:
    # Fall back to absolute import
    from MetaMindIQTrain.module_registry import configure_modules_display, get_available_modules
    from MetaMindIQTrain.config import SCREEN_WIDTH, SCREEN_HEIGHT

def run_server(args):
    """Run the server with the given arguments.
    
    Args:
        args: Command line arguments
        
    Returns:
        Return code from the server process
    """
    try:
        # Configure display settings for modules using values from config.py
        configure_modules_display(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
        
        # Validate available modules
        available_modules = get_available_modules()
        logger.info(f"Available modules: {', '.join(m['id'] for m in available_modules)}")
        
        # Determine which server implementation to use
        if args.server_type == 'simple':
            logger.info("Starting simple server implementation...")
            try:
                from server.simple import run_server as simple_run_server
            except ImportError:
                from MetaMindIQTrain.server.simple import run_server as simple_run_server
            return simple_run_server(host=args.host, port=args.port, debug=args.debug)
        
        elif args.server_type == 'optimized':
            logger.info("Starting optimized server implementation...")
            try:
                from server.optimized import run_server as optimized_run_server
            except ImportError:
                from MetaMindIQTrain.server.optimized import run_server as optimized_run_server
            
            # Pass all the options specific to the optimized server
            return optimized_run_server(
                host=args.host,
                port=args.port,
                debug=args.debug,
                use_flask=not args.no_flask,
                use_websocket=not args.no_websocket
            )
        
        else:
            logger.error(f"Unknown server type: {args.server_type}")
            return 1
    
    except ImportError as e:
        logger.error(f"Failed to import server: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error running server: {e}")
        return 1

def main():
    """Main entry point for the server runner."""
    parser = argparse.ArgumentParser(description='Run the MetaMindIQTrain server')
    parser.add_argument('--host', default='0.0.0.0', help='Host address to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--server-type', choices=['simple', 'optimized'], default='optimized',
                       help='Server implementation to use (simple or optimized)')
    
    # Options specific to the optimized server
    parser.add_argument('--no-flask', action='store_true', help='Do not use Flask even if available (optimized server only)')
    parser.add_argument('--no-websocket', action='store_true', help='Do not use WebSocket even if available (optimized server only)')
    
    args = parser.parse_args()
    
    # Enable debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    return run_server(args)

if __name__ == '__main__':
    sys.exit(main()) 