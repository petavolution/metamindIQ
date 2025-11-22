#!/usr/bin/env python3
"""
Test Script for Running the Optimized MetaMindIQTrain Platform

This script runs both the optimized server and client for testing purposes.
It manages starting the server, waiting for it to initialize, and then launching the client.
"""

import os
import sys
import time
import subprocess
import argparse
import threading
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('TestOptimized')

# Add the project root to the Python path
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))

def run_server(args):
    """
    Start the server process.
    """
    server_cmd = [
        sys.executable,
        f"{script_dir}/MetaMindIQTrain/run_server.py",
        "--port", str(args.port),
        "--host", args.host
    ]
    
    if args.debug:
        server_cmd.append("--debug")
    
    logger.info(f"Starting server with command: {' '.join(server_cmd)}")
    
    try:
        server_process = subprocess.Popen(
            server_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            env=dict(os.environ, PYTHONPATH=str(script_dir))
        )
        logger.info("Server started successfully")
        
        # Start a thread to log server output
        def log_output():
            for line in server_process.stdout:
                logger.info(f"Server output: {line.strip()}")
        
        threading.Thread(target=log_output, daemon=True).start()
        
        return server_process
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to start server: {e}")
        return None

def run_client(args):
    """
    Start the client process.
    """
    client_cmd = [
        sys.executable,
        f"{script_dir}/MetaMindIQTrain/run_client.py",
        "--server", f"http://{args.host}:{args.port}",
        "--width", str(args.client_width),
        "--height", str(args.client_height)
    ]
    
    if args.debug:
        client_cmd.append("--debug")
    
    logger.info(f"Starting client with command: {' '.join(client_cmd)}")
    
    try:
        client_process = subprocess.Popen(
            client_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            env=dict(os.environ, PYTHONPATH=str(script_dir))
        )
        logger.info("Client started successfully")
        
        # Log the client's output in real-time
        for line in client_process.stdout:
            logger.info(f"Client output: {line.strip()}")
        
        return client_process
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to start client: {e}")
        return None

def main():
    """
    Run the server and client processes.
    """
    parser = argparse.ArgumentParser(description='Run the MetaMindIQTrain platform in test mode.')
    parser.add_argument('--server-only', action='store_true', help='Run only the server')
    parser.add_argument('--client-only', action='store_true', help='Run only the client')
    parser.add_argument('--port', type=int, default=5000, help='Server port (default: 5000)')
    parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    parser.add_argument('--window-size', default='800x600', help='Client window size (WIDTHxHEIGHT)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Parse client window size
    try:
        width, height = args.window_size.lower().split('x')
        args.client_width = int(width)
        args.client_height = int(height)
    except (ValueError, AttributeError):
        logger.error(f"Invalid window size format: {args.window_size}. Use WIDTHxHEIGHT format.")
        return 1
    
    server_process = None
    client_process = None
    
    try:
        # Start server if not client-only
        if not args.client_only:
            server_process = run_server(args)
            if not server_process:
                return 1
            
            # Give the server time to start up
            time.sleep(2)
        
        # Start client if not server-only
        if not args.server_only:
            client_process = run_client(args)
            if not client_process:
                return 1
            
            # Wait for client to finish
            client_process.wait()
            logger.info("Client process terminated")
        else:
            # In server-only mode, wait for keyboard interrupt
            logger.info("Server running. Press Ctrl+C to terminate.")
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        logger.info("Interrupt received, shutting down...")
    finally:
        # Terminate processes
        if client_process and client_process.poll() is None:
            logger.info("Terminating client process...")
            client_process.terminate()
            client_process.wait()
        
        if server_process and server_process.poll() is None:
            logger.info("Terminating server process...")
            server_process.terminate()
            server_process.wait()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 