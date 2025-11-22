#!/usr/bin/env python3
"""
Music Module Loader for MetaMindIQTrain Server

This module provides specialized handling for music-based training modules,
including optimized state synchronization and resource management.
"""

import logging
import sys
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional, Type

# Configure logging
logger = logging.getLogger(__name__)

class MusicModuleLoader:
    """
    Specialized loader for music training modules.
    
    This class provides optimized loading, initialization, and management
    of music-related modules. It handles audio resource management and
    ensures proper cleanup when modules are unloaded.
    """
    
    def __init__(self):
        """Initialize the music module loader."""
        self.loaded_modules = {}
        self.module_metadata = {}
        self.discover_modules()
        
    def discover_modules(self):
        """
        Discover available music modules.
        
        This method scans the music module directory and collects metadata
        about available modules without loading them completely.
        """
        try:
            # Get the music module directory
            module_dir = Path(__file__).parent.parent.parent / "modules" / "music"
            
            if not module_dir.exists():
                logger.warning(f"Music module directory not found: {module_dir}")
                return
            
            # Scan for module files (skip __init__.py and base.py)
            module_files = [
                f for f in module_dir.glob("*.py") 
                if f.name not in ["__init__.py", "base.py", "README.md"]
                and not f.name.startswith("_")
            ]
            
            # Extract module information
            for module_file in module_files:
                module_name = module_file.stem
                
                # Skip utility modules
                if module_name in ["audio_synthesis", "visual_components", "notation", "achievements"]:
                    continue
                
                # Generate module ID (convert from snake_case to CamelCase for class name)
                class_name_parts = [part.capitalize() for part in module_name.split('_')]
                class_name = ''.join(class_name_parts) + "Module"
                module_id = module_name
                
                # Add metadata
                self.module_metadata[module_id] = {
                    'id': module_id,
                    'name': ' '.join(class_name_parts),
                    'file_path': str(module_file),
                    'module_path': f"MetaMindIQTrain.modules.music.{module_name}",
                    'class_name': class_name,
                    'category': 'Music',
                    'initialized': False
                }
            
            logger.info(f"Discovered {len(self.module_metadata)} music modules")
            
        except Exception as e:
            logger.error(f"Error discovering music modules: {e}")
    
    def get_module_info(self, module_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific module.
        
        Args:
            module_id: The ID of the module to retrieve information for.
            
        Returns:
            Dict containing module information or None if not found.
        """
        return self.module_metadata.get(module_id)
    
    def list_modules(self) -> List[Dict[str, Any]]:
        """
        List all available music modules with their metadata.
        
        Returns:
            List of dictionaries containing module information.
        """
        return list(self.module_metadata.values())
    
    def load_module(self, module_id: str, **kwargs) -> Any:
        """
        Load and instantiate a music training module.
        
        Args:
            module_id: The ID of the module to load.
            **kwargs: Additional parameters to pass to the module constructor.
            
        Returns:
            An instance of the requested training module or None if not found.
            
        Raises:
            ImportError: If the module cannot be imported.
            AttributeError: If the specified class cannot be found in the module.
        """
        # Check if module is already loaded
        if module_id in self.loaded_modules:
            return self.loaded_modules[module_id]
        
        # Check if module exists
        if module_id not in self.module_metadata:
            logger.error(f"Music module '{module_id}' not found")
            return None
        
        module_info = self.module_metadata[module_id]
        
        try:
            # Import the module
            module_path = module_info['module_path']
            module = importlib.import_module(module_path)
            
            # Get the module class
            class_name = module_info['class_name']
            module_class = getattr(module, class_name)
            
            # Instantiate the module
            module_instance = module_class(**kwargs)
            
            # Store the loaded module
            self.loaded_modules[module_id] = module_instance
            
            # Update metadata
            self.module_metadata[module_id]['initialized'] = True
            
            logger.info(f"Loaded music module '{module_id}'")
            return module_instance
            
        except ImportError as e:
            logger.error(f"Error importing music module '{module_id}': {e}")
            raise
        except AttributeError as e:
            logger.error(f"Error finding class '{class_name}' in module '{module_path}': {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading music module '{module_id}': {e}")
            raise
    
    def unload_module(self, module_id: str) -> bool:
        """
        Unload a music module and clean up resources.
        
        This method properly cleans up any audio resources used by the module.
        
        Args:
            module_id: The ID of the module to unload.
            
        Returns:
            True if successful, False otherwise.
        """
        if module_id not in self.loaded_modules:
            logger.warning(f"Cannot unload module {module_id} - not loaded")
            return False
        
        try:
            # Get the module instance
            module = self.loaded_modules[module_id]
            
            # Clean up audio resources if possible
            if hasattr(module, 'stop_all_sounds'):
                module.stop_all_sounds()
            
            # Remove from loaded modules
            del self.loaded_modules[module_id]
            
            # Update metadata
            if module_id in self.module_metadata:
                self.module_metadata[module_id]['initialized'] = False
            
            logger.info(f"Unloaded music module '{module_id}'")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading music module '{module_id}': {e}")
            return False
    
    def unload_all(self):
        """Unload all music modules and clean up resources."""
        for module_id in list(self.loaded_modules.keys()):
            self.unload_module(module_id)
    
    def get_module_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get music modules filtered by category.
        
        Args:
            category: The category to filter by.
            
        Returns:
            List of music modules matching the specified category.
        """
        return [info for info in self.module_metadata.values() 
                if info.get('category', '').lower() == category.lower()]
    
    def initialize_for_server(self):
        """
        Initialize the music module loader for server use.
        
        This method performs additional setup required for server-side
        operation, such as registering with the main module registry.
        """
        try:
            # Import the module registry
            from MetaMindIQTrain.module_registry import register_module_type
            
            # Register this loader for music modules
            register_module_type('music', self)
            logger.info("Registered music module loader with module registry")
            
        except ImportError:
            logger.warning("Could not register with module registry - module may not be available")
        except Exception as e:
            logger.error(f"Error initializing music module loader for server: {e}")

# Singleton instance
_loader_instance = None

def get_music_module_loader():
    """
    Get the singleton instance of the MusicModuleLoader.
    
    Returns:
        MusicModuleLoader instance
    """
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = MusicModuleLoader()
    return _loader_instance

# For testing when run directly
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create loader
    loader = get_music_module_loader()
    
    # List available modules
    modules = loader.list_modules()
    print(f"Available music modules: {len(modules)}")
    for module in modules:
        print(f"- {module['name']} ({module['id']})")
    
    # Try loading a module
    if modules:
        first_module_id = modules[0]['id']
        module = loader.load_module(first_module_id)
        if module:
            print(f"Successfully loaded module: {module.name}")
            
            # Test a sound
            if hasattr(module, 'play_note'):
                print("Playing a test note...")
                module.play_note('C4')
                import time
                time.sleep(1)
            
            # Clean up
            loader.unload_module(first_module_id) 