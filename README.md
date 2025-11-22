# MetaMindIQTrain Optimized

## Overview

MetaMindIQTrain is a cognitive training platform designed to enhance mental capabilities through various exercises. This optimized version features a complete architectural overhaul focusing on performance and flexibility.

## Key Optimizations

1. **Unified Component System**: Declarative UI with automatic diffing and component memoization
2. **Optimized Rendering**: Surface caching, component pooling, and batch rendering
3. **Dynamic Resolution Support**: Adaptive layouts that work on any screen size
4. **Efficient State Management**: Delta encoding for minimal state updates
5. **Modular Architecture**: Clean separation between modules and rendering

## Directory Structure

```
MetaMindIQTrain/
├── core/                   # Core framework components
│   └── unified_component_system.py # Component base classes and utilities
├── clients/                # Client renderers
│   ├── pygame/            # Pygame renderer
│   │   └── unified_renderer.py # Optimized pygame renderer
│   └── terminal/          # Terminal renderer (optional)
├── modules/                # Training modules
│   ├── unified_symbol_memory.py    # Symbol memory game
│   ├── unified_morph_matrix.py     # Pattern recognition exercise
│   └── unified_expand_vision.py    # Peripheral vision training
├── tests/                  # Test suite
│   ├── test_modules.py            # Module testing utility
│   ├── test_component_system.py   # Unit tests for component system
│   └── setup_executable.py        # Permission setup utility
└── run_unified_client.py   # Client launcher
```

## Running a Module

```bash
# Run a specific module
./run_unified_client.py unified_symbol_memory

# Run other optimized modules
./run_unified_client.py unified_morph_matrix
./run_unified_client.py unified_expand_vision

# List available modules
./run_unified_client.py --list

# Run with a specific resolution
./run_unified_client.py unified_symbol_memory --width 1920 --height 1080

# Run with terminal renderer (if implemented)
./run_unified_client.py unified_symbol_memory --terminal

# Run with debug logging
./run_unified_client.py unified_symbol_memory --debug
```

## Available Training Modules

1. **Symbol Memory**: Memorize and recall symbols in a grid
2. **Morph Matrix**: Identify patterns that are exact rotations vs. modified patterns
3. **Expand Vision**: Focus on a central point while tracking numbers in peripheral vision

## Testing the Modules

The `tests/` directory contains tools for testing the framework and modules:

```bash
# Run the module tester
./tests/test_modules.py --list       # List all available modules
./tests/test_modules.py unified_symbol_memory  # Test a specific module
./tests/test_modules.py --all        # Test all modules

# Run unit tests for the component system
./tests/test_component_system.py

# Make all Python files executable
./tests/setup_executable.py
```

## Creating New Modules

New modules should inherit the base functionality and implement these key methods:

1. `initialize()`: Set up initial state
2. `update()`: Update module state
3. `build_ui()`: Create and return UI components
4. `handle_click()`: Process user clicks
5. `handle_key()`: Process keyboard input
6. `get_state()`: Return current state for rendering

See the existing unified modules for complete examples.

## Performance Monitoring

The unified client includes built-in performance monitoring. Statistics are logged periodically during execution and can be accessed programmatically through the renderer's `get_stats()` method. 

## Troubleshooting

If you encounter permission issues when running scripts, use the setup utility:

```bash
python3 MetaMindIQTrain/tests/setup_executable.py
```

This will make all Python files in the project executable.

## Testing and Development

### Test Scripts

Several test scripts are available to help with development and testing:

#### Basic Pygame Test
Tests basic Pygame functionality to ensure rendering is working properly:

```
./tests/basic_pygame_test.py
```

#### Direct Module Runner
For running modules directly, bypassing the module system (useful for debugging):

```
./tests/run_module_direct.py [module_name]
```

#### Simple Module Runner
For listing available unified modules:

```
./tests/simple_module_runner.py --list
```

### Making Scripts Executable

If you need to make Python scripts executable, use:

```
./tests/setup_executable.py
```

This script will recursively set executable permissions on all Python files in the project. 