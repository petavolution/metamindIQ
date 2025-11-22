#!/usr/bin/env python3
"""
Basic ExpandVision Test

This script provides a minimal pygame environment to test the ExpandVision concept
without relying on complex imports.
"""

import os
import sys
import time
import pygame
import random
import math
from pathlib import Path

# Initialize pygame
pygame.init()

# Set up window
width, height = 1024, 768
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Basic ExpandVision Test")

# Set up fonts
title_font = pygame.font.SysFont("arial", 24)
regular_font = pygame.font.SysFont("arial", 18)
small_font = pygame.font.SysFont("arial", 14)

# Set up colors
colors = {
    "background": (240, 240, 240),
    "text": (0, 0, 0),
    "grid_border": (100, 100, 100),
    "grid_bg": (230, 230, 230),
    "focus_area": (230, 250, 230),
    "button": (200, 200, 200),
    "button_hover": (180, 180, 180),
    "selected": (100, 180, 255),
    "correct": (100, 255, 100),
    "incorrect": (255, 100, 100),
    "hidden": (80, 80, 100),
    "target": (255, 200, 0),
    "focus": (0, 200, 0, 128)
}

# Define ExpandVisionModel (simplified version)
class ExpandVisionModel:
    """Model component for ExpandVision test."""
    
    def __init__(self, difficulty=3):
        """Initialize the model with game state and business logic."""
        # Game settings
        self.difficulty = max(1, min(10, difficulty))
        self.level = self.difficulty
        self.grid_size = self._calculate_grid_size()
        self.score = 0
        
        # Game state
        self.game_state = "challenge_active"  # challenge_active, challenge_complete, feedback
        self.grid = []  # The complete grid of symbols
        self.visible_grid = []  # Grid with hidden parts
        self.focus_position = [0, 0]  # Current focus position (row, col)
        self.focus_radius = 2  # Radius of visible area around focus
        self.target_position = None  # Target position to find
        self.target_symbol = None  # Symbol to find
        self.selected_position = None  # Player's selected position
        self.answered = False  # Whether user has submitted an answer
        self.correct_answer = None  # Whether the last answer was correct
        
        # Performance tracking
        self.round_start_time = time.time()
        self.challenge_time = 0
        self.moves_made = 0
        
        # Symbol set (simplified)
        self.symbols = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
        
        # Create first challenge
        self.create_new_challenge()
    
    def _calculate_grid_size(self):
        """Calculate grid size based on difficulty."""
        return max(5, min(15, 5 + self.difficulty))
    
    def create_new_challenge(self):
        """Create a new expand vision challenge."""
        # Adjust grid size based on level
        self.grid_size = self._calculate_grid_size()
        
        # Reset state
        self.grid = self.generate_random_grid(self.grid_size)
        self.visible_grid = self.create_visible_grid()
        self.focus_position = [self.grid_size // 2, self.grid_size // 2]  # Center
        self.selected_position = None
        self.answered = False
        self.correct_answer = None
        self.round_start_time = time.time()
        self.moves_made = 0
        
        # Choose random target
        row = random.randint(0, self.grid_size - 1)
        col = random.randint(0, self.grid_size - 1)
        self.target_position = [row, col]
        self.target_symbol = self.grid[row][col]
        
        # Update the visible grid
        self.update_visible_area()
    
    def generate_random_grid(self, size):
        """Generate a random grid of symbols."""
        # Create empty grid
        grid = [[None for _ in range(size)] for _ in range(size)]
        
        # Fill with random symbols
        for row in range(size):
            for col in range(size):
                grid[row][col] = random.choice(self.symbols)
        
        return grid
    
    def create_visible_grid(self):
        """Create a grid where all cells are initially hidden."""
        return [["?" for _ in range(self.grid_size)] for _ in range(self.grid_size)]
    
    def update_visible_area(self):
        """Update the visible area based on current focus position."""
        # Reset visible grid first
        self.visible_grid = [["?" for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Get focus center
        center_row, center_col = self.focus_position
        
        # Reveal area around focus
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                # Calculate distance from focus
                distance = max(abs(row - center_row), abs(col - center_col))
                
                # Reveal if within focus radius
                if distance <= self.focus_radius:
                    self.visible_grid[row][col] = self.grid[row][col]
    
    def move_focus(self, direction):
        """Move the focus point in the specified direction."""
        row, col = self.focus_position
        
        if direction == "up":
            row = max(0, row - 1)
        elif direction == "down":
            row = min(self.grid_size - 1, row + 1)
        elif direction == "left":
            col = max(0, col - 1)
        elif direction == "right":
            col = min(self.grid_size - 1, col + 1)
        
        # Only count as a move if actually moved
        if (row, col) != tuple(self.focus_position):
            self.focus_position = [row, col]
            self.moves_made += 1
            self.update_visible_area()
    
    def handle_click(self, x, y):
        """Handle user click at position (x, y)."""
        # Skip if challenge is complete
        if self.game_state != "challenge_active":
            # Check if clicked continue button
            if self.game_state == "challenge_complete" and 462 <= x <= 562 and 670 <= y <= 720:
                self.create_new_challenge()
                self.game_state = "challenge_active"
            return
        
        # Calculate grid positions
        grid_rect = self.calculate_grid_rect()
        grid_x, grid_y, grid_width, grid_height = grid_rect
        
        # Check if clicked inside grid
        if grid_x <= x < grid_x + grid_width and grid_y <= y < grid_y + grid_height:
            # Calculate cell size
            cell_size = grid_width / self.grid_size
            
            # Calculate clicked cell
            cell_col = int((x - grid_x) / cell_size)
            cell_row = int((y - grid_y) / cell_size)
            
            # Set as selected position
            self.selected_position = [cell_row, cell_col]
        
        # Check if clicked direction buttons
        button_y = 600
        button_spacing = 50
        button_size = 40
        
        # Up button
        if 487 <= x <= 487 + button_size and button_y - button_size <= y <= button_y:
            self.move_focus("up")
        
        # Left button
        if 487 - button_spacing <= x <= 487 - button_spacing + button_size and button_y <= y <= button_y + button_size:
            self.move_focus("left")
        
        # Right button
        if 487 + button_spacing <= x <= 487 + button_spacing + button_size and button_y <= y <= button_y + button_size:
            self.move_focus("right")
        
        # Down button
        if 487 <= x <= 487 + button_size and button_y + button_size <= y <= button_y + 2 * button_size:
            self.move_focus("down")
        
        # Check if clicked submit button
        if 462 <= x <= 562 and 670 <= y <= 720 and self.selected_position is not None:
            self.check_answer()
    
    def calculate_grid_rect(self):
        """Calculate the rectangle for the grid."""
        grid_size = min(500, 500)
        grid_x = (width - grid_size) // 2
        grid_y = 150
        
        return (grid_x, grid_y, grid_size, grid_size)
    
    def check_answer(self):
        """Check if user's answer is correct."""
        if self.selected_position is None:
            return
        
        # Compare selected position with target
        self.correct_answer = (
            self.selected_position[0] == self.target_position[0] and
            self.selected_position[1] == self.target_position[1]
        )
        
        # Update score
        if self.correct_answer:
            # Base points + efficiency bonus
            base_points = 10 * self.difficulty
            efficiency_bonus = max(0, 30 - self.moves_made) * 2
            time_bonus = max(0, 60 - int(time.time() - self.round_start_time))
            
            self.score += base_points + efficiency_bonus + time_bonus
        
        # Mark challenge as complete
        self.game_state = "challenge_complete"
        self.answered = True
        
        # Reveal entire grid
        self.visible_grid = [row[:] for row in self.grid]
    
    def update(self, dt):
        """Update model state based on elapsed time."""
        # Update challenge time
        if self.game_state == "challenge_active":
            self.challenge_time = time.time() - self.round_start_time

# Define a simple view component
class SimpleExpandVisionView:
    """View component for ExpandVision test."""
    
    def __init__(self, screen, fonts):
        self.screen = screen
        self.fonts = fonts
    
    def build_components(self, model):
        """Build UI components from model state."""
        components = []
        
        # Add title
        components.append({
            "type": "text",
            "text": "ExpandVision Training",
            "position": [width // 2, 50],
            "font_size": 24,
            "color": (0, 0, 0)
        })
        
        # Add score
        components.append({
            "type": "text",
            "text": f"Score: {model.score}",
            "position": [80, 50],
            "font_size": 18,
            "color": (0, 0, 0)
        })
        
        # Add level
        components.append({
            "type": "text",
            "text": f"Level: {model.level}",
            "position": [80, 80],
            "font_size": 18,
            "color": (0, 0, 0)
        })
        
        # Add target to find
        components.append({
            "type": "text",
            "text": f"Find symbol: {model.target_symbol}",
            "position": [width // 2, 100],
            "font_size": 24,
            "color": colors["target"]
        })
        
        # Add instruction text
        if model.game_state == "challenge_active":
            instruction_text = "Use the navigation controls to move the focus. Click on the grid to select the target."
        elif model.game_state == "challenge_complete":
            if model.correct_answer:
                instruction_text = "Correct! You found the target."
            else:
                instruction_text = "Incorrect! The target was elsewhere."
        else:
            instruction_text = ""
        
        components.append({
            "type": "text",
            "text": instruction_text,
            "position": [width // 2, 130],
            "font_size": 18,
            "color": (0, 0, 100)
        })
        
        # Add timer
        if model.game_state == "challenge_active":
            components.append({
                "type": "text",
                "text": f"Time: {int(model.challenge_time)}s",
                "position": [width - 80, 50],
                "font_size": 18,
                "color": (0, 0, 0)
            })
        
        # Add moves counter
        components.append({
            "type": "text",
            "text": f"Moves: {model.moves_made}",
            "position": [width - 80, 80],
            "font_size": 18,
            "color": (0, 0, 0)
        })
        
        # Add grid background
        grid_rect = model.calculate_grid_rect()
        grid_x, grid_y, grid_width, grid_height = grid_rect
        
        components.append({
            "type": "rect",
            "position": [grid_x, grid_y],
            "size": [grid_width, grid_height],
            "color": colors["grid_bg"],
            "border_color": colors["grid_border"],
            "border_width": 2
        })
        
        # Add grid cells
        cell_size = grid_width / model.grid_size
        
        for row in range(model.grid_size):
            for col in range(model.grid_size):
                # Calculate cell position
                cell_x = grid_x + col * cell_size
                cell_y = grid_y + row * cell_size
                
                # Get cell content
                cell_text = model.visible_grid[row][col]
                
                # Determine cell color
                cell_color = colors["grid_bg"]
                
                # If game is complete, highlight target and selection
                if model.game_state == "challenge_complete":
                    if row == model.target_position[0] and col == model.target_position[1]:
                        cell_color = colors["target"]
                    
                    if model.selected_position and row == model.selected_position[0] and col == model.selected_position[1]:
                        if model.correct_answer:
                            cell_color = colors["correct"]
                        else:
                            cell_color = colors["incorrect"]
                
                # If cell is within focus area, add subtle highlight
                if model.visible_grid[row][col] != "?":
                    # Distance from focus
                    focus_row, focus_col = model.focus_position
                    distance = max(abs(row - focus_row), abs(col - focus_col))
                    
                    if distance <= model.focus_radius:
                        cell_color = colors["focus_area"]
                
                # Add cell background
                components.append({
                    "type": "rect",
                    "position": [cell_x, cell_y],
                    "size": [cell_size, cell_size],
                    "color": cell_color,
                    "border_color": colors["grid_border"],
                    "border_width": 1
                })
                
                # Add cell text
                components.append({
                    "type": "text",
                    "text": cell_text,
                    "position": [cell_x + cell_size/2, cell_y + cell_size/2],
                    "font_size": 16,
                    "color": colors["text"] if cell_text != "?" else colors["hidden"]
                })
        
        # Add focus indicator
        focus_row, focus_col = model.focus_position
        focus_x = grid_x + focus_col * cell_size
        focus_y = grid_y + focus_row * cell_size
        
        components.append({
            "type": "focus",
            "position": [focus_x, focus_y],
            "size": [cell_size, cell_size],
            "color": (0, 200, 100, 128),
            "border_color": (0, 200, 100),
            "border_width": 3
        })
        
        # Add navigation controls
        button_y = 600
        button_spacing = 50
        button_size = 40
        
        # Up button
        components.append({
            "type": "button",
            "text": "↑",
            "position": [487, button_y - button_size],
            "size": [button_size, button_size],
            "active": model.game_state == "challenge_active"
        })
        
        # Left button
        components.append({
            "type": "button",
            "text": "←",
            "position": [487 - button_spacing, button_y],
            "size": [button_size, button_size],
            "active": model.game_state == "challenge_active"
        })
        
        # Right button
        components.append({
            "type": "button",
            "text": "→",
            "position": [487 + button_spacing, button_y],
            "size": [button_size, button_size],
            "active": model.game_state == "challenge_active"
        })
        
        # Down button
        components.append({
            "type": "button",
            "text": "↓",
            "position": [487, button_y + button_size],
            "size": [button_size, button_size],
            "active": model.game_state == "challenge_active"
        })
        
        # Add submit/continue button
        button_text = "Submit"
        if model.game_state == "challenge_complete":
            button_text = "Continue"
        
        components.append({
            "type": "button",
            "text": button_text,
            "position": [462, 670],
            "size": [100, 50],
            "active": True
        })
        
        return components

# Define a simple renderer
def render_components(screen, components):
    """Render UI components to the screen."""
    for component in components:
        comp_type = component.get("type", "")
        
        if comp_type == "text":
            render_text(screen, component)
        elif comp_type == "rect":
            render_rect(screen, component)
        elif comp_type == "button":
            render_button(screen, component)
        elif comp_type == "focus":
            render_focus(screen, component)

def render_text(screen, component):
    """Render a text component."""
    text = component.get("text", "")
    position = component.get("position", [0, 0])
    font_size = component.get("font_size", 18)
    color = component.get("color", colors["text"])
    
    # Select font based on size
    if font_size >= 24:
        font = title_font
    elif font_size >= 16:
        font = regular_font
    else:
        font = small_font
    
    # Render text
    if text:
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=position)
        screen.blit(text_surface, text_rect)

def render_rect(screen, component):
    """Render a rectangle component."""
    position = component.get("position", [0, 0])
    size = component.get("size", [100, 100])
    color = component.get("color", colors["grid_bg"])
    border_color = component.get("border_color", colors["grid_border"])
    border_width = component.get("border_width", 1)
    
    # Draw rectangle
    rect = pygame.Rect(position[0], position[1], size[0], size[1])
    pygame.draw.rect(screen, color, rect)
    
    # Draw border if needed
    if border_width > 0:
        pygame.draw.rect(screen, border_color, rect, border_width)

def render_focus(screen, component):
    """Render a focus highlight."""
    position = component.get("position", [0, 0])
    size = component.get("size", [100, 100])
    color = component.get("color", (0, 200, 100, 128))
    border_color = component.get("border_color", (0, 200, 100))
    border_width = component.get("border_width", 3)
    
    # Create a surface with per-pixel alpha
    focus_surface = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(focus_surface, color, (0, 0, size[0], size[1]))
    
    # Draw surface
    rect = pygame.Rect(position[0], position[1], size[0], size[1])
    screen.blit(focus_surface, rect)
    
    # Draw border
    pygame.draw.rect(screen, border_color, rect, border_width)

def render_button(screen, component):
    """Render a button component."""
    position = component.get("position", [0, 0])
    size = component.get("size", [100, 40])
    text = component.get("text", "")
    active = component.get("active", True)
    
    # Choose color based on state
    if active:
        color = colors["button"]
        text_color = colors["text"]
    else:
        color = (180, 180, 180)  # Disabled color
        text_color = (120, 120, 120)  # Disabled text color
    
    # Draw button
    rect = pygame.Rect(position[0], position[1], size[0], size[1])
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, colors["grid_border"], rect, 2)
    
    # Draw text
    if text:
        text_surface = regular_font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=(
            position[0] + size[0] // 2,
            position[1] + size[1] // 2
        ))
        screen.blit(text_surface, text_rect)

# Create model and view
model = ExpandVisionModel(difficulty=3)
view = SimpleExpandVisionView(screen, {
    "title": title_font,
    "regular": regular_font,
    "small": small_font
})

# Game loop
clock = pygame.time.Clock()
running = True
last_time = time.time()
show_debug = True

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
            elif event.key == pygame.K_d:
                show_debug = not show_debug
            # Navigation with arrow keys
            elif event.key == pygame.K_UP:
                model.move_focus("up")
            elif event.key == pygame.K_DOWN:
                model.move_focus("down")
            elif event.key == pygame.K_LEFT:
                model.move_focus("left")
            elif event.key == pygame.K_RIGHT:
                model.move_focus("right")
            # Submit with Enter/Space
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if model.game_state == "challenge_active" and model.selected_position is not None:
                    model.check_answer()
                elif model.game_state == "challenge_complete":
                    model.create_new_challenge()
                    model.game_state = "challenge_active"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            model.handle_click(x, y)
    
    # Update model
    model.update(dt)
    
    # Build components from model state
    components = view.build_components(model)
    
    # Render components
    screen.fill(colors["background"])
    render_components(screen, components)
    
    # Draw debug info if needed
    if show_debug:
        # Draw FPS
        fps_text = f"FPS: {int(clock.get_fps())}"
        fps_surface = small_font.render(fps_text, True, (0, 0, 0))
        screen.blit(fps_surface, (5, 5))
        
        # Draw mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pos_text = f"Mouse: ({mouse_x}, {mouse_y})"
        pos_surface = small_font.render(pos_text, True, (0, 0, 0))
        screen.blit(pos_surface, (5, 25))
        
        # Draw focus position
        focus_text = f"Focus: {model.focus_position}"
        focus_surface = small_font.render(focus_text, True, (0, 0, 0))
        screen.blit(focus_surface, (5, 45))
        
        # Draw target position
        target_text = f"Target: {model.target_position}"
        target_surface = small_font.render(target_text, True, (0, 0, 0))
        screen.blit(target_surface, (5, 65))
        
        # Draw selected position
        selected_text = f"Selected: {model.selected_position}"
        selected_surface = small_font.render(selected_text, True, (0, 0, 0))
        screen.blit(selected_surface, (5, 85))
    
    # Update display
    pygame.display.flip()
    
    # Cap at 60 FPS
    clock.tick(60)

# Clean up
pygame.quit()
sys.exit(0) 