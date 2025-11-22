#!/usr/bin/env python3
"""
Basic Styled Test

This script implements a simplified test for our enhanced styling
without relying on complex imports.
"""

import sys
import time
import pygame
from pathlib import Path
import random

# Initialize pygame
pygame.init()

# Set up window
width, height = 1440, 1024  # Use our default resolution
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Styled UI Test - 70% Visual Scale")

# Set up fonts
title_font = pygame.font.SysFont("arial", 32)
regular_font = pygame.font.SysFont("arial", 24)
small_font = pygame.font.SysFont("arial", 18)

# Colors from our UI_THEME
colors = {
    "bg_dark": (30, 36, 44),        # Dark background (#1e242c)
    "bg_light": (40, 44, 52),       # Lighter background (#282c34)
    "primary": (50, 152, 255),      # Blue for primary elements (#3298ff)
    "secondary": (255, 149, 0),     # Orange for secondary elements (#ff9500)
    "success": (50, 255, 50),       # Green for correct answers (#32ff32)
    "error": (255, 50, 50),         # Red for incorrect answers (#ff3232)
    "text_light": (255, 255, 255),  # Light text (#ffffff)
    "text_dark": (170, 187, 204),   # Dark/muted text (#aabbcc)
    "border": (74, 85, 104)         # Border color (#4a5568)
}

# Bright colors for symbols to enhance cognitive engagement
bright_colors = [
    (255, 0, 0),      # Bright Red
    (0, 255, 0),      # Bright Green
    (0, 0, 255),      # Bright Blue
    (255, 255, 0),    # Yellow
    (255, 0, 255),    # Magenta
    (0, 255, 255),    # Cyan
    (255, 128, 0),    # Orange
    (128, 0, 255),    # Purple
    (255, 0, 128),    # Pink
    (0, 255, 128),    # Mint
    (128, 255, 0),    # Lime
    (0, 128, 255)     # Sky Blue
]

# UI layout percentages
header_height = int(height * 0.15)  # 15% of screen height
content_height = int(height * 0.70)  # 70% of screen height
footer_height = int(height * 0.15)  # 15% of screen height

content_y = header_height
footer_y = header_height + content_height

# Visual scaling factor (70%)
VISUAL_SCALE = 0.7
PRESERVE_FONT_SIZE = True

# Simplified Symbol Memory game state
class GameState:
    def __init__(self):
        self.phase = "memorize"  # memorize, hidden, recall, feedback
        self.score = 0
        self.grid_size = 4
        self.difficulty = 3
        self.symbols = ["■", "●", "▲", "◆", "★", "♦", "♥", "♣", "♠", "⬡", "⬢", "⌘"]
        self.symbol_colors = {}  # Dictionary to store symbol colors
        self.assign_symbol_colors()
        self.original_pattern = self.generate_pattern()
        self.modified_pattern = None
        self.was_modified = False
        self.modified_position = None
        self.user_answer = None
        self.timer = 0
        self.memorize_duration = 5  # seconds
    
    def assign_symbol_colors(self):
        """Assign a random bright color to each symbol for enhanced perception."""
        # Shuffle the bright colors
        available_colors = bright_colors.copy()
        random.shuffle(available_colors)
        
        # Assign a color to each symbol
        for i, symbol in enumerate(self.symbols):
            color_index = i % len(available_colors)
            self.symbol_colors[symbol] = available_colors[color_index]
    
    def generate_pattern(self):
        """Generate a random symbol pattern."""
        # Create empty grid
        grid = [["" for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Fill with random symbols
        num_symbols = self.grid_size * 2  # Fewer symbols for easier patterns
        positions = []
        
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                positions.append((r, c))
        
        # Randomly select positions
        selected_positions = random.sample(positions, num_symbols)
        
        # Place symbols
        for r, c in selected_positions:
            grid[r][c] = random.choice(self.symbols)
        
        return {"grid": grid, "size": self.grid_size}
    
    def update(self, dt):
        """Update game state."""
        if self.phase == "memorize":
            self.timer += dt
            if self.timer >= self.memorize_duration:
                self.phase = "hidden"
                self.timer = 0
                # Generate modified pattern
                self.modified_pattern = self.create_modified_pattern()
        elif self.phase == "hidden":
            self.timer += dt
            if self.timer >= 1:  # 1 second hidden phase
                self.phase = "recall"
                self.timer = 0
    
    def create_modified_pattern(self):
        """Create a modified version of the original pattern."""
        # Copy original pattern
        original_grid = self.original_pattern["grid"]
        new_grid = [row[:] for row in original_grid]  # Deep copy
        
        # Decide if we'll modify it (70% chance)
        self.was_modified = random.random() < 0.7
        
        if self.was_modified:
            # Find positions with symbols
            filled_positions = []
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    if original_grid[r][c]:
                        filled_positions.append((r, c))
            
            # Choose random position to modify
            if filled_positions:
                r, c = random.choice(filled_positions)
                self.modified_position = (r, c)
                
                # Replace with different symbol
                current_symbol = original_grid[r][c]
                new_symbols = [s for s in self.symbols if s != current_symbol]
                new_grid[r][c] = random.choice(new_symbols)
                
        return {"grid": new_grid, "size": self.grid_size}
    
    def process_answer(self, answer):
        """Process user's answer."""
        self.user_answer = answer
        self.phase = "feedback"
        
        # Calculate score
        correct = (answer == self.was_modified)
        score_change = 10 if correct else -5
        self.score += score_change
        
        return correct, score_change
    
    def next_round(self):
        """Start next round."""
        self.phase = "memorize"
        self.timer = 0
        self.user_answer = None
        self.original_pattern = self.generate_pattern()
        self.modified_pattern = None
        
        # Increase difficulty occasionally
        if random.random() < 0.3 and self.difficulty < 10:
            self.difficulty += 1
            if self.difficulty % 2 == 0 and self.grid_size < 6:
                self.grid_size += 1

# Create game state
game = GameState()

# Render functions that match our enhanced styling
def render_text_with_shadow(text, position, font=regular_font, color=colors["text_light"], shadow=True):
    """Render text with optional drop shadow."""
    if shadow:
        # Render shadow (offset and darker)
        shadow_surf = font.render(str(text), True, (0, 0, 0, 160))
        shadow_rect = shadow_surf.get_rect(center=(position[0] + 2, position[1] + 2))
        screen.blit(shadow_surf, shadow_rect)
    
    # Render main text
    text_surf = font.render(str(text), True, color)
    text_rect = text_surf.get_rect(center=position)
    screen.blit(text_surf, text_rect)
    return text_rect

def render_styled_button(text, rect, is_highlighted=False):
    """Render a styled button with rounded corners and hover effect."""
    # Button style parameters
    border_radius = 8
    
    # Get rect dimensions
    if not isinstance(rect, pygame.Rect):
        rect = pygame.Rect(*rect)
    
    # Apply scale if highlighted
    if is_highlighted:
        scale = 1.05
        # Calculate scaled dimensions
        scaled_width = int(rect.width * scale)
        scaled_height = int(rect.height * scale)
        
        # Center the scaled button on the original position
        x_offset = (scaled_width - rect.width) // 2
        y_offset = (scaled_height - rect.height) // 2
        
        rect = pygame.Rect(rect.x - x_offset, rect.y - y_offset, 
                         scaled_width, scaled_height)
    
    # Draw shadow
    shadow_color = (0, 0, 0, 128)
    shadow_rect = pygame.Rect(rect.x + 2, rect.y + 4, rect.width, rect.height)
    pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=border_radius)
    
    # Draw button background
    bg_color = colors["primary"]
    pygame.draw.rect(screen, bg_color, rect, border_radius=border_radius)
    
    # Draw border
    border_color = colors["border"]
    pygame.draw.rect(screen, border_color, rect, 1, border_radius=border_radius)
    
    # Render text
    render_text_with_shadow(text, rect.center)

def render_phase_indicator(text, phase_type):
    """Render a phase indicator matching HTML styling."""
    # Set properties based on phase
    if phase_type == "memorize":
        bg_color = colors["primary"]
    elif phase_type == "recall":
        bg_color = colors["secondary"]
    elif phase_type == "feedback_correct":
        bg_color = colors["success"]
    elif phase_type == "feedback_incorrect":
        bg_color = colors["error"]
    else:
        bg_color = colors["bg_dark"]
    
    # Calculate position
    x = width // 2
    y = content_y + 50  # Moved down 20 pixels (from original value of 30)
    
    # Render text to get dimensions
    text_surf = regular_font.render(str(text), True, colors["text_light"])
    text_width, text_height = text_surf.get_size()
    
    # Add padding with increased size for more space around text
    padding_x, padding_y = 70, 20  # Wider horizontally (70px) and shorter vertically (20px)
    rect_width = text_width + padding_x * 2
    rect_height = text_height + padding_y * 2
    
    # Apply visual scaling
    rect_width = int(rect_width * VISUAL_SCALE)
    rect_height = int(rect_height * VISUAL_SCALE)
    
    # Draw rounded rectangle with semi-transparency
    rect = pygame.Rect(x - rect_width//2, y - rect_height//2, rect_width, rect_height)
    border_radius = 20
    
    # Create surface with alpha for the background
    indicator_surf = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
    pygame.draw.rect(indicator_surf, (*bg_color[:3], 50), 
                   (0, 0, rect_width, rect_height), 
                   border_radius=border_radius)
    screen.blit(indicator_surf, rect)
    
    # Render text
    text_rect = text_surf.get_rect(center=(x, y))
    screen.blit(text_surf, text_rect)

def render_styled_grid_cell(rect, symbol=None, is_highlighted=False):
    """Render a styled grid cell matching HTML styling."""
    # Cell style parameters
    border_radius = 8
    
    # Create cell rectangle
    if not isinstance(rect, pygame.Rect):
        rect = pygame.Rect(*rect)
    
    # Store original dimensions for font size calculation
    original_width, original_height = rect.width, rect.height
    if PRESERVE_FONT_SIZE and VISUAL_SCALE < 1.0:
        # Calculate what the original size would have been before scaling
        original_width = int(original_width / VISUAL_SCALE)
        original_height = int(original_height / VISUAL_SCALE)
    
    # Apply scale if highlighted
    if is_highlighted:
        scale = 1.05
        # Calculate scaled dimensions
        scaled_width = int(rect.width * scale)
        scaled_height = int(rect.height * scale)
        
        # Center the scaled cell on the original position
        x_offset = (scaled_width - rect.width) // 2
        y_offset = (scaled_height - rect.height) // 2
        
        rect = pygame.Rect(rect.x - x_offset, rect.y - y_offset, 
                         scaled_width, scaled_height)
    
    # Draw shadow
    shadow_color = (0, 0, 0, 100)
    shadow_rect = pygame.Rect(rect.x + 2, rect.y + 4, rect.width, rect.height)
    pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=border_radius)
    
    # Draw cell background
    cell_bg_color = colors["primary"] if is_highlighted else colors["bg_light"]
    pygame.draw.rect(screen, cell_bg_color, rect, border_radius=border_radius)
    
    # Draw border
    border_color = colors["border"]
    pygame.draw.rect(screen, border_color, rect, 1, border_radius=border_radius)
    
    # Draw symbol if provided
    if symbol:
        # Calculate font size based on original cell dimensions for preserved font size
        # Apply 80% scaling to the symbol size (0.6 × 0.8 = 0.48)
        symbol_size_factor = 0.48  # 80% of the original 0.6 factor
        font_size = int(min(original_width, original_height) * symbol_size_factor)
        symbol_font = pygame.font.SysFont("arial", font_size)
        
        # Get symbol color from game state if available
        if symbol in game.symbol_colors:
            symbol_color = game.symbol_colors[symbol]
        else:
            symbol_color = colors["text_light"]
        
        # Create a temporary surface to measure the exact symbol dimensions
        symbol_surf = symbol_font.render(str(symbol), True, symbol_color)
        symbol_width, symbol_height = symbol_surf.get_size()
        
        # Calculate exact center coordinates with a slight downward adjustment
        center_x = rect.x + rect.width // 2 + int(font_size * 0.03)  # Reduce right offset to move symbol left
        center_y = rect.y + rect.height // 2 + int(font_size * 0.06)  # Maintain vertical position
        
        # Create a precise rect for the symbol position
        symbol_rect = symbol_surf.get_rect(center=(center_x, center_y))
        
        # Blit the symbol to the screen at the exact center position
        screen.blit(symbol_surf, symbol_rect)

def render_layout():
    """Render the layout with header, content, and footer areas."""
    # Draw background
    screen.fill(colors["bg_dark"])
    
    # Draw header
    header_rect = pygame.Rect(0, 0, width, header_height)
    pygame.draw.rect(screen, colors["bg_light"], header_rect)
    pygame.draw.rect(screen, colors["border"], header_rect, 1)
    
    # Draw content area
    content_rect = pygame.Rect(0, content_y, width, content_height)
    pygame.draw.rect(screen, colors["bg_dark"], content_rect)
    pygame.draw.rect(screen, colors["border"], content_rect, 1)
    
    # Draw footer
    footer_rect = pygame.Rect(0, footer_y, width, footer_height)
    pygame.draw.rect(screen, colors["bg_light"], footer_rect)
    pygame.draw.rect(screen, colors["border"], footer_rect, 1)

def render_header():
    """Render the header with title and description."""
    # Render title
    render_text_with_shadow(
        "Symbol Memory", 
        (width // 2, header_height // 3),
        font=title_font
    )
    
    # Render description
    render_text_with_shadow(
        "Memorize the pattern and identify changes", 
        (width // 2, header_height * 2 // 3),
        font=regular_font,
        color=colors["text_dark"]
    )

def render_grid():
    """Render the symbol grid."""
    # Get grid data
    if game.phase == "memorize":
        pattern = game.original_pattern
        show_symbols = True
        phase_text = "Memorize the pattern"
        phase_type = "memorize"
    elif game.phase == "hidden":
        pattern = game.original_pattern
        show_symbols = False
        phase_text = "Remembering..."
        phase_type = "memorize"
    elif game.phase == "recall":
        pattern = game.modified_pattern
        show_symbols = True
        phase_text = "Was the pattern changed?"
        phase_type = "recall"
    elif game.phase == "feedback":
        pattern = game.modified_pattern
        show_symbols = True
        
        if game.was_modified == game.user_answer:
            phase_text = "Correct!"
            phase_type = "feedback_correct"
        else:
            phase_text = "Incorrect!"
            phase_type = "feedback_incorrect"
    
    # Render phase indicator
    render_phase_indicator(phase_text, phase_type)
    
    # Calculate grid dimensions
    grid_margin = int(min(width, content_height) * 0.05)
    grid_padding = int(min(width, content_height) * 0.02)
    grid_size = pattern["size"]
    
    content_width = width
    
    # Calculate maximum grid size
    max_grid_width = content_width - (2 * grid_margin)
    max_grid_height = content_height - (2 * grid_margin)
    max_grid_size = min(max_grid_width, max_grid_height)
    
    # Apply the visual scaling factor (70%)
    max_grid_size = int(max_grid_size * VISUAL_SCALE)
    
    # Calculate cell size and spacing
    cell_margin_percent = 0.015  # 1.5% margin between cells
    total_cell_margin = (grid_size - 1) * (max_grid_size * cell_margin_percent)
    available_cell_space = max_grid_size - total_cell_margin
    cell_size = int(available_cell_space / grid_size)
    
    # Calculate total grid dimensions
    grid_width = (grid_size * cell_size) + total_cell_margin + (2 * grid_padding)
    grid_height = grid_width  # Square grid
    
    # Center grid in content area
    grid_x = (content_width - grid_width) // 2
    grid_y = content_y + (content_height - grid_height) // 2
    
    # Draw grid background
    grid_rect = pygame.Rect(grid_x, grid_y, grid_width, grid_height)
    pygame.draw.rect(screen, colors["bg_dark"], grid_rect, border_radius=10)
    
    # Draw cells
    for row in range(grid_size):
        for col in range(grid_size):
            # Calculate cell position
            cell_margin = cell_size * cell_margin_percent
            cell_x = grid_x + grid_padding + col * (cell_size + cell_margin)
            cell_y = grid_y + grid_padding + row * (cell_size + cell_margin)
            
            # Get symbol for this cell
            symbol = ""
            if row < len(pattern["grid"]) and col < len(pattern["grid"][row]):
                symbol = pattern["grid"][row][col] if show_symbols else ""
            
            # Determine if cell is highlighted
            is_highlighted = False
            if game.phase == "feedback" and game.was_modified:
                if game.modified_position and game.modified_position == (row, col):
                    is_highlighted = True
            
            # Render cell
            cell_rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size)
            render_styled_grid_cell(cell_rect, symbol, is_highlighted)

def render_buttons():
    """Render interaction buttons based on game phase."""
    # Calculate button dimensions
    # Apply visual scaling to button dimensions
    button_width = int(width * 0.15 * VISUAL_SCALE)  # 15% of screen width * scale
    button_height = int(footer_height * 0.5 * VISUAL_SCALE)  # 50% of footer height * scale
    button_margin = int(width * 0.05)  # 5% of screen width (not scaled)
    
    # Calculate button positions
    yes_x = width // 2 - button_width - button_margin // 2
    no_x = width // 2 + button_margin // 2
    button_y = footer_y + (footer_height - button_height) // 2
    
    yes_rect = pygame.Rect(yes_x, button_y, button_width, button_height)
    no_rect = pygame.Rect(no_x, button_y, button_width, button_height)
    continue_rect = pygame.Rect((width - button_width) // 2, button_y, button_width, button_height)
    
    # Get mouse position for hover effect
    mouse_pos = pygame.mouse.get_pos()
    
    # Render appropriate buttons based on phase
    if game.phase == "recall":
        # Yes/No buttons
        render_styled_button(
            "Yes", 
            yes_rect, 
            is_highlighted=yes_rect.collidepoint(mouse_pos)
        )
        render_styled_button(
            "No", 
            no_rect, 
            is_highlighted=no_rect.collidepoint(mouse_pos)
        )
    elif game.phase == "feedback":
        # Continue button
        render_styled_button(
            "Continue", 
            continue_rect, 
            is_highlighted=continue_rect.collidepoint(mouse_pos)
        )

def handle_click(x, y):
    """Handle mouse click events."""
    # Calculate button dimensions for hit testing
    button_width = int(width * 0.15 * VISUAL_SCALE)
    button_height = int(footer_height * 0.5 * VISUAL_SCALE)
    button_margin = int(width * 0.05)
    
    yes_x = width // 2 - button_width - button_margin // 2
    no_x = width // 2 + button_margin // 2
    button_y = footer_y + (footer_height - button_height) // 2
    
    yes_rect = pygame.Rect(yes_x, button_y, button_width, button_height)
    no_rect = pygame.Rect(no_x, button_y, button_width, button_height)
    continue_rect = pygame.Rect((width - button_width) // 2, button_y, button_width, button_height)
    
    # Process click based on game phase
    if game.phase == "recall":
        if yes_rect.collidepoint(x, y):
            game.process_answer(True)
        elif no_rect.collidepoint(x, y):
            game.process_answer(False)
    elif game.phase == "feedback":
        if continue_rect.collidepoint(x, y):
            game.next_round()

# Game loop
clock = pygame.time.Clock()
running = True
last_time = time.time()

while running:
    # Calculate delta time
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
                handle_click(*event.pos)
    
    # Update game state
    game.update(dt)
    
    # Render everything
    render_layout()
    render_header()
    render_grid()
    render_buttons()
    
    # Display score
    score_text = f"Score: {game.score}"
    render_text_with_shadow(
        score_text,
        (width - 100, 30),
        color=colors["text_light"],
        font=regular_font
    )
    
    # Display difficulty level
    level_text = f"Level: {game.difficulty}"
    render_text_with_shadow(
        level_text,
        (width - 100, 60),
        color=colors["text_light"],
        font=regular_font
    )
    
    # Debug info
    fps = clock.get_fps()
    render_text_with_shadow(
        f"FPS: {fps:.1f}",
        (10, height - 20),
        color=colors["text_dark"],
        font=small_font,
        shadow=False
    )
    
    # Update display
    pygame.display.flip()
    
    # Cap at 60 FPS
    clock.tick(60)

# Clean up
pygame.quit()
sys.exit(0) 