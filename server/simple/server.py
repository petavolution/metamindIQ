#!/usr/bin/env python3
"""
Simple HTTP Server for MetaMindIQTrain

This is a simple, reliable server implementation for the MetaMindIQTrain platform.
It provides a straightforward HTTP API for training modules with minimal dependencies.
"""

import http.server
import socketserver
import json
import logging
import threading
import time
import sys
import os
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path

# Configure relative imports
current_dir = Path(__file__).resolve().parent.parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import base server
from MetaMindIQTrain.server.base.base_server import BaseServer
from MetaMindIQTrain.module_registry import get_available_modules

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleRequestHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for the simple MetaMindIQTrain server.
    
    This handler processes HTTP requests and interacts with training modules.
    """
    
    def _send_response(self, status_code, data):
        """Send a JSON response.
        
        Args:
            status_code: HTTP status code
            data: Response data to be JSON-encoded
        """
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response = json.dumps(data).encode('utf-8')
        self.wfile.write(response)
        
        # Record the request
        if hasattr(self.server, 'server_instance'):
            self.server.server_instance.metrics_collector.record_request()
    
    def _send_error(self, status_code, message):
        """Send an error response.
        
        Args:
            status_code: HTTP status code
            message: Error message
        """
        self._send_response(status_code, {
            'error': message
        })
        
        # Record the error
        if hasattr(self.server, 'server_instance'):
            self.server.server_instance.metrics_collector.record_error()
    
    def _parse_path(self):
        """Parse the request path.
        
        Returns:
            Tuple of (endpoint, query_params)
        """
        path_parts = self.path.split('?')
        endpoint = path_parts[0]
        
        # Parse query parameters if present
        query_params = {}
        if len(path_parts) > 1:
            query_string = path_parts[1]
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    query_params[key] = value
        
        return endpoint, query_params
    
    def _parse_json_body(self):
        """Parse JSON request body.
        
        Returns:
            Parsed JSON data or None if invalid
        """
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length)
                return json.loads(body.decode('utf-8'))
            return {}
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse JSON body: {e}")
            return None
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        # Record the start time for metrics
        start_time = time.time()
        
        endpoint, params = self._parse_path()
        
        try:
            # Health check endpoint
            if endpoint == '/api/health':
                # Get server instance to access session manager
                server_instance = self.server.server_instance if hasattr(self.server, 'server_instance') else None
                
                # Prepare response data
                response_data = {
                    'status': 'ok',
                    'uptime': 0,
                    'requests': 0,
                    'errors': 0,
                    'active_sessions': 0
                }
                
                # Add metrics if available
                if server_instance:
                    metrics = server_instance.metrics_collector.get_all_metrics()
                    active_sessions = server_instance.get_active_sessions_count()
                    
                    response_data.update(metrics)
                    response_data['active_sessions'] = active_sessions
                
                self._send_response(200, response_data)
            
            # List available modules
            elif endpoint == '/api/modules':
                modules = get_available_modules()
                self._send_response(200, {
                    'modules': modules
                })
            
            # Get session state
            elif endpoint.startswith('/api/session/'):
                session_id = endpoint.split('/')[-1]
                
                # Get server instance to access session manager
                server_instance = self.server.server_instance if hasattr(self.server, 'server_instance') else None
                
                if server_instance:
                    session_manager = server_instance.session_manager
                    
                    # Check cache first
                    cached_state = session_manager.get_cached_state(session_id)
                    if cached_state:
                        self._send_response(200, {
                            'session_id': session_id,
                            'state': cached_state,
                            'cached': True
                        })
                        
                        # Record response time
                        response_time = (time.time() - start_time) * 1000
                        server_instance.metrics_collector.record_response_time(response_time)
                        return
                    
                    # Get from session manager
                    module = session_manager.get_session(session_id)
                    if module:
                        state = module.get_state()
                        
                        # Update cache
                        session_manager.update_cache(session_id, state)
                        
                        # Update last activity time
                        if hasattr(module, '__dict__'):
                            module.last_activity = time.time()
                        
                        self._send_response(200, {
                            'session_id': session_id,
                            'state': state
                        })
                        
                        # Record response time
                        response_time = (time.time() - start_time) * 1000
                        server_instance.metrics_collector.record_response_time(response_time)
                        return
                
                self._send_error(404, f"Session {session_id} not found")
            
            # Unknown endpoint
            else:
                self._send_error(404, f"Endpoint {endpoint} not found")
            
        except Exception as e:
            logger.error(f"Error handling GET request: {e}")
            self._send_error(500, str(e))
        
        # Record response time if server instance is available
        if hasattr(self.server, 'server_instance'):
            response_time = (time.time() - start_time) * 1000
            self.server.server_instance.metrics_collector.record_response_time(response_time)
    
    def do_POST(self):
        """Handle POST requests."""
        # Record the start time for metrics
        start_time = time.time()
        
        endpoint, params = self._parse_path()
        data = self._parse_json_body()
        
        if data is None:
            self._send_error(400, "Invalid JSON body")
            return
        
        try:
            # Get server instance to access session manager
            server_instance = self.server.server_instance if hasattr(self.server, 'server_instance') else None
            
            if not server_instance:
                self._send_error(500, "Server instance not available")
                return
            
            session_manager = server_instance.session_manager
            
            # Create a new session
            if endpoint == '/api/session/create':
                module_id = data.get('module_id')
                if not module_id:
                    self._send_error(400, "module_id is required")
                    return
                
                try:
                    # Create session using session manager
                    session_id, module, state = session_manager.create_session(module_id)
                    
                    self._send_response(200, {
                        'session_id': session_id,
                        'module_id': module_id,
                        'state': state
                    })
                except ValueError as e:
                    self._send_error(400, str(e))
            
            # Process input for a session
            elif endpoint.startswith('/api/session/') and endpoint.endswith('/input'):
                session_id = endpoint.split('/')[-2]
                module = session_manager.get_session(session_id)
                
                if module:
                    # Process click input
                    x = data.get('x')
                    y = data.get('y')
                    if x is not None and y is not None:
                        result = module.handle_click(x, y)
                        state = module.get_state()
                        
                        # Update cache
                        session_manager.update_cache(session_id, state)
                        
                        # Update last activity time
                        if hasattr(module, '__dict__'):
                            module.last_activity = time.time()
                        
                        self._send_response(200, {
                            'session_id': session_id,
                            'result': result,
                            'state': state
                        })
                    else:
                        self._send_error(400, "x and y coordinates are required")
                else:
                    self._send_error(404, f"Session {session_id} not found")
            
            # End a session
            elif endpoint.startswith('/api/session/') and endpoint.endswith('/end'):
                session_id = endpoint.split('/')[-2]
                if session_manager.end_session(session_id):
                    self._send_response(200, {
                        'session_id': session_id,
                        'status': 'ended'
                    })
                else:
                    self._send_error(404, f"Session {session_id} not found")
            
            # Unknown endpoint
            else:
                self._send_error(404, f"Endpoint {endpoint} not found")
        
        except Exception as e:
            logger.error(f"Error handling POST request: {e}")
            self._send_error(500, str(e))
        
        # Record response time if server instance is available
        if hasattr(self.server, 'server_instance'):
            response_time = (time.time() - start_time) * 1000
            self.server.server_instance.metrics_collector.record_response_time(response_time)


class SimpleServer(BaseServer):
    """Simple HTTP server implementation for MetaMindIQTrain.
    
    This class provides a simple, reliable HTTP server for the MetaMindIQTrain platform.
    It uses the standard library's http.server with minimal dependencies.
    """
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8080, debug: bool = False):
        """Initialize the simple server.
        
        Args:
            host: Host address to bind to
            port: Port to listen on
            debug: Enable debug mode
        """
        super().__init__(host, port, debug)
        self.server = None
    
    def start(self):
        """Start the server."""
        # Call parent implementation first
        super().start()
        
        try:
            # Create server with our handler
            self.server = socketserver.ThreadingTCPServer((self.host, self.port), SimpleRequestHandler)
            
            # Store a reference to the server instance for the handler to access
            self.server.server_instance = self
            
            # Configure the server
            self.server.daemon_threads = True
            
            # Start serving
            logger.info(f"Simple server running on {self.host}:{self.port}")
            logger.info("Press Ctrl+C to stop the server")
            
            # Serve forever
            self.server.serve_forever()
            
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            self.stop()
    
    def stop(self):
        """Stop the server."""
        # Call parent implementation first
        super().stop()
        
        if self.server:
            self.server.server_close()
            self.server = None


def run_server(host: str = '0.0.0.0', port: int = 8080, debug: bool = False) -> int:
    """Run the simple server.
    
    Args:
        host: Host address to bind to
        port: Port to listen on
        debug: Enable debug mode
        
    Returns:
        0 on success, non-zero on error
    """
    try:
        server = SimpleServer(host, port, debug)
        server.start()
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run the simple MetaMindIQTrain server')
    parser.add_argument('--host', default='0.0.0.0', help='Host address to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    sys.exit(run_server(host=args.host, port=args.port, debug=args.debug)) 