#!/usr/bin/env python3
"""
Test script for theme-aware cognitive training modules.

This script demonstrates the theme-aware versions of the cognitive training modules
with consistent styling and resolution independence.
"""

import os
import sys
import pygame
import time
import logging
from pathlib import Path

# Add the project root to the Python path if needed
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import theme system
from MetaMindIQTrain.core.theme import Theme, ThemeProvider, register_theme
from MetaMindIQTrain.core.components import UI, Component, ComponentFactory
from MetaMindIQTrain.core.scaling_helper import ScalingHelper

# Import cognitive modules (theme-aware versions)
from MetaMindIQTrain.modules.theme_aware_expand_vision import ThemeAwareExpandVision
# Assuming we have implemented ThemeAwareSymbolMemory too
try:
    from MetaMindIQTrain.modules.theme_aware_symbol_memory import ThemeAwareSymbolMemory
    has_symbol_memory = True
except ImportError:
    has_symbol_memory = False
    print("Symbol Memory module not found, continuing with Expand Vision only.")

# Import module theme styles
from MetaMindIQTrain.core.module_theme_styles import register_cognitive_module_styles

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModuleTest:
    """Test harness for theme-aware cognitive training modules."""
    
    # Module types
    MODULE_EXPAND_VISION = 0
    MODULE_SYMBOL_MEMORY = 1
    
    # Module selection states
    STATE_MODULE_SELECTION = 0
    STATE_MODULE_RUNNING = 1
    
    def __init__(self):
        """Initialize the module test."""
        self.init_pygame()
        self.init_themes()
        self.init_ui()
        
        # Current state and active module
        self.state = self.STATE_MODULE_SELECTION
        self.active_module = None
        self.active_module_type = -1
        
        # Time tracking
        self.prev_time = time.time()
        self.current_time = time.time()
        
        # Initialize scaling helper
        self.scaling_helper = ScalingHelper()
        self.scaling_helper.update_scale_factors(self.width, self.height, 1440, 1024)
    
    def init_pygame(self):
        """Initialize pygame and create the display."""
        pygame.init()
        
        # Set up the display (use native resolution, but default to 1440x1024)
        info = pygame.display.Info()
        self.width = info.current_w
        self.height = info.current_h
        
        # Create the window
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("MetaMindIQTrain - Theme-Aware Cognitive Modules")
        
        # Create font cache
        self.fonts = {}
    
    def get_font(self, size):
        """Get a font of the specified size."""
        if size not in self.fonts:
            self.fonts[size] = pygame.font.SysFont("Arial", size)
        return self.fonts[size]
    
    def init_themes(self):
        """Initialize and register themes."""
        # Create dark theme
        self.dark_theme = Theme(
            name="Dark Theme",
            id="dark",
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
        register_theme(self.dark_theme)
        
        # Create light theme
        self.light_theme = Theme(
            name="Light Theme",
            id="light",
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
        register_theme(self.light_theme)
        
        # Create theme provider with dark theme as default
        self.theme_provider = ThemeProvider(self.dark_theme)
        
        # Register module-specific styles
        register_cognitive_module_styles(self.dark_theme)
        register_cognitive_module_styles(self.light_theme)
    
    def init_ui(self):
        """Initialize the UI components."""
        self.ui = UI()
        self.component_factory = ComponentFactory(self.theme_provider)
        
        # No active module initially
        self.active_module = None
    
    def toggle_theme(self):
        """Toggle between dark and light themes."""
        if self.theme_provider.theme.id == "dark":
            self.theme_provider.theme = self.light_theme
            logger.info("Switched to light theme")
        else:
            self.theme_provider.theme = self.dark_theme
            logger.info("Switched to dark theme")
        
        # If a module is active, update its theme
        if self.active_module:
            self.active_module.theme_provider = self.theme_provider
            self.active_module.build_ui()
    
    def build_module_selection_ui(self):
        """Build the module selection UI."""
        # Clear existing UI
        self.ui = UI()
        
        # Main container
        container = Component(
            type="rectangle",
            position=(0, 0),
            width=self.width,
            height=self.height,
            style=self.theme_provider.theme.get_style("common.container")
        )
        self.ui.add_component(container)
        
        # Title
        title = Component(
            type="text",
            text="MetaMindIQTrain - Theme-Aware Cognitive Modules",
            position=(self.width/2, self.scaling_helper.scale_value(80)),
            style=self.theme_provider.theme.get_style("common.title"),
            align="center"
        )
        self.ui.add_component(title)
        
        # Subtitle with theme info
        theme_name = "Dark Theme" if self.theme_provider.theme.id == "dark" else "Light Theme"
        subtitle = Component(
            type="text",
            text=f"Current Theme: {theme_name} (Press T to toggle)",
            position=(self.width/2, self.scaling_helper.scale_value(140)),
            style=self.theme_provider.theme.get_style("common.subtitle"),
            align="center"
        )
        self.ui.add_component(subtitle)
        
        # Module selection instructions
        instructions = Component(
            type="text",
            text="Select a cognitive training module to test:",
            position=(self.width/2, self.scaling_helper.scale_value(200)),
            style=self.theme_provider.theme.get_style("common.instruction"),
            align="center"
        )
        self.ui.add_component(instructions)
        
        # Available modules
        modules = [
            {
                "name": "Expand Vision",
                "type": self.MODULE_EXPAND_VISION,
                "description": "Peripheral vision and attention training"
            }
        ]
        
        if has_symbol_memory:
            modules.append({
                "name": "Symbol Memory",
                "type": self.MODULE_SYMBOL_MEMORY,
                "description": "Visual memory and pattern recall training"
            })
        
        # Calculate button dimensions and placement
        button_width = self.scaling_helper.scale_value(300)
        button_height = self.scaling_helper.scale_value(80)
        spacing = self.scaling_helper.scale_value(40)
        start_y = self.scaling_helper.scale_value(300)
        
        # Module selection buttons
        self.module_buttons = []
        
        for i, module in enumerate(modules):
            # Button position
            button_x = (self.width - button_width) / 2
            button_y = start_y + i * (button_height + spacing)
            
            # Create button
            button = Component(
                type="rectangle",
                position=(button_x, button_y),
                width=button_width,
                height=button_height,
                style=self.theme_provider.theme.get_style("common.button")
            )
            self.ui.add_component(button)
            
            # Button text
            text = Component(
                type="text",
                text=module["name"],
                position=(button_x + button_width/2, button_y + button_height/3),
                style=self.theme_provider.theme.get_style("common.button_text"),
                align="center"
            )
            self.ui.add_component(text)
            
            # Button description
            desc = Component(
                type="text",
                text=module["description"],
                position=(button_x + button_width/2, button_y + button_height*2/3),
                style=self.theme_provider.theme.get_style("common.button_description"),
                align="center"
            )
            self.ui.add_component(desc)
            
            # Store button bounds and module type for click detection
            self.module_buttons.append({
                "rect": (button_x, button_y, button_width, button_height),
                "type": module["type"]
            })
        
        # Exit instructions
        exit_instructions = Component(
            type="text",
            text="Press ESC to exit",
            position=(self.width/2, self.height - self.scaling_helper.scale_value(50)),
            style=self.theme_provider.theme.get_style("common.instruction"),
            align="center"
        )
        self.ui.add_component(exit_instructions)
    
    def launch_module(self, module_type):
        """Launch the selected cognitive module.
        
        Args:
            module_type: Type of module to launch
        """
        # Clean up previous module if any
        self.active_module = None
        
        # Create new module instance
        if module_type == self.MODULE_EXPAND_VISION:
            self.active_module = ThemeAwareExpandVision(
                difficulty=1,
                theme_provider=self.theme_provider,
                resolution=(self.width, self.height)
            )
            logger.info("Launched Expand Vision module")
        elif module_type == self.MODULE_SYMBOL_MEMORY and has_symbol_memory:
            self.active_module = ThemeAwareSymbolMemory(
                difficulty=1,
                theme_provider=self.theme_provider,
                resolution=(self.width, self.height)
            )
            logger.info("Launched Symbol Memory module")
        
        # Update state
        if self.active_module:
            self.active_module_type = module_type
            self.state = self.STATE_MODULE_RUNNING
            
            # Initialize module UI
            self.active_module.build_ui()
    
    def return_to_module_selection(self):
        """Return to the module selection screen."""
        self.active_module = None
        self.active_module_type = -1
        self.state = self.STATE_MODULE_SELECTION
        self.build_module_selection_ui()
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == self.STATE_MODULE_RUNNING:
                        self.return_to_module_selection()
                    else:
                        return False
                
                elif event.key == pygame.K_t:
                    # Toggle theme
                    self.toggle_theme()
                    
                    # Rebuild UI if in module selection
                    if self.state == self.STATE_MODULE_SELECTION:
                        self.build_module_selection_ui()
                
                elif event.key == pygame.K_BACKSPACE and self.active_module:
                    # Pass backspace as a string for text input handling
                    self.active_module.handle_key_press("\b")
                
                elif event.key == pygame.K_RETURN and self.active_module:
                    # Pass enter as a string for form submission
                    self.active_module.handle_key_press("\r")
                
                elif self.active_module:
                    # Pass other keys to the active module
                    if event.unicode:
                        self.active_module.handle_key_press(event.unicode)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if self.state == self.STATE_MODULE_SELECTION:
                        # Check if a module button was clicked
                        for button in self.module_buttons:
                            rect = button["rect"]
                            if (rect[0] <= mouse_pos[0] <= rect[0] + rect[2] and
                                rect[1] <= mouse_pos[1] <= rect[1] + rect[3]):
                                self.launch_module(button["type"])
                                break
                    
                    elif self.state == self.STATE_MODULE_RUNNING and self.active_module:
                        # Pass click to active module
                        self.active_module.handle_click(mouse_pos)
        
        return True
    
    def update(self):
        """Update game state."""
        # Calculate delta time
        self.current_time = time.time()
        delta_time = self.current_time - self.prev_time
        self.prev_time = self.current_time
        
        # Update active module if any
        if self.state == self.STATE_MODULE_RUNNING and self.active_module:
            self.active_module.update(delta_time)
    
    def render(self):
        """Render the current state to the screen."""
        # Clear screen
        self.screen.fill(self.theme_provider.theme.get_color("background"))
        
        if self.state == self.STATE_MODULE_SELECTION:
            # Render module selection UI
            self.render_ui(self.ui)
        
        elif self.state == self.STATE_MODULE_RUNNING and self.active_module:
            # Render active module UI
            self.render_ui(self.active_module.ui)
        
        # Update the display
        pygame.display.flip()
    
    def render_ui(self, ui):
        """Render UI components to the screen.
        
        Args:
            ui: UI object containing components to render
        """
        components = ui.to_dict().get("components", [])
        
        for component in components:
            component_type = component.get("type")
            
            if component_type == "rectangle":
                self.render_rectangle(component)
            elif component_type == "text":
                self.render_text(component)
            elif component_type == "circle":
                self.render_circle(component)
            elif component_type == "button":
                self.render_button(component)
            elif component_type == "container":
                self.render_rectangle(component)
                # Render children if any
                children = component.get("children", [])
                if children:
                    child_ui = UI()
                    child_ui.set_from_dict({"components": children})
                    self.render_ui(child_ui)
    
    def render_rectangle(self, component):
        """Render a rectangle component."""
        position = component.get("position", (0, 0))
        width = component.get("width", 100)
        height = component.get("height", 100)
        style = component.get("style", {})
        
        bg_color = style.get("backgroundColor", (100, 100, 100))
        border_width = style.get("borderWidth", 0)
        border_color = style.get("borderColor", (0, 0, 0))
        border_radius = style.get("borderRadius", 0)
        
        rect = pygame.Rect(position[0], position[1], width, height)
        
        # Draw with border radius if supported
        if border_radius > 0:
            pygame.draw.rect(self.screen, bg_color, rect, 0, border_radius)
            if border_width > 0:
                pygame.draw.rect(self.screen, border_color, rect, border_width, border_radius)
        else:
            pygame.draw.rect(self.screen, bg_color, rect)
            if border_width > 0:
                pygame.draw.rect(self.screen, border_color, rect, border_width)
    
    def render_text(self, component):
        """Render a text component."""
        text = component.get("text", "")
        position = component.get("position", (0, 0))
        style = component.get("style", {})
        align = component.get("align", "left")
        
        color = style.get("color", (255, 255, 255))
        font_size = style.get("fontSize", 20)
        
        # Get font
        font = self.get_font(font_size)
        
        # Render text
        text_surface = font.render(str(text), True, color)
        
        # Adjust position based on alignment
        x, y = position
        if align == "center":
            x -= text_surface.get_width() // 2
        elif align == "right":
            x -= text_surface.get_width()
        
        # Draw text
        self.screen.blit(text_surface, (x, y))
    
    def render_circle(self, component):
        """Render a circle component."""
        position = component.get("position", (0, 0))
        radius = component.get("radius", 10)
        style = component.get("style", {})
        
        bg_color = style.get("backgroundColor", (100, 100, 100))
        border_width = style.get("borderWidth", 0)
        border_color = style.get("borderColor", (0, 0, 0))
        
        # Draw filled circle
        pygame.draw.circle(self.screen, bg_color, position, radius)
        
        # Draw border if needed
        if border_width > 0:
            pygame.draw.circle(self.screen, border_color, position, radius, border_width)
    
    def render_button(self, component):
        """Render a button component (rectangle with text)."""
        # Render button background (as rectangle)
        self.render_rectangle(component)
        
        # Extract text from component
        text = component.get("text", "")
        position = component.get("position", (0, 0))
        width = component.get("width", 100)
        height = component.get("height", 50)
        style = component.get("style", {})
        
        # Text color and properties
        text_color = style.get("textColor", (255, 255, 255))
        font_size = style.get("fontSize", 20)
        
        # Create text component
        text_component = {
            "type": "text",
            "text": text,
            "position": (position[0] + width // 2, position[1] + height // 2),
            "style": {"color": text_color, "fontSize": font_size},
            "align": "center"
        }
        
        # Render text
        self.render_text(text_component)
    
    def run(self):
        """Main game loop."""
        # Build initial module selection UI
        self.build_module_selection_ui()
        
        # Main loop
        running = True
        clock = pygame.time.Clock()
        
        while running:
            # Handle events
            running = self.handle_events()
            
            # Update game state
            self.update()
            
            # Render to screen
            self.render()
            
            # Cap at 60 FPS
            clock.tick(60)
        
        # Clean up
        pygame.quit()


if __name__ == "__main__":
    # Run the test
    test = ModuleTest()
    test.run() 