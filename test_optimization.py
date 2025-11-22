#!/usr/bin/env python3
"""
Test Script for Optimized MetaMindIQTrain

This script tests the optimized components of the MetaMindIQTrain platform,
including the unified audio engine, renderer optimizations, and component system.
"""

import sys
import logging
import time
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_renderer():
    """Test the optimized renderer."""
    logger.info("=== Testing Optimized Renderer ===")
    
    try:
        from MetaMindIQTrain.core.renderer import get_renderer, Renderer
        
        # Get renderer instance
        renderer = get_renderer()
        
        # Initialize with Pygame backend
        result = renderer.initialize(800, 600, "pygame", "Renderer Test")
        if not result:
            logger.error("Failed to initialize renderer")
            return False
        
        logger.info(f"Renderer initialized with backend: {renderer.backend_name}")
        
        # Enable batching
        renderer.enable_batching(True)
        logger.info("Batching enabled")
        
        # Test rendering operations
        renderer.clear((0, 0, 0, 255))
        
        # Queue several render operations
        for i in range(5):
            x = 100 + i * 120
            y = 100
            renderer.queue_render("rectangle", x, y, 100, 100, (255, 0, 0, 255))
            
        # Flush queue
        renderer.flush_queue()
        
        # Test specialized UI elements
        renderer.queue_render(
            "ui_element", 
            "button", 
            (300, 250, 200, 50), 
            (0, 120, 200, 255),
            text="Test Button",
            highlight=True,
            text_color=(255, 255, 255, 255)
        )
        
        # Present frame
        renderer.present()
        
        # Get render stats
        stats = renderer.get_stats()
        logger.info(f"Render stats: {stats}")
        
        # Short delay to see the result
        time.sleep(0.5)
        
        logger.info("Renderer test successful")
        return True
        
    except Exception as e:
        logger.error(f"Renderer test failed: {e}", exc_info=True)
        return False

def test_audio_engine():
    """Test the unified audio engine."""
    logger.info("=== Testing Unified Audio Engine ===")
    
    try:
        from MetaMindIQTrain.modules.music.audio_synthesis import AudioEngine, AUDIO_AVAILABLE
        
        # Get audio engine instance
        engine = AudioEngine.get_instance()
        
        logger.info(f"Audio engine initialized, audio available: {AUDIO_AVAILABLE}")
        
        if AUDIO_AVAILABLE:
            # Test synthesizing a simple tone
            logger.info("Synthesizing and playing a simple tone (A4)...")
            waveform = engine.synthesize(440.0, 0.5, "sine")
            engine.play(waveform, 0.7)
            time.sleep(0.6)
            
            # Test playing a note by name
            logger.info("Playing a note by name (C4)...")
            engine.play_note("C4", 0.5, 0.7)
            time.sleep(0.6)
            
            # Test playing a chord
            logger.info("Playing a C major chord...")
            engine.play_chord(["C4", "E4", "G4"], 1.0, 0.7)
            time.sleep(1.1)
            
            # Test playing a scale
            logger.info("Playing a C major scale...")
            engine.play_scale("C4", "Major", 0.2, 0.7)
            time.sleep(2.0)
        else:
            logger.warning("Audio not available, skipping audio playback tests")
        
        logger.info("Audio engine test successful")
        return True
        
    except Exception as e:
        logger.error(f"Audio engine test failed: {e}", exc_info=True)
        return False

def test_component_system():
    """Test the optimized component system."""
    logger.info("=== Testing Component System ===")
    
    try:
        from MetaMindIQTrain.core.component_system import Component, UIComponent, Container, Text, Button
        
        # Create a simple component hierarchy
        root = Container("root")
        root.set_size(800, 600)
        
        # Add some child components
        header = Container("header")
        header.set_size(800, 60)
        header.set_property("background_color", (50, 50, 100))
        root.add_child(header)
        
        title = Text("title")
        title.set_text("Component System Test")
        title.set_position(400, 30)
        title.set_property("align", "center")
        title.set_property("color", (255, 255, 255))
        header.add_child(title)
        
        # Test event handling
        button = Button("test_button")
        button.set_text("Test Button")
        button.set_position(350, 200)
        button.set_size(100, 40)
        
        click_count = [0]  # Use a list for mutable closure
        
        def on_button_click(button):
            click_count[0] += 1
            logger.info(f"Button clicked, count: {click_count[0]}")
            return True
            
        button.set_on_click(on_button_click)
        root.add_child(button)
        
        # Mount component tree
        from MetaMindIQTrain.core.component_system import mount_component_tree
        mount_component_tree(root)
        
        # Verify components are mounted
        logger.info(f"Root component has {len(root.get_children())} children")
        logger.info(f"Button is mounted: {button._mounted}")
        
        # Simulate a click event
        button.trigger_event("mouse_down", {"pos": (400, 220)})
        button.trigger_event("mouse_up", {"pos": (400, 220)})
        
        # Check click count
        logger.info(f"Final click count: {click_count[0]}")
        
        logger.info("Component system test successful")
        return True
        
    except Exception as e:
        logger.error(f"Component system test failed: {e}", exc_info=True)
        return False

def test_module_loading():
    """Test optimized module loading."""
    logger.info("=== Testing Module Loading ===")
    
    try:
        from MetaMindIQTrain.core.application import Application
        
        # Create application instance
        app = Application("Module Test")
        
        # Initialize with headless renderer for testing
        app.initialize(800, 600, "headless")
        
        # Define module factory function
        def create_example_module():
            from MetaMindIQTrain.modules.example_module import create_module
            return create_module()
        
        # Create and set module
        module = create_example_module()
        app.set_root_component(module)
        
        # Trigger module mounting
        module.trigger_event("mount")
        
        # Check if module is properly mounted
        logger.info(f"Module is mounted: {module._mounted}")
        logger.info(f"Module has {len(module.get_children())} children")
        
        logger.info("Module loading test successful")
        return True
        
    except Exception as e:
        logger.error(f"Module loading test failed: {e}", exc_info=True)
        return False

def main():
    """Run all tests."""
    logger.info("Starting optimization tests...")
    
    # Track test results
    results = {}
    
    # Run tests
    results["renderer"] = test_renderer()
    results["audio_engine"] = test_audio_engine()
    results["component_system"] = test_component_system()
    results["module_loading"] = test_module_loading()
    
    # Print summary
    logger.info("\n=== Test Results ===")
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        logger.info(f"{test_name}: {status}")
    
    # Overall result
    all_passed = all(results.values())
    logger.info(f"\nOverall result: {'PASS' if all_passed else 'FAIL'}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 