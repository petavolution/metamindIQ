#!/usr/bin/env python3
"""
Test script for the optimized music module system.

This script demonstrates loading and using the optimized music module system,
including the unified audio engine and specialized module loader.
"""

import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure the project is in the Python path
project_dir = Path(__file__).resolve().parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

def test_audio_engine():
    """Test the unified audio engine."""
    try:
        from MetaMindIQTrain.core.audio.engine import get_audio_engine
        
        # Get the audio engine
        engine = get_audio_engine()
        logger.info(f"Audio engine initialized using {engine.get_backend_name()}")
        
        # Play a test note
        logger.info("Playing a test note (C4)...")
        engine.play_note(frequency=261.63, duration=1.0)  # C4
        
        # Wait for the note to finish
        import time
        time.sleep(1.5)
        
        # Play a chord
        logger.info("Playing a C major chord...")
        engine.play_chord(
            frequencies=[261.63, 329.63, 392.00],  # C4, E4, G4
            duration=1.5
        )
        time.sleep(2.0)
        
        return True
    except Exception as e:
        logger.error(f"Error testing audio engine: {e}")
        return False

def test_music_module_loader():
    """Test the specialized music module loader."""
    try:
        # Import the music module loader
        from MetaMindIQTrain.server.optimized.music_module_loader import get_music_module_loader
        
        # Get the loader
        loader = get_music_module_loader()
        logger.info("Music module loader initialized")
        
        # List available modules
        modules = loader.list_modules()
        logger.info(f"Found {len(modules)} music modules:")
        for module in modules:
            logger.info(f"- {module['name']} ({module['id']})")
        
        return True
    except Exception as e:
        logger.error(f"Error testing music module loader: {e}")
        return False

def test_music_theory_module():
    """Test the simplified music theory module."""
    try:
        # Import the module directly
        from MetaMindIQTrain.modules.music.music_theory_simplified import MusicTheorySimplifiedModule
        
        # Create an instance
        module = MusicTheorySimplifiedModule()
        logger.info(f"Created music theory module: {module.name}")
        
        # Play a scale
        logger.info("Playing a C major scale...")
        module.play_scale("C4", "Major")
        
        # Wait for the scale to finish
        import time
        time.sleep(3.0)
        
        # Generate a new challenge
        logger.info("Generating a new challenge...")
        module.generate_challenge()
        logger.info(f"Challenge type: {module.current_challenge_type}")
        logger.info(f"Correct answer: {module.correct_answer}")
        logger.info(f"Options: {module.current_options}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing music theory module: {e}")
        return False

def test_integration():
    """Test integration with the module registry."""
    try:
        # Import the module registry
        from MetaMindIQTrain.module_registry import get_available_modules, create_module_instance
        
        # Register the music module loader with the registry
        from MetaMindIQTrain.server.optimized.music_module_loader import get_music_module_loader
        loader = get_music_module_loader()
        loader.initialize_for_server()
        
        # Get all available modules (should include music modules)
        modules = get_available_modules()
        music_modules = [m for m in modules if m.get('category') == 'Music']
        logger.info(f"Found {len(music_modules)} music modules in registry:")
        for module in music_modules:
            logger.info(f"- {module['name']} ({module['id']})")
        
        # Try to create a module instance through the registry
        if music_modules:
            module_id = music_modules[0]['id']
            logger.info(f"Creating instance of {module_id} through registry...")
            instance = create_module_instance(module_id)
            if instance:
                logger.info(f"Successfully created {instance.name}")
                return True
        
        return False
    except Exception as e:
        logger.error(f"Error testing integration: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("=== Testing Optimized Music Module System ===")
    
    # Run tests
    audio_test = test_audio_engine()
    loader_test = test_music_module_loader()
    module_test = test_music_theory_module()
    integration_test = test_integration()
    
    # Print results
    logger.info("\n=== Test Results ===")
    logger.info(f"Audio Engine: {'PASSED' if audio_test else 'FAILED'}")
    logger.info(f"Module Loader: {'PASSED' if loader_test else 'FAILED'}")
    logger.info(f"Music Theory Module: {'PASSED' if module_test else 'FAILED'}")
    logger.info(f"Registry Integration: {'PASSED' if integration_test else 'FAILED'}")
    
    # Overall result
    all_passed = audio_test and loader_test and module_test and integration_test
    logger.info(f"\nOverall Result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 