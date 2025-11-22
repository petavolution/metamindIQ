#!/usr/bin/env python3
"""
Test All Modules With Generic Renderer

This script automatically tests all available modules using the enhanced generic renderer.
It ensures that each module can be properly initialized and rendered with the generic approach.
"""

import sys
import os
import time
import pygame
import argparse
from pathlib import Path

# Add parent directory to path
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))  # Add the project root to path

# Import the module registry and configuration
from MetaMindIQTrain.module_registry import create_module_instance, get_available_modules, configure_modules_display
from MetaMindIQTrain.config import SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_FPS
from MetaMindIQTrain.clients.pygame.renderers.enhanced_generic_renderer import EnhancedGenericRenderer

def main():
    """Test all available modules with the enhanced generic renderer."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Test all modules with generic renderer.")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode (no display)")
    parser.add_argument("--duration", type=int, default=5, help="Duration to display each module (seconds)")
    args = parser.parse_args()
    
    # Initialize PyGame
    pygame.init()
    
    # Set up display
    if args.headless:
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        print("Running in headless mode (no display)")
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        print(f"Running with display at {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    
    # Configure all modules to use the same display settings
    configure_modules_display(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Create fonts
    fonts = {
        'small': pygame.font.SysFont("Arial", 18),
        'medium': pygame.font.SysFont("Arial", 24),
        'large': pygame.font.SysFont("Arial", 36),
        'title': pygame.font.SysFont("Arial", 48, bold=True)
    }
    
    # Get all available modules
    available_modules = get_available_modules()
    print(f"Found {len(available_modules)} available modules:")
    for module_info in available_modules:
        print(f" - {module_info['name']} ({module_info['id']})")
    
    # Create a clock for framerate control
    clock = pygame.time.Clock()
    fps = DEFAULT_FPS
    
    # Test each module
    for module_info in available_modules:
        module_id = module_info['id']
        module_name = module_info['name']
        
        # Create the module instance
        try:
            module = create_module_instance(module_id)
            print(f"\nTesting module: {module_name} (ID: {module_id})")
            
            # Create renderer for this specific module
            renderer = EnhancedGenericRenderer(screen, module_id, fonts=fonts)
            print(f" - Created enhanced generic renderer for {module_name}")
            
            # Start a challenge if supported
            if hasattr(module, 'start_challenge'):
                module.start_challenge()
                print(f" - Started challenge for {module_name}")
            
            # Get initial state
            state = module.get_state()
            print(f" - Got initial state with {len(state)} keys")
            
            # Set window title
            pygame.display.set_caption(f"Testing {module_name}")
            
            # Display for specified duration
            start_time = time.time()
            
            while time.time() - start_time < args.duration:
                # Process events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                
                # Clear screen
                screen.fill((30, 30, 40))
                
                # Render the module
                renderer.render(state)
                
                # Draw test information
                info_text = fonts['small'].render(f"Testing {module_name} ({module_id})", True, (255, 255, 255))
                screen.blit(info_text, (10, 10))
                
                time_left = int(args.duration - (time.time() - start_time))
                time_text = fonts['small'].render(f"Time remaining: {time_left}s", True, (255, 255, 255))
                screen.blit(time_text, (10, 30))
                
                # Update display
                pygame.display.flip()
                
                # Cap the frame rate
                clock.tick(fps)
                
                # Get updated state periodically
                if hasattr(module, 'update') and callable(getattr(module, 'update')):
                    module.update()
                    state = module.get_state()
            
            print(f" - Successfully displayed {module_name} for {args.duration} seconds")
            
        except Exception as e:
            print(f" - ERROR: Failed to test {module_name}: {e}")
    
    pygame.quit()
    print("\nAll modules tested successfully!")

if __name__ == "__main__":
    main() 