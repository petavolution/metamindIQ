#!/usr/bin/env python3
"""
Main Entry Point for MetaMindIQTrain

This module provides an optimized main entry point for the MetaMindIQTrain application,
featuring better startup performance, module lazy loading, and simplified execution flow.
"""

import logging
import sys
import os
import argparse
import time
from typing import Dict, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(stream=sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments with sensible defaults.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Run MetaMindIQTrain with the optimized architecture')
    
    parser.add_argument(
        '--width', type=int, default=1024,
        help='Window width (default: 1024)'
    )
    parser.add_argument(
        '--height', type=int, default=768,
        help='Window height (default: 768)'
    )
    parser.add_argument(
        '--renderer', type=str, default='auto',
        choices=['auto', 'pygame', 'webgl', 'headless'],
        help='Renderer backend to use (default: auto)'
    )
    parser.add_argument(
        '--debug', action='store_true',
        help='Enable debug mode'
    )
    parser.add_argument(
        '--module', type=str, default='example',
        help='Module to load (default: example)'
    )
    parser.add_argument(
        '--fullscreen', action='store_true',
        help='Run in fullscreen mode'
    )
    parser.add_argument(
        '--fps', type=int, default=60,
        help='Target frames per second (default: 60)'
    )
    parser.add_argument(
        '--profile', action='store_true',
        help='Enable performance profiling'
    )
    
    return parser.parse_args()

def main():
    """Main entry point for the application with optimized flow."""
    start_time = time.time()
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Enable debug mode if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    # Lazy import core modules to improve startup time
    from MetaMindIQTrain.core.application import Application
    from MetaMindIQTrain.core.app_context import set_app_initialized, set_debug_mode, set_current_module
    
    # Initialize performance monitoring if requested
    if args.profile:
        try:
            import cProfile
            profiler = cProfile.Profile()
            profiler.enable()
            logger.info("Performance profiling enabled")
        except ImportError:
            logger.warning("cProfile not available, profiling disabled")
            args.profile = False
    
    # Create application instance directly rather than using singleton
    # This provides more control over initialization
    app = Application(app_name="MetaMindIQTrain")
    
    # Configure app based on arguments
    set_debug_mode(args.debug)
    
    # Apply renderer settings
    renderer_settings = {
        'width': args.width,
        'height': args.height,
        'renderer_backend': args.renderer,
        'fullscreen': args.fullscreen,
        'target_fps': args.fps
    }
    
    # Initialize the application
    logger.info("Initializing application...")
    if not app.initialize(**renderer_settings):
        logger.error("Failed to initialize application")
        return 1
    
    # Use a module registry approach for dynamic module loading
    modules = {}
    
    # Register built-in modules
    def register_module(name, creator_func):
        """Register a module creation function."""
        modules[name] = creator_func
    
    # Register the example module
    def load_example_module():
        """Lazy load the example module."""
        from MetaMindIQTrain.modules.example_module import create_module
        return create_module()
    
    register_module('example', load_example_module)
    
    # Register music modules if available
    try:
        def load_music_theory_module():
            """Lazy load the music theory module."""
            from MetaMindIQTrain.modules.music.music_theory_simplified import create_module
            return create_module()
        
        register_module('music_theory', load_music_theory_module)
        logger.info("Music modules registered")
    except ImportError:
        logger.info("Music modules not available")
    
    # Load the requested module
    module_name = args.module
    if module_name not in modules:
        logger.error(f"Unknown module: {module_name}")
        logger.info(f"Available modules: {', '.join(modules.keys())}")
        return 1
    
    try:
        # Create the module instance using the factory function
        logger.info(f"Loading module: {module_name}")
        module_instance = modules[module_name]()
        
        # Set the module as the root component
        app.set_root_component(module_instance)
        
        # Update app context
        set_current_module(
            module_id=module_instance.id,
            module_name=getattr(module_instance, 'name', module_name.title()),
            module_type=module_name
        )
        
        # Mark application as fully initialized
        set_app_initialized(True)
        
        # Report startup time
        startup_time = time.time() - start_time
        logger.info(f"Application startup completed in {startup_time:.2f} seconds")
        
        # Run the application main loop
        app.run()
        
        # Clean up profiler if active
        if args.profile:
            profiler.disable()
            import pstats
            from io import StringIO
            
            # Sort statistics by cumulative time
            s = StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats('cumtime')
            ps.print_stats(30)  # Print top 30 functions
            print(s.getvalue())
        
        return 0
        
    except Exception as e:
        logger.error(f"Error starting application: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 