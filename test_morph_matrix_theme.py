#!/usr/bin/env python3
"""
Test script for the theme-aware Morph Matrix module.

This script demonstrates the theme-aware Morph Matrix cognitive training module
with theme toggling and theme-based styling, using a standalone implementation
that doesn't depend on the full package structure.
"""

import pygame
import sys
import time
import logging
import random
from pathlib import Path

# Add the project root to Python path if needed
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Simple Theme implementation for testing
class SimpleTheme:
    """Simple theme implementation for testing."""
    
    def __init__(self, name, id):
        """Initialize a simple theme.
        
        Args:
            name: Theme name
            id: Theme ID
        """
        self.name = name
        self.id = id
        self.colors = {}
        self._styles = {}
    
    def get_color(self, key):
        """Get a color from the theme.
        
        Args:
            key: Color key
            
        Returns:
            RGB color tuple
        """
        return self.colors.get(key, (255, 255, 255))
    
    def get_font_size(self, key):
        """Get a font size from the theme.
        
        Args:
            key: Font size key
            
        Returns:
            Font size value
        """
        return self.font_sizes.get(key, 16)
    
    def get_spacing(self, key):
        """Get a spacing value from the theme.
        
        Args:
            key: Spacing key
            
        Returns:
            Spacing value
        """
        return self.spacings.get(key, 8)
    
    def get_border_radius(self, key):
        """Get a border radius value from the theme.
        
        Args:
            key: Border radius key
            
        Returns:
            Border radius value
        """
        return self.border_radius.get(key, 0)
    
    def get_style(self, key):
        """Get a style from the registered styles.
        
        Args:
            key: Style key
            
        Returns:
            Style dictionary
        """
        if key in self._styles:
            return self._styles[key]
        
        # Default style based on component type
        return self._generate_default_style(key)
    
    def _generate_default_style(self, key):
        """Generate a default style based on the component type.
        
        Args:
            key: Style key (e.g., "morph_matrix.container")
            
        Returns:
            Style dictionary
        """
        parts = key.split(".")
        component = parts[0] if len(parts) > 0 else ""
        subtype = parts[1] if len(parts) > 1 else ""
        state = parts[2] if len(parts) > 2 else ""
        
        style = {}
        
        # Basic styling based on component type
        if component == "morph_matrix":
            if subtype == "container":
                style = {
                    "backgroundColor": self.get_color("card"),
                    "borderWidth": 2,
                    "borderColor": self.get_color("border"),
                    "borderRadius": self.get_border_radius("large")
                }
            elif subtype == "title":
                style = {
                    "color": self.get_color("text"),
                    "fontSize": 32
                }
            elif subtype == "instruction":
                style = {
                    "color": self.get_color("text_secondary"),
                    "fontSize": 20
                }
            elif subtype == "matrix":
                style = {
                    "backgroundColor": self.get_color("surface"),
                    "borderWidth": 2,
                    "borderColor": self.get_color("primary"),
                    "borderRadius": self.get_border_radius("medium")
                }
            elif subtype == "cell":
                if state == "filled":
                    style = {
                        "backgroundColor": self.get_color("primary"),
                        "borderWidth": 1,
                        "borderColor": self.get_color("primary_hover"),
                        "borderRadius": self.get_border_radius("small")
                    }
                else:  # empty
                    style = {
                        "backgroundColor": self.get_color("surface"),
                        "borderWidth": 1,
                        "borderColor": self.get_color("border"),
                        "borderRadius": self.get_border_radius("small")
                    }
            elif subtype == "option":
                if state == "correct":
                    style = {
                        "backgroundColor": self.get_color("surface"),
                        "borderWidth": 2,
                        "borderColor": self.get_color("success"),
                        "borderRadius": self.get_border_radius("small")
                    }
                elif state == "incorrect":
                    style = {
                        "backgroundColor": self.get_color("surface"),
                        "borderWidth": 2,
                        "borderColor": self.get_color("error"),
                        "borderRadius": self.get_border_radius("small")
                    }
                elif state == "selected":
                    style = {
                        "backgroundColor": self.get_color("surface"),
                        "borderWidth": 2,
                        "borderColor": self.get_color("primary"),
                        "borderRadius": self.get_border_radius("small")
                    }
                elif state == "missed":
                    style = {
                        "backgroundColor": self.get_color("surface"),
                        "borderWidth": 2,
                        "borderColor": self.get_color("warning"),
                        "borderRadius": self.get_border_radius("small")
                    }
                else:
                    style = {
                        "backgroundColor": self.get_color("surface"),
                        "borderWidth": 2,
                        "borderColor": self.get_color("border"),
                        "borderRadius": self.get_border_radius("small")
                    }
            elif subtype == "option_label":
                style = {
                    "color": self.get_color("text"),
                    "fontSize": 16
                }
            elif subtype == "score":
                style = {
                    "color": self.get_color("text_secondary"),
                    "fontSize": 18
                }
            elif subtype == "feedback":
                if state == "correct":
                    style = {
                        "color": self.get_color("success"),
                        "fontSize": 28,
                        "fontWeight": "bold"
                    }
                elif state == "incorrect":
                    style = {
                        "color": self.get_color("error"),
                        "fontSize": 28,
                        "fontWeight": "bold"
                    }
                elif state == "partial":
                    style = {
                        "color": self.get_color("warning"),
                        "fontSize": 28,
                        "fontWeight": "bold"
                    }
        
        # Store for future use
        self._styles[key] = style
        return style
    
    def register_style(self, key, style):
        """Register a new style.
        
        Args:
            key: Style key
            style: Style dictionary
        """
        self._styles[key] = style


# Simple ThemeProvider implementation for testing
class SimpleThemeProvider:
    """Simple theme provider implementation for testing."""
    
    def __init__(self, theme):
        """Initialize a simple theme provider.
        
        Args:
            theme: Theme instance
        """
        self.theme = theme


# Import our theme-aware module
from MetaMindIQTrain.modules.theme_aware_morph_matrix import ThemeAwareMorphMatrix


class MorphMatrixTest:
    """Test harness for the theme-aware Morph Matrix module."""
    
    def __init__(self):
        """Initialize the module test."""
        # Initialize pygame
        self.init_pygame()
        
        # Initialize themes
        self.init_themes()
        
        # Time tracking
        self.prev_time = time.time()
        self.current_time = time.time()
        
        # Initialize the module with theme provider
        self.morph_matrix = ThemeAwareMorphMatrix(
            difficulty=1,
            theme_provider=self.theme_provider,
            resolution=(self.width, self.height)
        )
        
        # Scheduled events
        self.scheduled_events = []
    
    def init_pygame(self):
        """Initialize pygame and create the display."""
        pygame.init()
        
        # Set up the display
        info = pygame.display.Info()
        self.width = info.current_w
        self.height = info.current_h
        
        # Create the window
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("MetaMindIQTrain - Theme-Aware Morph Matrix")
        
        # Create font cache
        self.fonts = {}
    
    def get_font(self, size):
        """Get a font of the specified size."""
        if size not in self.fonts:
            self.fonts[size] = pygame.font.SysFont("Arial", size)
        return self.fonts[size]
    
    def init_themes(self):
        """Initialize themes for testing."""
        # Create dark theme
        self.dark_theme = SimpleTheme(name="Dark Theme", id="dark")
        
        # Color palette
        self.dark_theme.colors = {
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
        }

        # Fonts, spacing and other properties
        self.dark_theme.font_sizes = {
            "small": 14,
            "medium": 18,
            "large": 24,
            "xlarge": 32,
        }
        
        self.dark_theme.spacings = {
            "small": 8,
            "medium": 16,
            "large": 24,
            "xlarge": 32,
        }
        
        self.dark_theme.border_radius = {
            "small": 4,
            "medium": 8,
            "large": 12,
        }
        
        # Create light theme
        self.light_theme = SimpleTheme(name="Light Theme", id="light")
        
        # Color palette
        self.light_theme.colors = {
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
        }
        
        # Fonts, spacing and other properties
        self.light_theme.font_sizes = {
            "small": 14,
            "medium": 18,
            "large": 24,
            "xlarge": 32,
        }
        
        self.light_theme.spacings = {
            "small": 8,
            "medium": 16,
            "large": 24,
            "xlarge": 32,
        }
        
        self.light_theme.border_radius = {
            "small": 4,
            "medium": 8,
            "large": 12,
        }
        
        # Create high contrast theme
        self.high_contrast_theme = SimpleTheme(name="High Contrast Theme", id="high_contrast")
        
        # Color palette
        self.high_contrast_theme.colors = {
            "background": (0, 0, 0),             # Black background
            "card": (20, 20, 20),                # Dark card background
            "surface": (40, 40, 40),             # Dark surface
            "border": (255, 255, 0),             # Yellow border
            
            "text": (255, 255, 255),             # White text
            "text_secondary": (220, 220, 220),   # Light gray text
            "text_disabled": (160, 160, 160),    # Medium gray text
            
            "primary": (0, 160, 255),            # Bright blue
            "primary_hover": (80, 200, 255),     # Lighter blue
            "primary_active": (0, 120, 215),     # Darker blue
            "secondary": (200, 200, 200),        # Light gray
            "accent": (255, 160, 0),             # Orange
            
            "success": (0, 255, 0),              # Pure green
            "error": (255, 0, 0),                # Pure red
            "warning": (255, 255, 0),            # Pure yellow
            "info": (0, 200, 255),               # Bright blue
        }
        
        # Fonts, spacing and other properties with larger sizes for accessibility
        self.high_contrast_theme.font_sizes = {
            "small": 16,                         # Larger minimum size
            "medium": 20,
            "large": 28,
            "xlarge": 36,
        }
        
        self.high_contrast_theme.spacings = {
            "small": 10,                         # Larger minimum spacing
            "medium": 18,
            "large": 28,
            "xlarge": 38,
        }
        
        self.high_contrast_theme.border_radius = {
            "small": 0,                          # No rounding for high contrast
            "medium": 0,
            "large": 0,
        }
        
        # Create theme provider with dark theme as default
        self.theme_provider = SimpleThemeProvider(self.dark_theme)
    
    def toggle_theme(self):
        """Toggle between themes."""
        if self.theme_provider.theme.id == "dark":
            self.theme_provider.theme = self.light_theme
            logger.info("Switched to light theme")
        elif self.theme_provider.theme.id == "light":
            self.theme_provider.theme = self.high_contrast_theme
            logger.info("Switched to high contrast theme")
        else:
            self.theme_provider.theme = self.dark_theme
            logger.info("Switched to dark theme")
        
        # Update module theme
        self.morph_matrix.set_theme(self.theme_provider)
    
    def schedule_event(self, callback, delay):
        """Schedule an event to be executed after a delay.
        
        Args:
            callback: Function to call
            delay: Delay in seconds
        """
        self.scheduled_events.append({
            "callback": callback,
            "time": time.time() + delay
        })
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                elif event.key == pygame.K_t:
                    # Toggle theme
                    self.toggle_theme()
                
                elif event.key == pygame.K_SPACE:
                    # Pass to module
                    self.morph_matrix.handle_key_press(" ")
                
                elif event.key == pygame.K_r:
                    # Restart module
                    self.morph_matrix._start_round()
                
                else:
                    # Pass other keys to module
                    if event.unicode:
                        self.morph_matrix.handle_key_press(event.unicode)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Pass click to module
                    self.morph_matrix.handle_click(event.pos)
        
        return True
    
    def update(self, delta_time):
        """Update game state."""
        # Update module
        self.morph_matrix.update(delta_time)
        
        # Check scheduled events
        current_time = time.time()
        current_events = self.scheduled_events.copy()
        self.scheduled_events = []
        
        for event in current_events:
            if current_time >= event["time"]:
                event["callback"]()
            else:
                self.scheduled_events.append(event)
    
    def render_components(self, components):
        """Render UI components to the screen."""
        for component in components:
            if component.type == "rectangle":
                # Get style properties
                bg_color = component.style.get("backgroundColor", (100, 100, 100))
                border_width = component.style.get("borderWidth", 0)
                border_color = component.style.get("borderColor", (0, 0, 0))
                border_radius = component.style.get("borderRadius", 0)
                
                rect = pygame.Rect(component.position[0], component.position[1], 
                                  component.width, component.height)
                
                # Draw with border radius if supported
                if border_radius > 0:
                    # Draw filled rectangle with rounded corners
                    pygame.draw.rect(self.screen, bg_color, rect, 0, border_radius)
                    if border_width > 0:
                        # Draw border
                        pygame.draw.rect(self.screen, border_color, rect, border_width, border_radius)
                else:
                    # Draw regular rectangle
                    pygame.draw.rect(self.screen, bg_color, rect)
                    if border_width > 0:
                        # Draw border
                        pygame.draw.rect(self.screen, border_color, rect, border_width)
            
            elif component.type == "text":
                # Get style properties
                color = component.style.get("color", (255, 255, 255))
                font_size = component.style.get("fontSize", 20)
                
                # Render text
                font = self.get_font(font_size)
                text_surface = font.render(component.text, True, color)
                
                # Adjust position based on alignment
                x, y = component.position
                if component.align == "center":
                    x -= text_surface.get_width() // 2
                elif component.align == "right":
                    x -= text_surface.get_width()
                
                # Draw text
                self.screen.blit(text_surface, (x, y))
            
            elif component.type == "circle":
                # Get style properties
                bg_color = component.style.get("backgroundColor", (100, 100, 100))
                border_width = component.style.get("borderWidth", 0)
                border_color = component.style.get("borderColor", (0, 0, 0))
                
                # Draw filled circle
                pygame.draw.circle(self.screen, bg_color, component.position, component.radius)
                
                # Draw border if needed
                if border_width > 0:
                    pygame.draw.circle(self.screen, border_color, component.position, component.radius, border_width)
    
    def render(self):
        """Render the current state to the screen."""
        # Clear screen with background color
        self.screen.fill(self.theme_provider.theme.colors["background"])
        
        # Render module UI
        if self.morph_matrix.ui:
            self.render_components(self.morph_matrix.ui.components)
        
        # Add theme info text at top
        theme_name = self.theme_provider.theme.name
        theme_text = f"Current Theme: {theme_name} (Press T to toggle themes)"
        
        font = self.get_font(20)
        text_surface = font.render(theme_text, True, self.theme_provider.theme.colors["text"])
        text_rect = text_surface.get_rect(center=(self.width // 2, 30))
        self.screen.blit(text_surface, text_rect)
        
        # Add controls text at bottom
        controls_text = "Controls: Space = Submit, R = Reset, ESC = Exit"
        controls_surface = font.render(controls_text, True, self.theme_provider.theme.colors["text_secondary"])
        controls_rect = controls_surface.get_rect(center=(self.width // 2, self.height - 30))
        self.screen.blit(controls_surface, controls_rect)
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        running = True
        clock = pygame.time.Clock()
        
        while running:
            # Calculate delta time
            self.current_time = time.time()
            delta_time = self.current_time - self.prev_time
            self.prev_time = self.current_time
            
            # Handle events
            running = self.handle_events()
            
            # Update
            self.update(delta_time)
            
            # Render
            self.render()
            
            # Cap at 60 FPS
            clock.tick(60)
        
        # Clean up
        pygame.quit()


if __name__ == "__main__":
    try:
        test = MorphMatrixTest()
        test.run()
    except Exception as e:
        logger.exception("An error occurred:")
        pygame.quit()
        sys.exit(1) 