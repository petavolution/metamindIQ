# MetaMindIQTrain Server Implementations

This directory contains the server implementations for the MetaMindIQTrain platform. The server provides HTTP and WebSocket APIs for interacting with the training modules.

## Directory Structure

- **base/**: Contains the base server abstract class that defines the common interface for all server implementations.
- **common/**: Contains common utilities and components used by all server implementations.
- **simple/**: A simple, reliable server implementation with minimal dependencies.
- **optimized/**: An optimized server implementation with advanced features like WebSocket support and caching.
- **utils/**: Utility functions and helpers specifically for the server implementations.

## Server Implementations

### Simple Server

The simple server provides a reliable, straightforward HTTP API for the training modules. Features include:

- Minimal dependencies (only standard library)
- Easy to install and configure
- Reliable operation with minimal points of failure
- Basic session management and caching
- Support for all core training modules

This server is recommended for simple deployments and testing.

### Optimized Server

The optimized server provides a high-performance implementation with advanced features. Features include:

- WebSocket support for real-time updates
- Advanced caching and performance optimizations
- Optional Flask support for advanced HTTP features
- Comprehensive metrics and monitoring
- Higher scalability for multiple concurrent users

This server is recommended for production deployments and situations where performance is critical.

## Core Training Modules

Both server implementations support the following core training modules:

- **SymbolMemory (symbol_memory.py)**: A memory training module where users have to remember symbol patterns and identify changes.
- **MorphMatrix (morph_matrix.py)**: A pattern recognition module focused on identifying rotated vs. mutated patterns.
- **ExpandVision (expand_vision.py)**: A peripheral vision training module where users focus on a central point while observing numbers in their peripheral vision.

## Usage

To run a server, use the `run_server.py` script in the project root:

```
# Run the simple server
python run_server.py --server-type=simple

# Run the optimized server
python run_server.py --server-type=optimized

# Run the optimized server with WebSocket but without Flask
python run_server.py --server-type=optimized --no-flask
```

See `python run_server.py --help` for more options. 