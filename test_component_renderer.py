#!/usr/bin/env python3
"""
Test script for the ThemeComponentRenderer

This script demonstrates the capabilities of the new theme-aware component renderer
with various UI components and theme switching.
"""

import pygame
import sys
import os
import time
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Import from MetaMindIQTrain package
from MetaMindIQTrain.core.theme import Theme, ThemeProvider, set_theme, create_dark_theme, create_light_theme
from MetaMindIQTrain.clients.pygame.renderers.theme_component_renderer import ThemeComponentRenderer
from MetaMindIQTrain.config import scale_coordinates, scale_for_resolution

def main():
    """Main function to run the test."""
    # Initialize pygame
    pygame.init()
    
    # Set up the display
    screen_width = 1440
    screen_height = 1024
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Theme Component Renderer Test")
    
    # Set up clock for limiting FPS
    clock = pygame.time.Clock()
    fps = 60
    
    # Create themes
    dark_theme = create_dark_theme()
    light_theme = create_light_theme()
    
    # Set initial theme
    current_theme = dark_theme
    set_theme(current_theme)
    
    # Create renderer
    renderer = ThemeComponentRenderer(screen)
    
    # Main loop
    running = True
    last_theme_switch = time.time()
    progress_value = 0.0
    progress_direction = 0.01
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_t and time.time() - last_theme_switch > 0.5:
                    # Toggle theme
                    current_theme = light_theme if current_theme == dark_theme else dark_theme
                    set_theme(current_theme)
                    renderer.theme = current_theme
                    renderer.theme_provider = ThemeProvider(current_theme)
                    last_theme_switch = time.time()
                    
                    # Clear caches when theme changes
                    renderer.component_render_cache.clear()
                    renderer.cache_timestamps.clear()
        
        # Update progress bar demo
        progress_value += progress_direction
        if progress_value >= 1.0 or progress_value <= 0.0:
            progress_direction *= -1
        
        # Clear screen
        bg_color = current_theme.colors.get("background", (30, 30, 30))
        screen.fill(bg_color)
        
        # Draw title
        title = f"Component Renderer Test - {current_theme.name}"
        renderer.render_text(
            title,
            (screen_width // 2, 50),
            variant="title",
            textAlign="center"
        )
        
        # Draw subtitle
        subtitle = "Press 'T' to toggle theme, 'Esc' to exit"
        renderer.render_text(
            subtitle,
            (screen_width // 2, 100),
            variant="subtitle",
            textAlign="center"
        )
        
        # Draw containers section
        containers_title = "Containers"
        renderer.render_text(
            containers_title,
            (screen_width // 4, 150),
            variant="subtitle",
            textAlign="center"
        )
        
        # Draw panel container
        renderer.render_rectangle(
            (100, 200),
            (screen_width // 2 - 150, 200),
            variant="panel"
        )
        
        # Draw card container
        renderer.render_rectangle(
            (100, 420),
            (screen_width // 2 - 150, 200),
            variant="card"
        )
        
        # Draw buttons section
        buttons_title = "Buttons"
        renderer.render_text(
            buttons_title,
            (screen_width * 3 // 4, 150),
            variant="subtitle",
            textAlign="center"
        )
        
        # Draw primary button
        renderer.render_button(
            "Primary Button",
            (screen_width // 2 + 100, 200),
            (200, 50),
            variant="primary"
        )
        
        # Draw secondary button
        renderer.render_button(
            "Secondary Button",
            (screen_width // 2 + 100, 270),
            (200, 50),
            variant="secondary"
        )
        
        # Draw outline button
        renderer.render_button(
            "Outline Button",
            (screen_width // 2 + 100, 340),
            (200, 50),
            variant="outline"
        )
        
        # Draw disabled button
        renderer.render_button(
            "Disabled Button",
            (screen_width // 2 + 100, 410),
            (200, 50),
            variant="primary",
            state="disabled"
        )
        
        # Draw hover button
        renderer.render_button(
            "Hover Button",
            (screen_width // 2 + 100, 480),
            (200, 50),
            variant="primary",
            state="hover"
        )
        
        # Draw active button
        renderer.render_button(
            "Active Button",
            (screen_width // 2 + 100, 550),
            (200, 50),
            variant="primary",
            state="active"
        )
        
        # Draw text section
        text_title = "Text Styles"
        renderer.render_text(
            text_title,
            (screen_width // 4, 650),
            variant="subtitle",
            textAlign="center"
        )
        
        # Draw regular text
        renderer.render_text(
            "Regular Text",
            (100, 700)
        )
        
        # Draw title text
        renderer.render_text(
            "Title Text",
            (100, 740),
            variant="title"
        )
        
        # Draw subtitle text
        renderer.render_text(
            "Subtitle Text",
            (100, 780),
            variant="subtitle"
        )
        
        # Draw caption text
        renderer.render_text(
            "Caption Text",
            (100, 820),
            variant="caption"
        )
        
        # Draw label text
        renderer.render_text(
            "Label Text",
            (100, 860),
            variant="label"
        )
        
        # Draw highlighted text
        renderer.render_text(
            "Highlighted Text",
            (100, 900),
            state="highlighted"
        )
        
        # Draw error text
        renderer.render_text(
            "Error Text",
            (100, 940),
            state="error"
        )
        
        # Draw progress bars section
        progress_title = "Progress Bars"
        renderer.render_text(
            progress_title,
            (screen_width * 3 // 4, 650),
            variant="subtitle",
            textAlign="center"
        )
        
        # Draw default progress bar
        renderer.render_progress(
            (screen_width // 2 + 100, 700),
            (300, 20),
            progress_value
        )
        
        # Draw success progress bar
        renderer.render_progress(
            (screen_width // 2 + 100, 740),
            (300, 20),
            progress_value,
            variant="success"
        )
        
        # Draw warning progress bar
        renderer.render_progress(
            (screen_width // 2 + 100, 780),
            (300, 20),
            progress_value,
            variant="warning"
        )
        
        # Draw error progress bar
        renderer.render_progress(
            (screen_width // 2 + 100, 820),
            (300, 20),
            progress_value,
            variant="error"
        )
        
        # Draw circles
        renderer.render_circle(
            (screen_width // 2 + 150, 880),
            20
        )
        
        renderer.render_circle(
            (screen_width // 2 + 210, 880),
            20,
            variant="indicator"
        )
        
        renderer.render_circle(
            (screen_width // 2 + 270, 880),
            20,
            state="active"
        )
        
        renderer.render_circle(
            (screen_width // 2 + 330, 880),
            20,
            state="success"
        )
        
        renderer.render_circle(
            (screen_width // 2 + 390, 880),
            20,
            state="error"
        )
        
        # Update display
        pygame.display.flip()
        
        # Limit FPS
        clock.tick(fps)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 