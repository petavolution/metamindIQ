#!/usr/bin/env python3
"""
Module Provider for MetaMindIQTrain.

This module handles registration, discovery, and information about
all available training modules, providing a unified interface
for the server to access module functionality and UI layouts.
"""

import os
import sys
import logging
import importlib
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Define available modules
AVAILABLE_MODULES = {
    'symbol_memory': {
        'name': 'Symbol Memory',
        'description': 'Train your memory by recalling sequences of symbols',
        'difficulty': 'Medium',
        'category': 'Memory',
        'module_path': 'MetaMindIQTrain.modules.symbol_memory',
        'class_name': 'SymbolMemoryModule'
    },
    'morph_matrix': {
        'name': 'Morph Matrix',
        'description': 'Identify patterns in a morphing matrix of elements',
        'difficulty': 'Hard',
        'category': 'Pattern Recognition',
        'module_path': 'MetaMindIQTrain.modules.morph_matrix',
        'class_name': 'MorphMatrixModule'
    },
    'expand_vision': {
        'name': 'Expand Vision',
        'description': 'Expand your visual awareness by tracking multiple elements',
        'difficulty': 'Medium',
        'category': 'Visual Attention',
        'module_path': 'MetaMindIQTrain.modules.expand_vision',
        'class_name': 'ExpandVisionModule'
    },
    'neural_flow': {
        'name': 'Neural Flow',
        'description': 'Enhance cognitive processing speed, neural pathway formation, and visual-spatial processing',
        'difficulty': 'Medium',
        'category': 'Cognitive Flexibility',
        'module_path': 'MetaMindIQTrain.modules.neural_flow',
        'class_name': 'NeuralFlowModule'
    },
    'quantum_memory': {
        'name': 'Quantum Memory',
        'description': 'Enhance working memory and cognitive flexibility through quantum-inspired challenges',
        'difficulty': 'Hard',
        'category': 'Working Memory',
        'module_path': 'MetaMindIQTrain.modules.quantum_memory',
        'class_name': 'QuantumMemoryModule'
    },
    'psychoacoustic_wizard': {
        'name': 'Psychoacoustic Wizard',
        'description': 'Master rhythm, timing, and audio-visual integration',
        'difficulty': 'Medium',
        'category': 'Audio-Visual',
        'module_path': 'MetaMindIQTrain.modules.psychoacoustic_wizard',
        'class_name': 'PsychoacousticWizardModule'
    }
}

class ModuleProvider:
    """Provides module information and instances for the server."""
    
    def __init__(self):
        """Initialize the module provider."""
        self.modules = {}
        self.module_instances = {}
        self.layouts = {}
        self._load_modules()
        
    def _load_modules(self):
        """Load all available modules."""
        for module_id, module_info in AVAILABLE_MODULES.items():
            try:
                # Store module info
                self.modules[module_id] = module_info
                
                # Try to load module layout
                self._load_module_layout(module_id)
                
                logger.info(f"Module registered: {module_id} ({module_info['name']})")
            except Exception as e:
                logger.error(f"Error loading module {module_id}: {e}")
                
    def _load_module_layout(self, module_id):
        """Load layout information for a module.
        
        Args:
            module_id: ID of the module to load layout for
        """
        try:
            # Try to import the module
            module_info = AVAILABLE_MODULES[module_id]
            module_path = module_info['module_path']
            
            # Import the module
            module = importlib.import_module(module_path)
            
            # Get layout if available
            if hasattr(module, 'get_layout'):
                layout = module.get_layout()
                self.layouts[module_id] = layout
                logger.info(f"Loaded layout for module: {module_id}")
            else:
                logger.warning(f"No layout found for module: {module_id}")
                
        except Exception as e:
            logger.error(f"Error loading layout for module {module_id}: {e}")
            
    def get_module_list(self) -> Dict[str, Dict[str, Any]]:
        """Get a list of all available modules.
        
        Returns:
            Dictionary of module information
        """
        return self.modules
    
    def get_module_info(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific module.
        
        Args:
            module_id: ID of the module to get information for
            
        Returns:
            Dictionary of module information, or None if not found
        """
        return self.modules.get(module_id)
        
    def get_module_instance(self, module_id: str) -> Optional[Any]:
        """Get an instance of a module.
        
        Args:
            module_id: ID of the module to get an instance of
            
        Returns:
            Module instance, or None if not found/loadable
        """
        # Return existing instance if available
        if module_id in self.module_instances:
            return self.module_instances[module_id]
            
        # Try to create a new instance
        try:
            module_info = self.get_module_info(module_id)
            if not module_info:
                logger.error(f"Module not found: {module_id}")
                return None
                
            # Import the module
            module = importlib.import_module(module_info['module_path'])
            
            # Get the module class
            module_class = getattr(module, module_info['class_name'])
            
            # Create an instance
            instance = module_class()
            
            # Store for future use
            self.module_instances[module_id] = instance
            
            return instance
            
        except Exception as e:
            logger.error(f"Error creating module instance {module_id}: {e}")
            return None
            
    def get_module_layout(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Get layout information for a module.
        
        Args:
            module_id: ID of the module to get layout for
            
        Returns:
            Layout dictionary, or None if not found
        """
        return self.layouts.get(module_id)

# Singleton instance
_provider = None

def get_provider() -> ModuleProvider:
    """Get the module provider instance.
    
    Returns:
        ModuleProvider instance
    """
    global _provider
    if _provider is None:
        _provider = ModuleProvider()
    return _provider 