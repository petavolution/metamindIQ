#!/usr/bin/env python3
"""
Optimized Server for MetaMindIQTrain.

This module provides an optimized server implementation that uses
the module provider to serve module information and layouts efficiently.
It handles client requests for module information, session management,
and state updates.
"""

import os
import sys
import time
import uuid
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

try:
    import socketio
    import eventlet
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    HAS_SOCKETIO = True
except ImportError:
    HAS_SOCKETIO = False
    
from MetaMindIQTrain.module_registry import (
    get_available_modules, get_module_info, create_module_instance
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MetaMindServer:
    """Optimized server for MetaMindIQTrain."""
    
    def __init__(self, host='0.0.0.0', port=5000, debug=False):
        """Initialize the server.
        
        Args:
            host: Host to bind to
            port: Port to listen on
            debug: Whether to run in debug mode
        """
        self.host = host
        self.port = port
        self.debug = debug
        
        # Create Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Configure SocketIO (if available)
        if HAS_SOCKETIO:
            self.sio = socketio.Server(
                cors_allowed_origins='*',
                async_mode='eventlet'
            )
            self.app = socketio.WSGIApp(self.sio, self.app)
            self._setup_socketio_events()
        else:
            self.sio = None
            logger.warning("SocketIO is not available. Using Flask only.")
            
        # Set up Flask routes
        self._setup_routes()
        
        # Active sessions
        self.sessions = {}
        
        # Connected clients
        self.clients = {}
        
        # Periodic task for session updates
        self.update_interval = 0.05  # 50ms updates
        self.last_update_time = time.time()
        
        logger.info(f"Initialized MetaMindServer on {host}:{port} (debug={debug})")
        
    def _setup_routes(self):
        """Set up Flask routes."""
        @self.app.route('/api/modules', methods=['GET'])
        def get_modules():
            """Return list of available modules."""
            modules = get_available_modules()
            return jsonify({'modules': modules})
            
        @self.app.route('/api/module/<module_id>', methods=['GET'])
        def get_module(module_id):
            """Return module information."""
            module_info = get_module_info(module_id)
            if module_info:
                return jsonify({'module': module_info})
            else:
                return jsonify({'error': f'Module {module_id} not found'}), 404
                
        @self.app.route('/api/session/create', methods=['POST'])
        def create_session():
            """Create a new session."""
            data = request.json
            
            if not data or 'module_id' not in data:
                return jsonify({'error': 'Missing module_id in request'}), 400
                
            module_id = data['module_id']
            user_id = data.get('user_id', 'anonymous')
            client_id = data.get('client_id', str(uuid.uuid4()))
            parameters = data.get('parameters', {})
            
            try:
                # Create session ID
                session_id = str(uuid.uuid4())
                
                # Create module instance
                module = create_module_instance(module_id, session_id=session_id)
                if not module:
                    return jsonify({'error': f'Failed to create module {module_id}'}), 500
                
                # Store session
                self.sessions[session_id] = {
                    'module': module,
                    'clients': set([client_id]),
                    'created_time': time.time(),
                    'last_activity': time.time()
                }
                
                # Get initial state
                initial_state = module.get_state()
                
                # Create or update client record
                self.clients[client_id] = {
                    'session_id': session_id,
                    'user_id': user_id,
                    'last_activity': time.time()
                }
                
                return jsonify({
                    'session_id': session_id,
                    'client_id': client_id,
                    'initial_state': initial_state
                })
                
            except Exception as e:
                logger.error(f"Error creating session: {e}")
                return jsonify({'error': f'Internal server error: {str(e)}'}), 500
                
        @self.app.route('/api/session/<session_id>', methods=['GET'])
        def get_session(session_id):
            """Get session state."""
            if session_id not in self.sessions:
                return jsonify({'error': f'Session {session_id} not found'}), 404
                
            try:
                # Get module from session
                module = self.sessions[session_id]['module']
                
                # Update last activity
                self.sessions[session_id]['last_activity'] = time.time()
                
                # Get current state
                state = module.get_state()
                
                return jsonify({'state': state})
                
            except Exception as e:
                logger.error(f"Error getting session state: {e}")
                return jsonify({'error': f'Internal server error: {str(e)}'}), 500
                
        @self.app.route('/api/session/<session_id>/input', methods=['POST'])
        def handle_input(session_id):
            """Handle user input."""
            if session_id not in self.sessions:
                return jsonify({'error': f'Session {session_id} not found'}), 404
                
            data = request.json
            if not data:
                return jsonify({'error': 'Missing input data'}), 400
                
            try:
                # Get module from session
                module = self.sessions[session_id]['module']
                
                # Update last activity
                self.sessions[session_id]['last_activity'] = time.time()
                
                # Handle input
                # For click events
                if 'click' in data:
                    x, y = data['click']
                    result = module.handle_click(x, y)
                else:
                    # Unknown input type
                    return jsonify({'error': 'Unknown input type'}), 400
                
                # Get updated state
                state = module.get_state()
                
                return jsonify({
                    'result': result,
                    'state': state
                })
                
            except Exception as e:
                logger.error(f"Error handling input: {e}")
                return jsonify({'error': f'Internal server error: {str(e)}'}), 500
                
        @self.app.route('/api/session/<session_id>/end', methods=['POST'])
        def end_session(session_id):
            """End a session."""
            if session_id not in self.sessions:
                return jsonify({'error': f'Session {session_id} not found'}), 404
                
            try:
                # Remove session
                del self.sessions[session_id]
                
                # Update client records
                for client_id, client in list(self.clients.items()):
                    if client.get('session_id') == session_id:
                        self.clients[client_id]['session_id'] = None
                
                return jsonify({'success': True})
                
            except Exception as e:
                logger.error(f"Error ending session: {e}")
                return jsonify({'error': f'Internal server error: {str(e)}'}), 500
            
    def _setup_socketio_events(self):
        """Set up SocketIO events."""
        if not self.sio:
            return
            
        @self.sio.event
        def connect(sid, environ):
            """Handle client connection."""
            logger.info(f"Client connected: {sid}")
            self.clients[sid] = {
                'session_id': None,
                'user_id': 'anonymous',
                'last_activity': time.time()
            }
            
        @self.sio.event
        def disconnect(sid):
            """Handle client disconnection."""
            logger.info(f"Client disconnected: {sid}")
            
            # Check if client is in a session
            client = self.clients.get(sid)
            if client and client.get('session_id'):
                session_id = client['session_id']
                if session_id in self.sessions:
                    # Remove client from session
                    self.sessions[session_id]['clients'].discard(sid)
                    
                    # If session has no clients, remove it after a delay
                    if not self.sessions[session_id]['clients']:
                        # We'll keep orphaned sessions around for reconnection
                        # The cleanup task will remove them after a timeout
                        logger.info(f"Session {session_id} has no clients. Marking for cleanup.")
                        self.sessions[session_id]['orphaned'] = True
                        self.sessions[session_id]['orphaned_time'] = time.time()
            
            # Remove client
            if sid in self.clients:
                del self.clients[sid]
                
        @self.sio.event
        def get_modules(sid, data=None):
            """Return list of available modules."""
            modules = get_available_modules()
            self.sio.emit('modules', {'modules': modules}, room=sid)
            
        @self.sio.event
        def create_session(sid, data):
            """Create a new session."""
            if not data or 'module_id' not in data:
                self.sio.emit('error', {'message': 'Missing module_id in request'}, room=sid)
                return
                
            module_id = data['module_id']
            user_id = data.get('user_id', 'anonymous')
            parameters = data.get('parameters', {})
            
            try:
                # Create session ID
                session_id = str(uuid.uuid4())
                
                # Create module instance
                module = create_module_instance(module_id, session_id=session_id)
                if not module:
                    self.sio.emit('error', {
                        'message': f'Failed to create module {module_id}'
                    }, room=sid)
                    return
                
                # Store session
                self.sessions[session_id] = {
                    'module': module,
                    'clients': set([sid]),
                    'created_time': time.time(),
                    'last_activity': time.time()
                }
                
                # Update client record
                self.clients[sid]['session_id'] = session_id
                self.clients[sid]['user_id'] = user_id
                self.clients[sid]['last_activity'] = time.time()
                
                # Get initial state
                initial_state = module.get_state()
                
                # Send session created event
                self.sio.emit('session_created', {
                    'session_id': session_id,
                    'module_id': module_id,
                    'initial_state': initial_state
                }, room=sid)
                
                logger.info(f"Created session {session_id} for client {sid}")
                
            except Exception as e:
                logger.error(f"Error creating session: {e}")
                self.sio.emit('error', {
                    'message': f'Internal server error: {str(e)}'
                }, room=sid)
                
        @self.sio.event
        def handle_input(sid, data):
            """Handle user input."""
            # Get client session
            client = self.clients.get(sid)
            if not client or not client.get('session_id'):
                self.sio.emit('error', {
                    'message': 'Not in a session'
                }, room=sid)
                return
                
            session_id = client['session_id']
            if session_id not in self.sessions:
                self.sio.emit('error', {
                    'message': f'Session {session_id} not found'
                }, room=sid)
                return
                
            if not data:
                self.sio.emit('error', {
                    'message': 'Missing input data'
                }, room=sid)
                return
                
            try:
                # Get module from session
                module = self.sessions[session_id]['module']
                
                # Update last activity
                self.sessions[session_id]['last_activity'] = time.time()
                
                # Handle input
                # For click events
                if 'click' in data:
                    x, y = data['click']
                    result = module.handle_click(x, y)
                else:
                    # Unknown input type
                    self.sio.emit('error', {
                        'message': 'Unknown input type'
                    }, room=sid)
                    return
                
                # Get updated state
                state = module.get_state()
                
                # Send update to all clients in session
                for client_sid in self.sessions[session_id]['clients']:
                    self.sio.emit('state_update', {
                        'state': state,
                        'result': result
                    }, room=client_sid)
                
            except Exception as e:
                logger.error(f"Error handling input: {e}")
                self.sio.emit('error', {
                    'message': f'Internal server error: {str(e)}'
                }, room=sid)
                
        @self.sio.event
        def end_session(sid):
            """End a session."""
            # Get client session
            client = self.clients.get(sid)
            if not client or not client.get('session_id'):
                self.sio.emit('error', {
                    'message': 'Not in a session'
                }, room=sid)
                return
                
            session_id = client['session_id']
            if session_id not in self.sessions:
                self.sio.emit('error', {
                    'message': f'Session {session_id} not found'
                }, room=sid)
                return
                
            try:
                # Notify all clients in session
                for client_sid in self.sessions[session_id]['clients']:
                    self.sio.emit('session_ended', {
                        'session_id': session_id
                    }, room=client_sid)
                    
                    # Update client record
                    if client_sid in self.clients:
                        self.clients[client_sid]['session_id'] = None
                
                # Remove session
                del self.sessions[session_id]
                
                logger.info(f"Ended session {session_id}")
                
            except Exception as e:
                logger.error(f"Error ending session: {e}")
                self.sio.emit('error', {
                    'message': f'Internal server error: {str(e)}'
                }, room=sid)
    
    def run(self):
        """Run the server."""
        if HAS_SOCKETIO:
            # Use eventlet server with WebSocket support
            eventlet.monkey_patch()
            
            # Start background task for periodic updates
            eventlet.spawn(self._update_task)
            
            # Run server
            eventlet.wsgi.server(
                eventlet.listen((self.host, self.port)),
                self.app,
                debug=self.debug
            )
        else:
            # Use standard Flask server (no WebSocket support)
            self.app.run(
                host=self.host,
                port=self.port,
                debug=self.debug
            )
    
    def _update_task(self):
        """Background task for periodic updates."""
        while True:
            try:
                current_time = time.time()
                dt = current_time - self.last_update_time
                self.last_update_time = current_time
                
                # Update active modules
                self._update_modules(dt)
                
                # Clean up orphaned sessions
                self._cleanup_sessions()
                
            except Exception as e:
                logger.error(f"Error in update task: {e}")
                
            # Sleep until next update
            eventlet.sleep(self.update_interval)
    
    def _update_modules(self, dt):
        """Update active modules.
        
        Args:
            dt: Time delta since last update.
        """
        for session_id, session in list(self.sessions.items()):
            module = session['module']
            
            # Skip orphaned sessions
            if session.get('orphaned', False):
                continue
                
            # Skip inactive sessions
            if current_time - session['last_activity'] > 60:  # 60s timeout
                continue
                
            try:
                # Update module
                if hasattr(module, 'update'):
                    module.update(dt)
                    
                    # Check if state has changed
                    prev_state = session.get('last_state')
                    current_state = module.get_state()
                    
                    # Simple change detection (we could use more sophisticated delta encoding)
                    if prev_state != current_state:
                        # Store new state
                        session['last_state'] = current_state
                        
                        # Send update to all clients in session
                        for client_sid in session['clients']:
                            self.sio.emit('state_update', {
                                'state': current_state
                            }, room=client_sid)
                            
            except Exception as e:
                logger.error(f"Error updating module {session_id}: {e}")
    
    def _cleanup_sessions(self):
        """Clean up orphaned sessions."""
        current_time = time.time()
        
        # Remove orphaned sessions after timeout
        for session_id, session in list(self.sessions.items()):
            if session.get('orphaned', False):
                if current_time - session['orphaned_time'] > 300:  # 5 minute timeout
                    logger.info(f"Removing orphaned session {session_id}")
                    del self.sessions[session_id]


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run the MetaMindIQTrain server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    server = MetaMindServer(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
    
    server.run()


if __name__ == '__main__':
    main() 