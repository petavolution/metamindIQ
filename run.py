#!/usr/bin/env python3
"""
MetaMindIQTrain Runner

This is the main entry point for the MetaMindIQTrain application.
It initializes and runs the application with the specified settings.
"""

import argparse
import logging
import sys
import os
from pathlib import Path

# Ensure the package is in the path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(project_root, 'iqtrain.log'), mode='w')
    ]
)
logger = logging.getLogger('MetaMindIQTrain')

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Run the MetaMindIQTrain application')
    
    parser.add_argument(
        '--width', type=int, default=1024,
        help='Window width (default: 1024)'
    )
    parser.add_argument(
        '--height', type=int, default=768,
        help='Window height (default: 768)'
    )
    parser.add_argument(
        '--backend', type=str, default='auto',
        choices=['auto', 'pygame', 'webgl', 'headless'],
        help='Renderer backend (default: auto)'
    )
    parser.add_argument(
        '--module', type=str,
        help='Module to start automatically'
    )
    parser.add_argument(
        '--show-fps', action='store_true',
        help='Show FPS counter'
    )
    parser.add_argument(
        '--debug', action='store_true',
        help='Enable debug logging'
    )
    
    return parser.parse_args()

def main():
    """Run the application."""
    args = parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    logger.info("Starting MetaMindIQTrain")
    
    try:
        # Import the application - try multiple approaches for robustness
        try:
            from core.app import get_application
        except ImportError:
            from MetaMindIQTrain.core.app import get_application
        
        # Get the application instance
        app = get_application()
        
        # Initialize the application
        title = "MetaMindIQTrain - Advanced Cognitive Training"
        if not app.initialize(args.width, args.height, title, args.backend):
            logger.error("Failed to initialize application")
            return 1
            
        # Set FPS display if requested
        if args.show_fps:
            app.toggle_fps_display()
            
        # Start a module if specified
        if args.module:
            if not app.start_module(args.module):
                logger.warning(f"Could not start module '{args.module}', using module selector")
                # Use the first available music module as a fallback
                music_modules = app.list_modules('music')
                if music_modules:
                    app.start_module(music_modules[0]['id'])
        
        # Run the application
        app.run()
        
        # Shutdown
        app.shutdown()
        
        logger.info("Application exited normally")
        return 0
        
    except Exception as e:
        logger.exception(f"Error running application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
 