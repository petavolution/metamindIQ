"""
MetaMindIQTrain Simple Server Package

This package provides a simple, reliable HTTP server implementation for the MetaMindIQTrain platform.
It focuses on robustness and minimal dependencies.
"""

__version__ = '1.0.0'

# Expose the run_server function directly
from MetaMindIQTrain.server.simple.server import SimpleServer, run_server

__all__ = ['run_server'] 