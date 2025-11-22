#!/usr/bin/env python3
"""
Styled Symbol Memory Test

This script runs the Symbol Memory MVC module with enhanced styling
that matches the HTML/CSS implementation.
"""

import sys
import time
import pygame
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import modules directly
from modules.symbol_memory_mvc import SymbolMemory
from core.theme_manager import ThemeManager
from core.ui_renderer import UIRenderer
from core import config

def main():
    """Main entry point for the styled Symbol Memory test."""
    # Initialize pygame
    pygame.init()
    
    # Set up the window based on config
    screen_width, screen_height = config.get_resolution()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Styled Symbol Memory Test")
    
    # Set platform for theme manager
    ThemeManager.set_platform("pygame")
    
    # Create clock for FPS limiting
    clock = pygame.time.Clock()
    
    # Create the Symbol Memory module
    module = SymbolMemory(difficulty=3)
    
    # Create the UI renderer
    ui_renderer = UIRenderer(screen, screen_width, screen_height)
    
    # Game loop
    running = True
    last_time = time.time()
    
    while running:
        # Calculate dt
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    x, y = event.pos
                    result = module.handle_click(x, y)
        
        # Update module state
        module.update(dt)
        
        # Clear the screen
        screen.fill(config.UI_THEME["colors"]["bg_dark"])
        
        # Render UI layout
        ui_renderer.render_layout()
        
        # Render header with title
        ui_renderer.render_header("Symbol Memory", "Memorize the pattern and identify changes")
        
        # Get current module state
        state = module.get_state()
        
        # Render grid using enhanced styling
        module.view.render_grid(ui_renderer)
        
        # Render buttons using enhanced styling
        module.view.render_buttons(ui_renderer)
        
        # Display score
        score_text = f"Score: {state.get('score', 0)}"
        ui_renderer.render_text_with_shadow(
            score_text,
            (screen_width - 100, 30),
            font_key="regular",
            color=config.UI_THEME["colors"]["text_light"]
        )
        
        # Display level
        level_text = f"Level: {state.get('difficulty', 1)}"
        ui_renderer.render_text_with_shadow(
            level_text,
            (screen_width - 100, 60),
            font_key="regular",
            color=config.UI_THEME["colors"]["text_light"]
        )
        
        # Debugging info
        fps = clock.get_fps()
        ui_renderer.render_text(
            f"FPS: {fps:.1f}",
            (10, screen_height - 20),
            font_key="small",
            color=config.UI_THEME["colors"]["text_dark"],
            align="left"
        )
        
        # Update display
        pygame.display.flip()
        
        # Limit FPS
        clock.tick(config.DISPLAY_CONFIG["fps_limit"])

if __name__ == "__main__":
    main() 