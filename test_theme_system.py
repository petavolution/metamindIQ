#!/usr/bin/env python3
"""
Simple Theme System Test for Cognitive Training Modules

This script demonstrates a simplified implementation of the theme system
for cognitive training modules.
"""

import pygame
import sys
import time
import math
import os
import random
from pathlib import Path

# Initialize pygame
pygame.init()

# Set up display
width, height = 1440, 1024
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("MetaMindIQTrain Theme System Test")

# Simple theme class
class SimpleTheme:
    """A simple theme class for testing."""
    
    def __init__(self, name, colors, font_sizes, spacings, border_radius):
        """Initialize a theme.
        
        Args:
            name: Theme name
            colors: Dictionary of colors
            font_sizes: Dictionary of font sizes
            spacings: Dictionary of spacing values
            border_radius: Dictionary of border radius values
        """
        self.name = name
        self.colors = colors
        self.font_sizes = font_sizes
        self.spacings = spacings
        self.border_radius = border_radius

# Create dark theme
dark_theme = SimpleTheme(
    name="Dark Theme",
    colors={
        "background": (15, 18, 28),          # Dark blue-black background
        "card": (25, 30, 45),                # Slightly lighter card background
        "surface": (35, 40, 55),             # Surface elements
        "border": (60, 70, 90),              # Border color
        
        "text": (230, 235, 245),             # Primary text (white with slight blue tint)
        "text_secondary": (180, 185, 200),   # Secondary text (light gray)
        "text_disabled": (120, 125, 140),    # Disabled text (medium gray)
        
        "primary": (75, 120, 210),           # Primary action color (blue)
        "primary_hover": (90, 140, 230),     # Primary hover state
        "primary_active": (60, 100, 190),    # Primary active state
        "secondary": (70, 80, 100),          # Secondary action color
        "accent": (255, 140, 0),             # Accent color (orange)
        
        "success": (70, 200, 120),           # Success/correct (green)
        "error": (240, 80, 80),              # Error/incorrect (red)
        "warning": (255, 190, 50),           # Warning (yellow)
        "info": (70, 145, 240),              # Information (blue)
    },
    font_sizes={
        "small": 14,
        "medium": 18,
        "large": 24,
        "xlarge": 32,
    },
    spacings={
        "small": 8,
        "medium": 16,
        "large": 24,
        "xlarge": 32,
    },
    border_radius={
        "small": 4,
        "medium": 8,
        "large": 12,
    }
)

# Create light theme
light_theme = SimpleTheme(
    name="Light Theme",
    colors={
        "background": (245, 248, 250),       # Very light blue-gray
        "card": (255, 255, 255),             # White cards
        "surface": (240, 242, 245),          # Slightly off-white for surfaces
        "border": (200, 210, 220),           # Light gray border
        
        "text": (30, 40, 50),                # Dark text
        "text_secondary": (80, 90, 100),     # Medium-dark text
        "text_disabled": (150, 160, 170),    # Light gray text
        
        "primary": (60, 120, 210),           # Primary blue
        "primary_hover": (80, 140, 230),     # Brighter blue for hover
        "primary_active": (40, 100, 190),    # Darker blue for active
        "secondary": (100, 110, 130),        # Secondary action color
        "accent": (245, 130, 0),             # Orange accent
        
        "success": (50, 180, 100),           # Success green
        "error": (220, 60, 60),              # Error red
        "warning": (245, 180, 40),           # Warning yellow
        "info": (60, 130, 220),              # Information blue
    },
    font_sizes={
        "small": 14,
        "medium": 18,
        "large": 24,
        "xlarge": 32,
    },
    spacings={
        "small": 8,
        "medium": 16,
        "large": 24,
        "xlarge": 32,
    },
    border_radius={
        "small": 4,
        "medium": 8,
        "large": 12,
    }
)

# Current theme
current_theme = dark_theme

# Fonts
fonts = {}

def get_font(size):
    """Get a font with the specified size.
    
    Args:
        size: Font size
        
    Returns:
        Font object
    """
    if size not in fonts:
        fonts[size] = pygame.font.SysFont("Arial", size)
    return fonts[size]

def render_text(text, position, size="medium", color=None, align="left"):
    """Render text on the screen.
    
    Args:
        text: Text to render
        position: (x, y) position
        size: Font size name (small, medium, large, xlarge)
        color: Text color (or None to use theme text color)
        align: Text alignment (left, center, right)
    """
    if color is None:
        color = current_theme.colors["text"]
    
    font_size = current_theme.font_sizes[size]
    font = get_font(font_size)
    text_surface = font.render(text, True, color)
    
    x, y = position
    if align == "center":
        x -= text_surface.get_width() // 2
    elif align == "right":
        x -= text_surface.get_width()
    
    screen.blit(text_surface, (x, y))

def render_rectangle(position, size, color=None, border_width=0, border_color=None, border_radius=0):
    """Render a rectangle on the screen.
    
    Args:
        position: (x, y) position
        size: (width, height) size
        color: Fill color (or None to use theme surface color)
        border_width: Border width
        border_color: Border color (or None to use theme border color)
        border_radius: Border radius
    """
    if color is None:
        color = current_theme.colors["surface"]
    if border_color is None:
        border_color = current_theme.colors["border"]
    
    x, y = position
    width, height = size
    
    if border_radius > 0:
        # Draw a rounded rectangle
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, color, rect, 0, border_radius)
        if border_width > 0:
            pygame.draw.rect(screen, border_color, rect, border_width, border_radius)
    else:
        # Draw a regular rectangle
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, color, rect, 0)
        if border_width > 0:
            pygame.draw.rect(screen, border_color, rect, border_width)

def render_circle(center, radius, color=None, border_width=0, border_color=None):
    """Render a circle on the screen.
    
    Args:
        center: (x, y) center position
        radius: Circle radius
        color: Fill color (or None to use theme surface color)
        border_width: Border width
        border_color: Border color (or None to use theme border color)
    """
    if color is None:
        color = current_theme.colors["surface"]
    if border_color is None:
        border_color = current_theme.colors["border"]
    
    # Draw the circle
    pygame.draw.circle(screen, color, center, radius)
    if border_width > 0:
        pygame.draw.circle(screen, border_color, center, radius, border_width)

def render_button(text, position, size, color=None, text_color=None, border_radius=None):
    """Render a button on the screen.
    
    Args:
        text: Button text
        position: (x, y) position
        size: (width, height) size
        color: Button color (or None to use theme primary color)
        text_color: Text color (or None to use theme text color)
        border_radius: Border radius (or None to use theme medium border radius)
    """
    if color is None:
        color = current_theme.colors["primary"]
    if text_color is None:
        text_color = current_theme.colors["text"]
    if border_radius is None:
        border_radius = current_theme.border_radius["medium"]
    
    x, y = position
    width, height = size
    
    # Draw button background
    render_rectangle(position, size, color, 0, None, border_radius)
    
    # Draw text
    text_x = x + width // 2
    text_y = y + height // 2 - current_theme.font_sizes["medium"] // 2
    render_text(text, (text_x, text_y), "medium", text_color, "center")

def render_progress(position, size, value, color=None, background_color=None, border_radius=None):
    """Render a progress bar on the screen.
    
    Args:
        position: (x, y) position
        size: (width, height) size
        value: Progress value (0.0 to 1.0)
        color: Fill color (or None to use theme primary color)
        background_color: Background color (or None to use theme surface color)
        border_radius: Border radius (or None to use theme small border radius)
    """
    if color is None:
        color = current_theme.colors["primary"]
    if background_color is None:
        background_color = current_theme.colors["surface"]
    if border_radius is None:
        border_radius = current_theme.border_radius["small"]
    
    x, y = position
    width, height = size
    
    # Draw background
    render_rectangle(position, size, background_color, 0, None, border_radius)
    
    # Draw fill
    fill_width = int(width * max(0.0, min(1.0, value)))
    if fill_width > 0:
        render_rectangle((x, y), (fill_width, height), color, 0, None, border_radius)

def render_demo_components():
    """Render demo components to showcase the theme system."""
    # Current time for animations
    current_time = time.time()
    elapsed = current_time - start_time
    
    # Clear screen
    screen.fill(current_theme.colors["background"])
    
    # Render containers
    container_width = width * 0.8
    container_height = height * 0.7
    container_x = (width - container_width) // 2
    container_y = (height - container_height) // 2 + 50
    
    # Main container
    render_rectangle(
        (container_x, container_y),
        (container_width, container_height),
        current_theme.colors["card"],
        2,
        current_theme.colors["border"],
        current_theme.border_radius["large"]
    )
    
    # Title
    render_text(
        "Theme System Demo",
        (width // 2, container_y - 40),
        "xlarge",
        align="center"
    )
    
    # Left side - buttons and controls
    button_section_x = container_x + 50
    button_section_y = container_y + 50
    button_width = 200
    button_height = 50
    button_spacing = 20
    
    # Section title
    render_text(
        "Buttons & Controls",
        (button_section_x, button_section_y - 30),
        "large"
    )
    
    # Primary button
    render_button(
        "Primary Button",
        (button_section_x, button_section_y),
        (button_width, button_height),
        current_theme.colors["primary"]
    )
    
    # Secondary button
    render_button(
        "Secondary Button",
        (button_section_x, button_section_y + button_height + button_spacing),
        (button_width, button_height),
        current_theme.colors["secondary"]
    )
    
    # Danger button
    render_button(
        "Danger Button",
        (button_section_x, button_section_y + (button_height + button_spacing) * 2),
        (button_width, button_height),
        current_theme.colors["error"]
    )
    
    # Progress bar
    progress = (math.sin(elapsed * 2) + 1) / 2  # Oscillate between 0 and 1
    render_progress(
        (button_section_x, button_section_y + (button_height + button_spacing) * 3),
        (button_width, button_height // 2),
        progress,
        current_theme.colors["primary"]
    )
    
    # Timer bar
    timer_progress = (math.cos(elapsed * 2) + 1) / 2  # Oscillate between 0 and 1
    render_progress(
        (button_section_x, button_section_y + (button_height + button_spacing) * 4),
        (button_width, button_height // 2),
        timer_progress,
        current_theme.colors["warning"]
    )
    
    # Right side - symbols and elements
    symbol_section_x = container_x + container_width - 300
    symbol_section_y = container_y + 50
    symbol_size = 60
    symbol_spacing = 80
    
    # Section title
    render_text(
        "Symbols & Elements",
        (symbol_section_x, symbol_section_y - 30),
        "large"
    )
    
    # Default circle
    render_circle(
        (symbol_section_x + symbol_size//2, symbol_section_y + symbol_size//2),
        symbol_size//2,
        current_theme.colors["surface"],
        2,
        current_theme.colors["border"]
    )
    
    # Success circle
    render_circle(
        (symbol_section_x + symbol_size//2, symbol_section_y + symbol_size//2 + symbol_spacing),
        symbol_size//2,
        current_theme.colors["success"]
    )
    
    # Error circle
    render_circle(
        (symbol_section_x + symbol_size//2, symbol_section_y + symbol_size//2 + symbol_spacing * 2),
        symbol_size//2,
        current_theme.colors["error"]
    )
    
    # Primary circle
    render_circle(
        (symbol_section_x + symbol_size//2, symbol_section_y + symbol_size//2 + symbol_spacing * 3),
        symbol_size//2,
        current_theme.colors["primary"]
    )
    
    # Center section - text examples
    text_section_x = width // 2
    text_section_y = container_y + 100
    text_spacing = 40
    
    # Heading
    render_text(
        "Heading Text",
        (text_section_x, text_section_y),
        "xlarge",
        align="center"
    )
    
    # Subheading
    render_text(
        "Subheading Text",
        (text_section_x, text_section_y + text_spacing),
        "large",
        align="center"
    )
    
    # Body text
    render_text(
        "Body text with normal styling",
        (text_section_x, text_section_y + text_spacing * 2),
        "medium",
        align="center"
    )
    
    # Label text
    render_text(
        "Label text for form elements",
        (text_section_x, text_section_y + text_spacing * 3),
        "small",
        align="center"
    )
    
    # Secondary text
    render_text(
        "Secondary text for less important information",
        (text_section_x, text_section_y + text_spacing * 4),
        "small",
        current_theme.colors["text_secondary"],
        align="center"
    )
    
    # Bottom section - instructions
    instructions_y = container_y + container_height - 80
    
    render_text(
        "Press T to toggle theme | Press ESC to exit",
        (width // 2, instructions_y),
        "medium",
        current_theme.colors["text_secondary"],
        align="center"
    )
    
    # Theme info
    render_text(
        f"Current Theme: {current_theme.name}",
        (width // 2, 30),
        "large",
        align="center"
    )

def render_symbol_memory_demo():
    """Render a simplified symbol memory demo with theme support."""
    # Clear screen
    screen.fill(current_theme.colors["background"])
    
    # Title
    render_text(
        "Symbol Memory Demo",
        (width // 2, 50),
        "xlarge",
        align="center"
    )
    
    # Create a grid of symbols
    grid_size = 4
    cell_size = 80
    grid_width = grid_size * cell_size
    grid_height = grid_size * cell_size
    
    # Center the grid on screen
    start_x = (width - grid_width) // 2
    start_y = (height - grid_height) // 2
    
    # Grid container
    render_rectangle(
        (start_x - 10, start_y - 10),
        (grid_width + 20, grid_height + 20),
        current_theme.colors["card"],
        2,
        current_theme.colors["border"],
        current_theme.border_radius["medium"]
    )
    
    # Generate symbols for the grid
    symbols = ["■", "●", "▲", "◆", "★", "♦", "♥", "♣", "♠", "⬡", "⬢", "⌘"]
    
    # Get phase based on time
    current_time = time.time()
    elapsed = current_time - start_time
    phase = int(elapsed / 3) % 3  # Cycle through phases every 3 seconds
    
    # Determine symbol state based on phase
    # 0: Memorize, 1: Hidden, 2: Compare
    for row in range(grid_size):
        for col in range(grid_size):
            # Calculate position
            x = start_x + col * cell_size + cell_size // 2
            y = start_y + row * cell_size + cell_size // 2
            
            # Generate symbol based on row/col (deterministic)
            symbol_index = (row * grid_size + col) % len(symbols)
            symbol = symbols[symbol_index]
            
            # Draw cell background
            cell_rect = (
                start_x + col * cell_size + 5,
                start_y + row * cell_size + 5,
                cell_size - 10,
                cell_size - 10
            )
            
            # Determine cell state
            if phase == 0:  # Memorize
                # Draw symbol
                render_circle(
                    (x, y),
                    cell_size // 2 - 5,
                    current_theme.colors["surface"],
                    2,
                    current_theme.colors["border"]
                )
                
                # Draw symbol text
                render_text(
                    symbol,
                    (x, y - current_theme.font_sizes["large"] // 2),
                    "large",
                    align="center"
                )
            elif phase == 1:  # Hidden
                # Draw empty cell
                render_circle(
                    (x, y),
                    cell_size // 2 - 5,
                    current_theme.colors["surface"],
                    2,
                    current_theme.colors["border"]
                )
            else:  # Compare - show with some symbols modified
                # Determine if this cell should be modified (based on position)
                if (row + col) % 7 == 0:
                    # Modified cell
                    render_circle(
                        (x, y),
                        cell_size // 2 - 5,
                        current_theme.colors["primary"],
                        2,
                        current_theme.colors["border"]
                    )
                    
                    # Draw a different symbol
                    alt_symbol = symbols[(symbol_index + 5) % len(symbols)]
                    render_text(
                        alt_symbol,
                        (x, y - current_theme.font_sizes["large"] // 2),
                        "large",
                        current_theme.colors["text"],
                        align="center"
                    )
                else:
                    # Unmodified cell
                    render_circle(
                        (x, y),
                        cell_size // 2 - 5,
                        current_theme.colors["surface"],
                        2,
                        current_theme.colors["border"]
                    )
                    
                    # Draw original symbol
                    render_text(
                        symbol,
                        (x, y - current_theme.font_sizes["large"] // 2),
                        "large",
                        current_theme.colors["text"],
                        align="center"
                    )
    
    # Show current phase
    phase_text = "Memorize" if phase == 0 else "Hidden" if phase == 1 else "Compare"
    render_text(
        f"Phase: {phase_text}",
        (width // 2, height - 100),
        "large",
        align="center"
    )
    
    # Progress bar for the current phase
    phase_progress = (elapsed % 3) / 3
    render_progress(
        (width // 4, height - 50),
        (width // 2, 20),
        phase_progress,
        current_theme.colors["primary"] if phase == 0 else
        current_theme.colors["secondary"] if phase == 1 else
        current_theme.colors["warning"]
    )
    
    # Instructions
    render_text(
        "Press T to toggle theme | Press ESC to exit | Press D for demo components",
        (width // 2, height - 20),
        "small",
        current_theme.colors["text_secondary"],
        align="center"
    )

# Set up timing
start_time = time.time()
mode = "symbol_memory"  # Start with symbol memory demo

# Main loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_t:
                # Toggle theme
                current_theme = light_theme if current_theme == dark_theme else dark_theme
            elif event.key == pygame.K_d:
                # Toggle mode
                mode = "demo" if mode == "symbol_memory" else "symbol_memory"
    
    # Render based on mode
    if mode == "symbol_memory":
        render_symbol_memory_demo()
    else:
        render_demo_components()
    
    # Update display
    pygame.display.flip()
    
    # Cap at 60 FPS
    pygame.time.Clock().tick(60)

# Quit pygame
pygame.quit()
sys.exit() 