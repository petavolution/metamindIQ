#!/usr/bin/env python3
"""
Basic MorphMatrix Test

This script provides a minimal pygame environment to test the MorphMatrix concept
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
pygame.display.set_caption("Basic MorphMatrix Test")

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
    "selected": (100, 180, 255),
    "modified": (255, 100, 100),
    "cell_on": (50, 50, 200),
    "cell_off": (230, 230, 230)
}

# Define MorphMatrixModel (simplified version)
class MorphMatrixModel:
    """Model component for MorphMatrix test."""
    
    def __init__(self, difficulty=3):
        """Initialize the model with game state and business logic."""
        # Game settings
        self.difficulty = max(1, min(10, difficulty))
        self.level = self.difficulty
        self.matrix_size = self._calculate_matrix_size()
        self.score = 0
        
        # Game state
        self.game_state = "challenge_active"  # challenge_active, challenge_complete, feedback
        self.clusters = []  # Matrix pattern clusters
        self.original_matrix = None  # Original pattern matrix
        self.selected_clusters = []  # User selections
        self.answered = False  # Whether the user has submitted an answer
        self.correct_answer = None  # Whether the last answer was correct
        self.modified_indices = []  # Indices of modified patterns
        self.selected_patterns = []  # Indices of user-selected patterns
        self.total_patterns = 0  # Total number of patterns in the challenge
        
        # Performance tracking
        self.round_start_time = time.time()
        self.challenge_time = 0
        
        # Create first challenge
        self.create_new_challenge()
    
    def _calculate_matrix_size(self):
        """Calculate matrix size based on difficulty."""
        return max(3, min(7, 3 + (self.difficulty - 1) // 2))
    
    def create_new_challenge(self):
        """Create a new pattern recognition challenge."""
        # Adjust matrix size based on level
        self.matrix_size = self._calculate_matrix_size()
        
        # Reset state
        self.original_matrix = self.generate_random_matrix(self.matrix_size)
        self.selected_patterns = []
        self.answered = False
        self.correct_answer = None
        self.round_start_time = time.time()
        
        # Create pattern variations
        num_patterns = 6  # Default 6 patterns (3x2 grid)
        num_modified = random.randint(1, 4)  # 1-4 modified patterns
        
        self.create_pattern_variations(num_patterns, num_modified)
    
    def generate_random_matrix(self, size):
        """Generate a random binary matrix of given size."""
        # Create empty matrix
        matrix = [[0 for _ in range(size)] for _ in range(size)]
        
        # Fill with random 1s and 0s, but ensure there are at least some 1s
        num_cells = size * size
        num_ones = random.randint(max(3, num_cells // 5), max(5, num_cells // 3))
        
        for _ in range(num_ones):
            row = random.randint(0, size - 1)
            col = random.randint(0, size - 1)
            matrix[row][col] = 1
        
        return matrix
    
    def create_pattern_variations(self, num_patterns, num_modified):
        """Create pattern variations from the original matrix."""
        self.clusters = []
        self.modified_indices = []
        
        # Create all patterns as rotations initially
        for i in range(num_patterns):
            rotation = random.choice([0, 90, 180, 270])
            position = None  # Will be set by the View
            
            cluster = self.create_cluster(self.original_matrix, rotation, i, position)
            self.clusters.append(cluster)
        
        # Select random patterns to modify
        indices_to_modify = random.sample(range(num_patterns), num_modified)
        self.modified_indices = indices_to_modify
        
        # Modify the selected patterns
        for idx in indices_to_modify:
            self.mutate_pattern(self.clusters[idx])
        
        self.total_patterns = num_patterns
    
    def create_cluster(self, source_matrix, rotation, index, position=None):
        """Create a pattern cluster with metadata."""
        rotated = self.rotate_matrix(source_matrix, rotation)
        
        return {
            "matrix": rotated,
            "rotation": rotation,
            "source": source_matrix,
            "position": position,
            "index": index,
            "modified": False,
            "selected": False
        }
    
    def rotate_matrix(self, matrix, angle):
        """Rotate a matrix by the given angle (0, 90, 180, 270)."""
        size = len(matrix)
        rotated = [[0 for _ in range(size)] for _ in range(size)]
        
        if angle == 0:
            # No rotation
            return [row[:] for row in matrix]
        
        elif angle == 90:
            # Rotate 90 degrees clockwise
            for row in range(size):
                for col in range(size):
                    rotated[col][size - 1 - row] = matrix[row][col]
        
        elif angle == 180:
            # Rotate 180 degrees
            for row in range(size):
                for col in range(size):
                    rotated[size - 1 - row][size - 1 - col] = matrix[row][col]
        
        elif angle == 270:
            # Rotate 270 degrees clockwise (90 counterclockwise)
            for row in range(size):
                for col in range(size):
                    rotated[size - 1 - col][row] = matrix[row][col]
        
        return rotated
    
    def mutate_pattern(self, cluster):
        """Modify a pattern by changing random pixels."""
        # Mark as modified
        cluster["modified"] = True
        
        # Deep copy the matrix
        matrix = [row[:] for row in cluster["matrix"]]
        
        # Modify 1-3 bits depending on matrix size
        size = len(matrix)
        num_changes = random.randint(1, min(3, size - 1))
        
        for _ in range(num_changes):
            row = random.randint(0, size - 1)
            col = random.randint(0, size - 1)
            
            # Flip the bit
            matrix[row][col] = 1 - matrix[row][col]
        
        # Update the matrix
        cluster["matrix"] = matrix
    
    def handle_click(self, x, y, screen_width=1024, screen_height=768):
        """Handle user click at position (x, y)."""
        # Skip if challenge is complete
        if self.game_state != "challenge_active":
            # Check if clicked continue button
            button_x = (screen_width - 100) // 2
            button_y = 670
            if self.game_state == "challenge_complete" and button_x <= x <= button_x + 100 and button_y <= y <= button_y + 50:
                self.create_new_challenge()
                self.game_state = "challenge_active"
                return
            
            return
        
        # Check if clicked on a pattern
        patterns_grid = self.calculate_pattern_positions(screen_width, screen_height)
        
        for i, pattern_pos in enumerate(patterns_grid):
            px, py, pwidth, pheight = pattern_pos
            
            if px <= x <= px + pwidth and py <= y <= py + pheight:
                # Toggle selection
                if i in self.selected_patterns:
                    self.selected_patterns.remove(i)
                    self.clusters[i]["selected"] = False
                else:
                    self.selected_patterns.append(i)
                    self.clusters[i]["selected"] = True
                break
        
        # Check if clicked submit button
        button_x = (screen_width - 100) // 2
        button_y = 670
        if button_x <= x <= button_x + 100 and button_y <= y <= button_y + 50:
            self.check_answer()
    
    def calculate_pattern_positions(self, screen_width=1024, screen_height=768):
        """Calculate positions for all patterns in a grid layout."""
        # Create a 3x2 grid layout
        pattern_width = 150
        pattern_height = 150
        padding = 30
        
        grid_width = 3  # 3 columns
        grid_height = 2  # 2 rows
        
        # Calculate total grid dimensions
        total_width = grid_width * pattern_width + (grid_width - 1) * padding
        total_height = grid_height * pattern_height + (grid_height - 1) * padding
        
        # Calculate top-left position of grid
        start_x = (screen_width - total_width) // 2
        start_y = 200
        
        # Calculate positions for each pattern
        positions = []
        
        for i in range(self.total_patterns):
            # Calculate grid position
            grid_x = i % grid_width
            grid_y = i // grid_width
            
            # Calculate actual position
            x = start_x + grid_x * (pattern_width + padding)
            y = start_y + grid_y * (pattern_height + padding)
            
            # Store position in pattern
            if i < len(self.clusters):
                self.clusters[i]["position"] = [x, y]
            
            positions.append((x, y, pattern_width, pattern_height))
        
        return positions
    
    def check_answer(self):
        """Check if user's answer is correct."""
        # Compare selected patterns with modified indices
        selected_set = set(self.selected_patterns)
        modified_set = set(self.modified_indices)
        
        # Check if selections match
        self.correct_answer = (selected_set == modified_set)
        
        # Update score
        if self.correct_answer:
            base_points = 10 * self.difficulty
            time_bonus = max(0, 30 - int(time.time() - self.round_start_time)) * 2
            self.score += base_points + time_bonus
        
        # Mark challenge as complete
        self.game_state = "challenge_complete"
        self.answered = True
        
        # Highlight correct answers
        for i in range(len(self.clusters)):
            # Reset selection
            self.clusters[i]["selected"] = False
            
            # Highlight correct answers
            if i in self.modified_indices:
                self.clusters[i]["selected"] = True
    
    def update(self, dt):
        """Update model state based on elapsed time."""
        # Update challenge time
        if self.game_state == "challenge_active":
            self.challenge_time = time.time() - self.round_start_time

# Define a simple view component
class SimpleMorphMatrixView:
    """View component for MorphMatrix test."""
    
    def __init__(self, screen, fonts, width=1024, height=768):
        self.screen = screen
        self.fonts = fonts
        self.width = width
        self.height = height
    
    def build_components(self, model):
        """Build UI components from model state."""
        components = []
        
        # Add title
        components.append({
            "type": "text",
            "text": "MorphMatrix Training",
            "position": [self.width // 2, 50],
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
        
        # Add instruction text
        if model.game_state == "challenge_active":
            instruction_text = "Select all matrices that have been modified from the original pattern."
        elif model.game_state == "challenge_complete":
            if model.correct_answer:
                instruction_text = "Correct! These are the modified patterns."
            else:
                instruction_text = "Incorrect! The highlighted patterns are the ones that were modified."
        else:
            instruction_text = ""
        
        components.append({
            "type": "text",
            "text": instruction_text,
            "position": [self.width // 2, 120],
            "font_size": 18,
            "color": (0, 0, 100)
        })
        
        # Add timer
        if model.game_state == "challenge_active":
            components.append({
                "type": "text",
                "text": f"Time: {int(model.challenge_time)}s",
                "position": [self.width - 80, 50],
                "font_size": 18,
                "color": (0, 0, 0)
            })
        
        # Add patterns
        pattern_positions = model.calculate_pattern_positions(self.width, self.height)
        
        for i, cluster in enumerate(model.clusters):
            if i >= len(pattern_positions):
                continue
                
            x, y, width, height = pattern_positions[i]
            
            # Add background
            bg_color = colors["grid_bg"]
            if cluster["selected"]:
                bg_color = colors["selected"]
                if model.game_state == "challenge_complete" and i in model.modified_indices:
                    bg_color = colors["modified"]
            
            components.append({
                "type": "rect",
                "position": [x, y],
                "size": [width, height],
                "color": bg_color,
                "border_color": colors["grid_border"],
                "border_width": 2
            })
            
            # Add matrix
            matrix_data = cluster["matrix"]
            
            components.append({
                "type": "matrix",
                "position": [x, y],
                "size": [width, height],
                "matrix": matrix_data,
                "selected": cluster["selected"],
                "modified": cluster["modified"]
            })
            
            # Add pattern index
            components.append({
                "type": "text",
                "text": f"Pattern {i+1}",
                "position": [x + width // 2, y - 15],
                "font_size": 14,
                "color": (0, 0, 0)
            })
        
        # Add submit button for active challenge
        if model.game_state == "challenge_active":
            button_x = (self.width - 100) // 2
            button_y = 670
            
            components.append({
                "type": "button",
                "text": "Submit",
                "position": [button_x, button_y],
                "size": [100, 50],
                "active": True
            })
        
        # Add continue button for completed challenge
        if model.game_state == "challenge_complete":
            button_x = (self.width - 100) // 2
            button_y = 670
            
            components.append({
                "type": "button",
                "text": "Continue",
                "position": [button_x, button_y],
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
        elif comp_type == "matrix":
            render_matrix(screen, component)
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

def render_matrix(screen, component):
    """Render a binary matrix component."""
    position = component.get("position", [0, 0])
    size = component.get("size", [150, 150])
    matrix_data = component.get("matrix", [])
    
    # Get matrix dimensions
    if matrix_data and isinstance(matrix_data, list):
        matrix_size = len(matrix_data)
    else:
        matrix_size = 5  # Default size
    
    # Calculate cell size
    cell_width = size[0] // matrix_size
    cell_height = size[1] // matrix_size
    
    # Draw matrix cells
    for y in range(matrix_size):
        for x in range(matrix_size):
            # Get cell value (0 or 1)
            cell_value = 0
            if y < len(matrix_data) and x < len(matrix_data[y]):
                cell_value = matrix_data[y][x]
            
            # Calculate cell position
            cell_x = position[0] + x * cell_width
            cell_y = position[1] + y * cell_height
            
            # Draw cell
            cell_rect = pygame.Rect(cell_x, cell_y, cell_width, cell_height)
            cell_color = colors["cell_on"] if cell_value == 1 else colors["cell_off"]
            pygame.draw.rect(screen, cell_color, cell_rect)
            pygame.draw.rect(screen, colors["grid_border"], cell_rect, 1)

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
model = MorphMatrixModel(difficulty=3)
view = SimpleMorphMatrixView(screen, {
    "title": title_font,
    "regular": regular_font,
    "small": small_font
}, width, height)

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
            model.handle_click(x, y, width, height)
    
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
        
        # Draw selected patterns
        selected_text = f"Selected: {model.selected_patterns}"
        selected_surface = small_font.render(selected_text, True, (0, 0, 0))
        screen.blit(selected_surface, (5, 45))
        
        # Draw modified indices
        modified_text = f"Modified: {model.modified_indices}"
        modified_surface = small_font.render(modified_text, True, (0, 0, 0))
        screen.blit(modified_surface, (5, 65))
    
    # Update display
    pygame.display.flip()
    
    # Cap at 60 FPS
    clock.tick(60)

# Clean up
pygame.quit()
sys.exit(0) 