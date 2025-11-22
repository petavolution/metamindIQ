#!/usr/bin/env python3
"""
Basic SymbolMemory MVC Test

This script provides a minimal pygame environment to test the SymbolMemory MVC module
by loading it directly and rendering its state with a simple renderer.
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
pygame.display.set_caption("Basic SymbolMemory Test")

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
    "button": (200, 200, 200),
    "button_hover": (180, 180, 180),
    "symbol": (50, 50, 200)
}

# Define SymbolMemoryModel (simplified version)
class SymbolMemoryModel:
    """Model component for SymbolMemory test."""
    
    SYMBOLS = ["■", "●", "▲", "◆", "★", "♦", "♥", "♣", "♠", "⬡", "⬢", "⌘"]
    
    PHASE_MEMORIZE = "memorize"
    PHASE_HIDDEN = "hidden"
    PHASE_COMPARE = "compare"
    PHASE_ANSWER = "answer"
    PHASE_FEEDBACK = "feedback"
    
    STATE_ACTIVE = "active"
    STATE_COMPLETED = "completed"
    
    def __init__(self, difficulty=3):
        self.difficulty = max(1, min(10, difficulty))
        self.level = self.difficulty
        self.score = 0
        self.current_grid_size = self._calculate_grid_size()
        
        self.phase = self.PHASE_MEMORIZE
        self.game_state = self.STATE_ACTIVE
        self.original_pattern = None
        self.modified_pattern = None
        self.was_modified = False
        self.user_answer = None
        self.timer_active = True
        self.round_score = 0
        self.total_rounds = 0
        self.correct_rounds = 0
        self.message = "Memorize the pattern"
        
        self.phase_start_time = time.time()
        self.memorize_duration = self._calculate_memorize_duration()
        self.hidden_duration = 1.0
        
        self._generate_pattern()
    
    def _calculate_grid_size(self):
        """Calculate grid size based on difficulty."""
        return max(3, min(6, 3 + (self.difficulty - 1) // 3))
    
    def _calculate_memorize_duration(self):
        """Calculate memorize phase duration based on difficulty."""
        return max(2.0, 6.0 - (self.difficulty - 1) * 0.4)
    
    def _generate_pattern(self):
        """Generate a new pattern for the current difficulty."""
        grid_size = self.current_grid_size
        
        # Number of symbols to place
        max_symbols = grid_size * grid_size
        num_symbols = min(max_symbols, max(3, int(max_symbols * (0.3 + 0.05 * self.difficulty))))
        
        # Create empty grid
        empty_grid = [["" for _ in range(grid_size)] for _ in range(grid_size)]
        
        # Place symbols randomly
        symbols = []
        positions = []
        
        for _ in range(num_symbols):
            symbol = random.choice(self.SYMBOLS)
            
            while True:
                row = random.randint(0, grid_size - 1)
                col = random.randint(0, grid_size - 1)
                
                if empty_grid[row][col] == "":
                    empty_grid[row][col] = symbol
                    symbols.append(symbol)
                    positions.append((row, col))
                    break
        
        self.original_pattern = {
            "grid": empty_grid,
            "symbols": symbols,
            "positions": positions,
            "size": grid_size
        }
        
        # Create modified pattern
        self.modified_pattern = self._create_modified_pattern(self.original_pattern)
        self.was_modified = (self.original_pattern["grid"] != self.modified_pattern["grid"])
    
    def _create_modified_pattern(self, original_pattern):
        """Create a possibly modified version of the pattern."""
        grid_size = original_pattern["size"]
        original_grid = original_pattern["grid"]
        
        # Deep copy the original grid
        new_grid = [row[:] for row in original_grid]
        
        # Decide if we should modify (50% chance)
        if random.random() < 0.5:
            # No modification - return a copy of the original
            return {
                "grid": new_grid,
                "symbols": original_pattern["symbols"][:],
                "positions": original_pattern["positions"][:],
                "size": grid_size
            }
        
        # Randomly choose modification type
        mod_type = random.choice(["change", "add", "remove"])
        
        if mod_type == "change" and original_pattern["positions"]:
            # Change a random symbol
            pos_idx = random.randint(0, len(original_pattern["positions"]) - 1)
            row, col = original_pattern["positions"][pos_idx]
            
            # Get a different symbol
            current_symbol = original_grid[row][col]
            new_symbol = current_symbol
            while new_symbol == current_symbol:
                new_symbol = random.choice(self.SYMBOLS)
            
            # Update the grid
            new_grid[row][col] = new_symbol
        
        elif mod_type == "add":
            # Add a new symbol
            max_attempts = 10
            for _ in range(max_attempts):
                row = random.randint(0, grid_size - 1)
                col = random.randint(0, grid_size - 1)
                
                if original_grid[row][col] == "":
                    new_grid[row][col] = random.choice(self.SYMBOLS)
                    break
        
        elif mod_type == "remove" and original_pattern["positions"]:
            # Remove a random symbol
            pos_idx = random.randint(0, len(original_pattern["positions"]) - 1)
            row, col = original_pattern["positions"][pos_idx]
            new_grid[row][col] = ""
        
        # Recalculate symbols and positions
        new_symbols = []
        new_positions = []
        for row in range(grid_size):
            for col in range(grid_size):
                if new_grid[row][col] != "":
                    new_symbols.append(new_grid[row][col])
                    new_positions.append((row, col))
        
        return {
            "grid": new_grid,
            "symbols": new_symbols,
            "positions": new_positions,
            "size": grid_size
        }
    
    def update(self, dt):
        """Update model state based on elapsed time."""
        if self.game_state == self.STATE_COMPLETED:
            return
        
        if self.phase == self.PHASE_MEMORIZE and self.timer_active:
            elapsed = time.time() - self.phase_start_time
            if elapsed >= self.memorize_duration:
                self.phase = self.PHASE_HIDDEN
                self.phase_start_time = time.time()
                self.message = "Remember the pattern..."
        
        elif self.phase == self.PHASE_HIDDEN and self.timer_active:
            elapsed = time.time() - self.phase_start_time
            if elapsed >= self.hidden_duration:
                self.phase = self.PHASE_COMPARE
                self.phase_start_time = time.time()
                self.message = "Did the pattern change?"
    
    def handle_click(self, x, y):
        """Handle user click at position (x, y)."""
        # Skip if game not active
        if self.game_state != self.STATE_ACTIVE:
            return
        
        # Update based on current phase
        if self.phase == self.PHASE_COMPARE:
            # Check if user clicked Yes button
            if 300 <= x <= 400 and 550 <= y <= 600:
                self.process_input({"action": "answer_yes"})
            
            # Check if user clicked No button
            elif 624 <= x <= 724 and 550 <= y <= 600:
                self.process_input({"action": "answer_no"})
        
        elif self.phase == self.PHASE_FEEDBACK:
            # Check if user clicked Continue button
            if 462 <= x <= 562 and 550 <= y <= 600:
                self.process_input({"action": "continue"})
    
    def process_input(self, input_data):
        """Process user input."""
        action = input_data.get("action", "")
        
        if action == "answer_yes":
            self.user_answer = True
            self._check_answer()
        
        elif action == "answer_no":
            self.user_answer = False
            self._check_answer()
        
        elif action == "continue":
            self._start_new_round()
    
    def _check_answer(self):
        """Check if user's answer is correct."""
        is_correct = (self.user_answer == self.was_modified)
        
        if is_correct:
            self.score += 10 * self.difficulty
            self.round_score = 10 * self.difficulty
            self.correct_rounds += 1
            self.message = "Correct! The pattern " + ("was modified" if self.was_modified else "was not modified")
        else:
            self.round_score = 0
            self.message = "Incorrect! The pattern " + ("was modified" if self.was_modified else "was not modified")
        
        self.total_rounds += 1
        self.phase = self.PHASE_FEEDBACK
        self.phase_start_time = time.time()
    
    def _start_new_round(self):
        """Start a new round."""
        # Update difficulty every 3 rounds if correct ratio is good
        if self.total_rounds % 3 == 0 and self.total_rounds > 0:
            correct_ratio = self.correct_rounds / self.total_rounds
            if correct_ratio >= 0.8 and self.difficulty < 10:
                self.difficulty += 1
                self.level = self.difficulty
                self.current_grid_size = self._calculate_grid_size()
                self.memorize_duration = self._calculate_memorize_duration()
        
        # Reset for new round
        self.phase = self.PHASE_MEMORIZE
        self.phase_start_time = time.time()
        self.user_answer = None
        self.message = "Memorize the pattern"
        
        # Generate new pattern
        self._generate_pattern()

# Define a simple view component
class SimpleSymbolMemoryView:
    """View component for SymbolMemory test."""
    
    def __init__(self, screen, fonts):
        self.screen = screen
        self.fonts = fonts
    
    def build_components(self, model):
        """Build UI components from model state."""
        components = []
        
        # Add title
        components.append({
            "type": "text",
            "text": "Symbol Memory Training",
            "position": [412, 50],
            "font_size": 24,
            "color": (0, 0, 0)
        })
        
        # Add score
        components.append({
            "type": "text",
            "text": f"Score: {model.score}",
            "position": [50, 50],
            "font_size": 18,
            "color": (0, 0, 0)
        })
        
        # Add level
        components.append({
            "type": "text",
            "text": f"Level: {model.level}",
            "position": [50, 80],
            "font_size": 18,
            "color": (0, 0, 0)
        })
        
        # Add message
        components.append({
            "type": "text",
            "text": model.message,
            "position": [512, 120],
            "font_size": 20,
            "color": (0, 0, 100)
        })
        
        # Add grid
        grid_size = 300
        grid_x = (width - grid_size) // 2
        grid_y = (height - grid_size) // 2
        
        components.append({
            "type": "rect",
            "position": [grid_x, grid_y],
            "size": [grid_size, grid_size],
            "color": colors["grid_bg"],
            "border_color": colors["grid_border"],
            "border_width": 2
        })
        
        # Add grid cells
        cell_size = grid_size // model.current_grid_size
        
        # Determine which pattern to display
        if model.phase in [model.PHASE_MEMORIZE, model.PHASE_FEEDBACK]:
            pattern = model.original_pattern
        elif model.phase == model.PHASE_COMPARE:
            pattern = model.modified_pattern
        else:
            pattern = None
        
        if pattern:
            grid_data = pattern["grid"]
            
            for row in range(model.current_grid_size):
                for col in range(model.current_grid_size):
                    # Add grid lines
                    components.append({
                        "type": "rect",
                        "position": [grid_x + col * cell_size, grid_y + row * cell_size],
                        "size": [cell_size, cell_size],
                        "color": colors["grid_bg"],
                        "border_color": colors["grid_border"],
                        "border_width": 1
                    })
                    
                    # Add symbol if cell is not empty
                    if grid_data[row][col]:
                        # Calculate center position
                        cell_center_x = grid_x + col * cell_size + cell_size // 2
                        cell_center_y = grid_y + row * cell_size + cell_size // 2
                        
                        components.append({
                            "type": "text",
                            "text": grid_data[row][col],
                            "position": [cell_center_x - 10, cell_center_y - 10],  # Adjust for centering
                            "font_size": 24,
                            "color": colors["symbol"]
                        })
        
        # Add buttons based on phase
        if model.phase == model.PHASE_COMPARE:
            # Yes button
            components.append({
                "type": "button",
                "text": "Yes",
                "position": [300, 550],
                "size": [100, 50],
                "active": True
            })
            
            # No button
            components.append({
                "type": "button",
                "text": "No",
                "position": [624, 550],
                "size": [100, 50],
                "active": True
            })
        
        elif model.phase == model.PHASE_FEEDBACK:
            # Add feedback text
            result_text = "Correct!" if model.round_score > 0 else "Incorrect!"
            components.append({
                "type": "text",
                "text": result_text,
                "position": [512, 500],
                "font_size": 24,
                "color": (0, 150, 0) if model.round_score > 0 else (150, 0, 0)
            })
            
            # Add continue button
            components.append({
                "type": "button",
                "text": "Continue",
                "position": [462, 550],
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
model = SymbolMemoryModel(difficulty=3)
view = SimpleSymbolMemoryView(screen, {
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
        
        # Draw phase info
        phase_text = f"Phase: {model.phase}"
        phase_surface = small_font.render(phase_text, True, (0, 0, 0))
        screen.blit(phase_surface, (5, 45))
    
    # Update display
    pygame.display.flip()
    
    # Cap at 60 FPS
    clock.tick(60)

# Clean up
pygame.quit()
sys.exit(0) 