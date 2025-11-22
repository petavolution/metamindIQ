#!/usr/bin/env python3
"""
Optimized HTTP Server for MetaMindIQTrain

This is an optimized server implementation for the MetaMindIQTrain platform.
It provides both HTTP REST APIs and WebSocket connections for real-time updates,
with performance optimizations and advanced features.
"""

import http.server
import socketserver
import json
import logging
import threading
import time
import sys
import socket
import traceback
import argparse
import os
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
from wsgiref.simple_server import make_server
import multiprocessing
import uuid

# Configure relative imports
current_dir = Path(__file__).resolve().parent.parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import the base server
from MetaMindIQTrain.server.base.base_server import BaseServer
from MetaMindIQTrain.module_registry import get_available_modules, create_module_instance

# Try to import WebSocket support
try:
    import socketio
    HAS_SOCKETIO = True
except ImportError:
    HAS_SOCKETIO = False
    logging.warning("Socket.IO not available. Only HTTP API will be enabled.")

# Try to import Flask for advanced features
try:
    from flask import Flask, request, jsonify, send_from_directory
    from werkzeug.serving import run_simple
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False
    logging.warning("Flask not available. Using basic HTTP server instead.")

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Socket.IO server if available
if HAS_SOCKETIO:
    sio = socketio.Server(cors_allowed_origins='*', async_mode='threading')

# HTTP request handler with optimizations
class OptimizedRequestHandler(http.server.BaseHTTPRequestHandler):
    """Optimized HTTP request handler with caching and performance improvements."""
    
    # Class-level cache of common responses
    static_responses = {}
    
    def _send_response(self, status_code, data, cache_control=None):
        """Send a JSON response.
        
        Args:
            status_code: HTTP status code
            data: Response data to be JSON-encoded
            cache_control: Optional cache control header value
        """
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        if cache_control:
            self.send_header('Cache-Control', cache_control)
        
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
        # Use cached response if available
        if 'OPTIONS' in self.static_responses:
            response = self.static_responses['OPTIONS']
            self.wfile.write(response)
            return
        
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Cache this response for future use
        self.static_responses['OPTIONS'] = b''
    
    def do_GET(self):
        """Handle GET requests."""
        start_time = time.time()
        endpoint, params = self._parse_path()
        
        # Get server instance
        server_instance = self.server.server_instance if hasattr(self.server, 'server_instance') else None
        
        if not server_instance:
            self._send_error(500, "Server instance not available")
            return
        
        session_manager = server_instance.session_manager
        metrics_collector = server_instance.metrics_collector
        
        try:
            # Health check endpoint
            if endpoint == '/api/health':
                # Get metrics from collector
                metrics = metrics_collector.get_all_metrics()
                metrics['active_sessions'] = server_instance.get_active_sessions_count()
                metrics['status'] = 'ok'
                
                self._send_response(200, metrics, cache_control='no-cache')
            
            # List available modules
            elif endpoint == '/api/modules':
                # This rarely changes, so cache the response
                if 'modules' in self.static_responses:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Cache-Control', 'max-age=3600')
                    self.end_headers()
                    self.wfile.write(self.static_responses['modules'])
                    metrics_collector.record_request()
                else:
                    modules = get_available_modules()
                    response_data = {
                        'modules': modules
                    }
                    response_json = json.dumps(response_data).encode('utf-8')
                    
                    # Cache this response
                    self.static_responses['modules'] = response_json
                    
                    self._send_response(200, response_data, cache_control='max-age=3600')
            
            # Get session state
            elif endpoint.startswith('/api/session/'):
                session_id = endpoint.split('/')[-1]
                module = session_manager.get_session(session_id)
                
                if module:
                    # Check cache first
                    cached_state = session_manager.get_cached_state(session_id)
                    if cached_state:
                        self._send_response(200, {
                            'session_id': session_id,
                            'state': cached_state,
                            'cached': True
                        }, cache_control='max-age=1')
                    else:
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
                else:
                    self._send_error(404, f"Session {session_id} not found")
            
            # Unknown endpoint
            else:
                self._send_error(404, f"Endpoint {endpoint} not found")
            
            # Record response time
            response_time = (time.time() - start_time) * 1000
            metrics_collector.record_response_time(response_time)
        
        except Exception as e:
            logger.error(f"Error handling GET request: {e}")
            self._send_error(500, str(e))
            metrics_collector.record_error()
    
    def do_POST(self):
        """Handle POST requests."""
        start_time = time.time()
        endpoint, params = self._parse_path()
        data = self._parse_json_body()
        
        # Get server instance
        server_instance = self.server.server_instance if hasattr(self.server, 'server_instance') else None
        
        if not server_instance:
            self._send_error(500, "Server instance not available")
            return
        
        session_manager = server_instance.session_manager
        metrics_collector = server_instance.metrics_collector
        
        if data is None:
            self._send_error(400, "Invalid JSON body")
            return
        
        try:
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
            
            # Record response time
            response_time = (time.time() - start_time) * 1000
            metrics_collector.record_response_time(response_time)
        
        except Exception as e:
            logger.error(f"Error handling POST request: {e}")
            self._send_error(500, str(e))
            metrics_collector.record_error()


# WebSocket event handlers
if HAS_SOCKETIO:
    @sio.event
    def connect(sid, environ):
        """Handle client connection."""
        logger.info(f"Client connected: {sid}")
        
        # Initialize client data
        if hasattr(sio, 'server_instance'):
            # Initialize client-session mapping if not exists
            if not hasattr(sio, 'clients'):
                sio.clients = {}
            
            sio.clients[sid] = None  # No session assigned yet
    
    @sio.event
    def disconnect(sid):
        """Handle client disconnection."""
        logger.info(f"Client disconnected: {sid}")
        
        # Remove from clients mapping
        if hasattr(sio, 'clients') and sid in sio.clients:
            session_id = sio.clients[sid]
            if session_id:
                logger.info(f"Client {sid} was connected to session {session_id}")
                # Don't end the session here to allow reconnection
            del sio.clients[sid]
    
    @sio.event
    def get_available_modules(sid, data=None):
        """Get available training modules."""
        # Record websocket event
        if hasattr(sio, 'server_instance'):
            sio.server_instance.metrics_collector.record_websocket_event()
            
        # Get modules from the registry
        modules = get_available_modules()
        return {'modules': modules}
    
    @sio.event
    def create_session(sid, data):
        """Create a new session."""
        client_id = sid
        
        # Parse request data
        module_id = data.get('module_id')
        parameters = data.get('parameters', {})
        
        if not module_id:
            return {
                'error': 'module_id is required'
            }
        
        logger.info(f"Creating session for module {module_id}")
        
        try:
            # Create session ID
            session_id = str(uuid.uuid4())
            
            # Create module instance - no extra parameters
            try:
                module = create_module_instance(module_id)
            except Exception as e:
                logger.error(f"Error creating module: {e}")
                return {
                    'error': f"Error creating module: {e}"
                }
            
            if not module:
                logger.error(f"Failed to create module {module_id}")
                return {
                    'error': f"Failed to create module {module_id}"
                }
            
            # Store session data
            session_manager = sio.server_instance.session_manager
            session_manager.create_session(session_id, module, client_id)
            
            # Add client to session
            if hasattr(sio, 'clients'):
                sio.clients[client_id] = session_id
            
            logger.info(f"Created session {session_id} for module {module_id}")
            
            # Return session data
            return {
                'session_id': session_id,
                'module_id': module_id,
                'state': module.get_state()
            }
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return {
                'error': f"Error creating session: {e}"
            }
    
    @sio.event
    def get_state(sid, data):
        """Get the current state of a session."""
        # Record websocket event
        if not hasattr(sio, 'server_instance'):
            return {'error': 'Server instance not available'}
        
        sio.server_instance.metrics_collector.record_websocket_event()
        
        try:
            session_id = data.get('session_id')
            if not session_id:
                sio.server_instance.metrics_collector.record_error()
                return {'error': 'session_id is required'}
            
            session_manager = sio.server_instance.session_manager
            
            # Check cache first
            cached_state = session_manager.get_cached_state(session_id)
            if cached_state:
                return {
                    'session_id': session_id,
                    'state': cached_state,
                    'cached': True
                }
            
            # Get from session manager
            module = session_manager.get_session(session_id)
            if module:
                state = module.get_state()
                
                # Update cache
                session_manager.update_cache(session_id, state)
                
                # Update last activity time
                if hasattr(module, '__dict__'):
                    module.last_activity = time.time()
                
                return {
                    'session_id': session_id,
                    'state': state
                }
            else:
                sio.server_instance.metrics_collector.record_error()
                return {'error': f"Session {session_id} not found"}
        except Exception as e:
            logger.error(f"Error getting state: {e}")
            sio.server_instance.metrics_collector.record_error()
            return {'error': str(e)}
    
    @sio.event
    def process_input(sid, data):
        """Process input for a session."""
        start_time = time.time()
        
        # Record websocket event
        if not hasattr(sio, 'server_instance'):
            return {'error': 'Server instance not available'}
        
        sio.server_instance.metrics_collector.record_websocket_event()
        
        try:
            session_id = data.get('session_id')
            if not session_id:
                sio.server_instance.metrics_collector.record_error()
                return {'error': 'session_id is required'}
            
            x = data.get('x')
            y = data.get('y')
            if x is None or y is None:
                sio.server_instance.metrics_collector.record_error()
                return {'error': 'x and y coordinates are required'}
            
            session_manager = sio.server_instance.session_manager
            module = session_manager.get_session(session_id)
            
            if module:
                # Process the click
                result = module.handle_click(x, y)
                
                # Get updated state
                state = module.get_state()
                
                # Update cache
                session_manager.update_cache(session_id, state)
                
                # Update last activity time
                if hasattr(module, '__dict__'):
                    module.last_activity = time.time()
                
                # Record response time
                response_time = (time.time() - start_time) * 1000
                sio.server_instance.metrics_collector.record_response_time(response_time)
                
                return {
                    'session_id': session_id,
                    'result': result,
                    'state': state
                }
            else:
                sio.server_instance.metrics_collector.record_error()
                return {'error': f"Session {session_id} not found"}
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            sio.server_instance.metrics_collector.record_error()
            return {'error': str(e)}
    
    @sio.event
    def end_session(sid, data):
        """End a training session."""
        # Record websocket event
        if not hasattr(sio, 'server_instance'):
            return {'error': 'Server instance not available'}
        
        sio.server_instance.metrics_collector.record_websocket_event()
        
        try:
            session_id = data.get('session_id')
            if not session_id:
                sio.server_instance.metrics_collector.record_error()
                return {'error': 'session_id is required'}
            
            session_manager = sio.server_instance.session_manager
            
            if session_manager.end_session(session_id):
                # If the client is associated with this session, remove the association
                if hasattr(sio, 'clients') and sid in sio.clients and sio.clients[sid] == session_id:
                    sio.clients[sid] = None
                
                return {
                    'session_id': session_id,
                    'status': 'ended'
                }
            else:
                sio.server_instance.metrics_collector.record_error()
                return {'error': f"Session {session_id} not found"}
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            sio.server_instance.metrics_collector.record_error()
            return {'error': str(e)}


# Flask routes (if Flask is available)
if HAS_FLASK:
    app = Flask(__name__)
    
    # Add reference to the server instance
    app.server_instance = None
    
    @app.route('/api/health')
    def health_check():
        """Check server health."""
        # Get server instance
        server_instance = app.server_instance
        
        if not server_instance:
            return jsonify({'error': 'Server instance not available'}), 500
        
        # Get metrics from collector
        metrics = server_instance.metrics_collector.get_all_metrics()
        metrics['active_sessions'] = server_instance.get_active_sessions_count()
        metrics['status'] = 'ok'
        
        return jsonify(metrics)
    
    @app.route('/api/modules')
    def get_modules():
        """Get available modules."""
        # Record request
        if app.server_instance:
            app.server_instance.metrics_collector.record_request()
            
        # Get modules from the registry
        modules = get_available_modules()
        return jsonify({
            'modules': modules
        })
    
    @app.route('/api/session/create', methods=['POST'])
    def create_session():
        """Create a new training session."""
        start_time = time.time()
        
        # Get server instance
        server_instance = app.server_instance
        
        if not server_instance:
            return jsonify({'error': 'Server instance not available'}), 500
        
        # Record request
        server_instance.metrics_collector.record_request()
        
        try:
            data = request.get_json()
            
            # Parse request data
            module_id = data.get('module_id')
            parameters = data.get('parameters', {})
            
            if not module_id:
                server_instance.metrics_collector.record_error()
                return jsonify({'error': 'module_id is required'}), 400
            
            logger.info(f"Creating session for module {module_id}")
            
            # Create session ID
            session_id = str(uuid.uuid4())
            
            # Create module instance - no extra parameters
            try:
                module = create_module_instance(module_id)
            except Exception as e:
                logger.error(f"Error creating module: {e}")
                server_instance.metrics_collector.record_error()
                return jsonify({'error': f"Error creating module: {e}"}), 500
            
            if not module:
                logger.error(f"Failed to create module {module_id}")
                return jsonify({'error': f"Failed to create module {module_id}"}), 400
            
            # Store session data
            session_manager = server_instance.session_manager
            session_manager.create_session(session_id, module, request.remote_addr)
            
            logger.info(f"Created session {session_id} for module {module_id}")
            
            # Record response time
            if server_instance:
                response_time = (time.time() - start_time) * 1000
                server_instance.metrics_collector.record_response_time(response_time)
            
            # Return session data
            return jsonify({
                'session_id': session_id,
                'module_id': module_id,
                'state': module.get_state()
            })
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/session/<session_id>')
    def get_session_state(session_id):
        """Get the state of a session."""
        # Get server instance
        server_instance = app.server_instance
        
        if not server_instance:
            return jsonify({'error': 'Server instance not available'}), 500
        
        # Record request
        server_instance.metrics_collector.record_request()
        
        session_manager = server_instance.session_manager
        
        # Check cache first
        cached_state = session_manager.get_cached_state(session_id)
        if cached_state:
            response = jsonify({
                'session_id': session_id,
                'state': cached_state,
                'cached': True
            })
            response.headers['Cache-Control'] = 'max-age=1'
            return response
        
        # Get from session manager
        module = session_manager.get_session(session_id)
        if module:
            state = module.get_state()
            
            # Update cache
            session_manager.update_cache(session_id, state)
            
            # Update last activity time
            if hasattr(module, '__dict__'):
                module.last_activity = time.time()
            
            return jsonify({
                'session_id': session_id,
                'state': state
            })
        else:
            server_instance.metrics_collector.record_error()
            return jsonify({'error': f"Session {session_id} not found"}), 404
    
    @app.route('/api/session/<session_id>/input', methods=['POST'])
    def process_input(session_id):
        """Process input for a session."""
        start_time = time.time()
        
        # Get server instance
        server_instance = app.server_instance
        
        if not server_instance:
            return jsonify({'error': 'Server instance not available'}), 500
        
        # Record request
        server_instance.metrics_collector.record_request()
        
        try:
            data = request.get_json()
            x = data.get('x')
            y = data.get('y')
            if x is None or y is None:
                server_instance.metrics_collector.record_error()
                return jsonify({'error': 'x and y coordinates are required'}), 400
            
            session_manager = server_instance.session_manager
            module = session_manager.get_session(session_id)
            
            if module:
                # Process the click
                result = module.handle_click(x, y)
                
                # Get updated state
                state = module.get_state()
                
                # Update cache
                session_manager.update_cache(session_id, state)
                
                # Update last activity time
                if hasattr(module, '__dict__'):
                    module.last_activity = time.time()
                
                # Record response time
                response_time = (time.time() - start_time) * 1000
                server_instance.metrics_collector.record_response_time(response_time)
                
                return jsonify({
                    'session_id': session_id,
                    'result': result,
                    'state': state
                })
            else:
                server_instance.metrics_collector.record_error()
                return jsonify({'error': f"Session {session_id} not found"}), 404
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            server_instance.metrics_collector.record_error()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/session/<session_id>/end', methods=['POST'])
    def end_session(session_id):
        """End a session."""
        # Get server instance
        server_instance = app.server_instance
        
        if not server_instance:
            return jsonify({'error': 'Server instance not available'}), 500
        
        # Record request
        server_instance.metrics_collector.record_request()
        
        session_manager = server_instance.session_manager
        
        if session_manager.end_session(session_id):
            return jsonify({
                'session_id': session_id,
                'status': 'ended'
            })
        else:
            server_instance.metrics_collector.record_error()
            return jsonify({'error': f"Session {session_id} not found"}), 404


class OptimizedServer(BaseServer):
    """Optimized server implementation for MetaMindIQTrain.
    
    This class provides an optimized server for the MetaMindIQTrain platform.
    It supports both HTTP and WebSocket connections, and includes advanced
    features like caching and performance optimizations.
    """
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8080, debug: bool = False,
                 use_flask: bool = True, use_websocket: bool = True):
        """Initialize the optimized server.
        
        Args:
            host: Host address to bind to
            port: Port to listen on
            debug: Enable debug mode
            use_flask: Use Flask if available
            use_websocket: Use WebSocket if available
        """
        super().__init__(host, port, debug)
        
        self.use_flask = use_flask and HAS_FLASK
        self.use_websocket = use_websocket and HAS_SOCKETIO
        
        self.server = None
        self.socket_server = None
        self.flask_app = None
        
        # Create Socket.IO app
        if self.use_websocket:
            # Provide a reference to this server instance
            sio.server_instance = self
            if not hasattr(sio, 'clients'):
                sio.clients = {}
    
    def start(self):
        """Start the server."""
        # Call parent implementation first
        super().start()
        
        try:
            # Use Flask if available and requested
            if self.use_flask:
                logger.info("Using Flask server implementation")
                
                # Create Flask app
                self.flask_app = app
                self.flask_app.server_instance = self
                
                # Use WebSocket if available and requested
                if self.use_websocket:
                    logger.info("WebSocket support enabled")
                    # Create Socket.IO WSGI app
                    socket_app = socketio.WSGIApp(sio, app)
                    
                    logger.info(f"Starting server on {self.host}:{self.port}")
                    logger.info("Press Ctrl+C to stop the server")
                    
                    # Run with Werkzeug server
                    run_simple(self.host, self.port, socket_app, use_reloader=False, threaded=True)
                else:
                    logger.info("WebSocket support disabled")
                    logger.info(f"Starting server on {self.host}:{self.port}")
                    logger.info("Press Ctrl+C to stop the server")
                    
                    # Run with Werkzeug server
                    app.run(host=self.host, port=self.port, debug=self.debug, threaded=True)
            else:
                logger.info("Using standard HTTP server implementation")
                
                # Create server with optimized handler
                self.server = socketserver.ThreadingTCPServer((self.host, self.port), OptimizedRequestHandler)
                self.server.daemon_threads = True
                self.server.server_instance = self
                
                # Use WebSocket if available and requested
                if self.use_websocket:
                    logger.info("WebSocket support enabled via separate thread")
                    
                    # Run Socket.IO in a separate thread
                    sio_app = socketio.WSGIApp(sio)
                    self.socket_server = make_server(self.host, self.port + 1, sio_app)
                    
                    sio_thread = threading.Thread(target=self.socket_server.serve_forever)
                    sio_thread.daemon = True
                    sio_thread.start()
                    
                    logger.info(f"WebSocket server running on {self.host}:{self.port+1}")
                
                logger.info(f"Starting server on {self.host}:{self.port}")
                logger.info("Press Ctrl+C to stop the server")
                
                # Serve forever
                self.server.serve_forever()
        
        except KeyboardInterrupt:
            logger.info("Server shutting down due to keyboard interrupt...")
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
        
        if self.socket_server:
            self.socket_server.shutdown()
            self.socket_server = None


def run_server(host='0.0.0.0', port=8080, debug=False, use_flask=True, use_websocket=True):
    """Run the optimized server.
    
    Args:
        host: Host address to bind to
        port: Port to listen on
        debug: Enable debug mode
        use_flask: Use Flask if available
        use_websocket: Use WebSocket if available
        
    Returns:
        0 on success, non-zero on error
    """
    try:
        server = OptimizedServer(
            host=host,
            port=port,
            debug=debug,
            use_flask=use_flask,
            use_websocket=use_websocket
        )
        server.start()
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}")
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the MetaMindIQTrain optimized server')
    parser.add_argument('--host', default='0.0.0.0', help='Host address to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-flask', action='store_true', help='Do not use Flask even if available')
    parser.add_argument('--no-websocket', action='store_true', help='Do not use WebSocket even if available')
    
    args = parser.parse_args()
    
    sys.exit(run_server(
        host=args.host,
        port=args.port,
        debug=args.debug,
        use_flask=not args.no_flask,
        use_websocket=not args.no_websocket
    )) 