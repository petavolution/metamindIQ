"""
Flask Server Application

This module provides a simplified server application for the MetaMindIQTrain platform.
It includes Flask routes and Socket.IO event handlers for the application.
"""

import logging
import time
import uuid
from typing import Dict, Any, Tuple, Optional

from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room

from core.config import load_config, AppConfig
from core.training_module import get_available_modules

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Session management
sessions = {}
clients = {}

def create_app(config: Optional[AppConfig] = None) -> Tuple[Flask, SocketIO]:
    """Create and configure the Flask application.
    
    Args:
        config: Application configuration
        
    Returns:
        Flask application and SocketIO server
    """
    global app, socketio
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration if not provided
    if config is None:
        config = load_config()
    
    # Configure app
    app.config['SECRET_KEY'] = 'secret-metamind-key'
    app.config['DEBUG'] = config.server.debug
    
    # Set up static folder
    if config.server.static_folder:
        app.static_folder = config.server.static_folder
    
    # Set up Socket.IO
    socketio = SocketIO(
        app,
        cors_allowed_origins=config.server.cors_allowed_origins,
        async_mode='eventlet'
    )
    
    # Set up routes
    setup_routes(app)
    
    # Set up Socket.IO events
    setup_socketio_events(socketio)
    
    return app, socketio

def setup_routes(app: Flask) -> None:
    """Set up Flask routes.
    
    Args:
        app: Flask application
    """
    @app.route('/')
    def index():
        """Index route."""
        return jsonify({
            'name': 'MetaMindIQTrain',
            'version': '1.0.0',
            'status': 'running'
        })
    
    @app.route('/api/health')
    def health_check():
        """Health check route."""
        return jsonify({
            'status': 'ok',
            'time': time.time(),
            'sessions': len(sessions)
        })
    
    @app.route('/api/modules')
    def get_modules():
        """Get available modules."""
        modules = get_available_modules()
        
        # Convert to list of dicts
        module_list = [
            {
                'id': module_id,
                'name': module_class.__name__,
                'description': getattr(module_class, '__doc__', '').strip()
            }
            for module_id, module_class in modules.items()
        ]
        
        return jsonify({
            'modules': module_list
        })

def setup_socketio_events(socketio: SocketIO) -> None:
    """Set up Socket.IO events.
    
    Args:
        socketio: Socket.IO server
    """
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        client_id = request.sid
        clients[client_id] = {
            'connect_time': time.time(),
            'session_id': None
        }
        
        logger.info(f"Client connected: {client_id}")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        client_id = request.sid
        
        if client_id in clients:
            # Leave session if in one
            session_id = clients[client_id].get('session_id')
            if session_id and session_id in sessions:
                leave_room(session_id)
                
                # Remove client from session
                sessions[session_id]['clients'].discard(client_id)
                
                logger.info(f"Client {client_id} left session {session_id}")
                
                # If no clients left, end the session
                if not sessions[session_id]['clients']:
                    try:
                        # End module
                        sessions[session_id]['module'].end()
                        
                        # Remove session
                        del sessions[session_id]
                        
                        logger.info(f"Session {session_id} automatically ended (no clients)")
                    except Exception as e:
                        logger.error(f"Error auto-ending session: {str(e)}")
            
            # Remove client
            del clients[client_id]
            
            logger.info(f"Client disconnected: {client_id}")
    
    @socketio.on('get_available_modules')
    def handle_get_modules(data=None):
        """Handle get available modules request."""
        modules = get_available_modules()
        
        # Convert to list of dicts
        module_list = [
            {
                'id': module_id,
                'name': module_class.__name__,
                'description': getattr(module_class, '__doc__', '').strip()
            }
            for module_id, module_class in modules.items()
        ]
        
        return module_list
    
    @socketio.on('create_session')
    def handle_create_session(data):
        """Handle create session request.
        
        Args:
            data: Request data
        """
        client_id = request.sid
        
        module_id = data.get('module_id')
        user_id = data.get('user_id', 'default_user')
        parameters = data.get('parameters', {})
        
        if not module_id:
            emit('error', {
                'message': 'module_id is required'
            })
            return
        
        # Get module class
        modules = get_available_modules()
        if module_id not in modules:
            emit('error', {
                'message': f"Module '{module_id}' not found"
            })
            return
        
        try:
            # Create session ID
            session_id = str(uuid.uuid4())
            
            # Initialize module
            module_class = modules[module_id]
            module = module_class(
                module_id=module_id,
                user_id=user_id,
                session_id=session_id,
                parameters=parameters
            )
            
            # Start module
            module.start()
            
            # Create session record
            sessions[session_id] = {
                'module': module,
                'clients': {client_id},
                'create_time': time.time()
            }
            
            # Join room for this session
            join_room(session_id)
            
            # Update client record
            clients[client_id]['session_id'] = session_id
            
            # Send session joined event
            emit('session_joined', {
                'session_id': session_id,
                'module_id': module_id,
                'user_id': user_id,
                'state': module.get_state()
            })
            
            logger.info(f"Client {client_id} created and joined session {session_id} with module {module_id}")
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            emit('error', {
                'message': f"Error creating session: {str(e)}"
            })
    
    @socketio.on('end_session')
    def handle_end_session(data=None):
        """Handle end session request."""
        client_id = request.sid
        session_id = clients.get(client_id, {}).get('session_id')
        
        if not session_id or session_id not in sessions:
            emit('error', {
                'message': 'No active session'
            })
            return
        
        try:
            # End module
            sessions[session_id]['module'].end()
            
            # Notify all clients in the session
            socketio.emit('session_ended', {
                'session_id': session_id
            }, room=session_id)
            
            # Clean up session
            for cid in sessions[session_id]['clients']:
                if cid in clients:
                    clients[cid]['session_id'] = None
            
            # Remove session
            del sessions[session_id]
            
            logger.info(f"Session {session_id} ended by client {client_id}")
        except Exception as e:
            logger.error(f"Error ending session: {str(e)}")
            emit('error', {
                'message': f"Error ending session: {str(e)}"
            })
    
    @socketio.on('process_input')
    def handle_process_input(data):
        """Handle process input request.
        
        Args:
            data: Request data
        """
        client_id = request.sid
        session_id = clients.get(client_id, {}).get('session_id')
        input_data = data.get('input', {})
        
        if not session_id or session_id not in sessions:
            emit('error', {
                'message': 'No active session'
            })
            return
        
        try:
            # Get module
            module = sessions[session_id]['module']
            
            # Process input
            result = module.process_input(input_data)
            
            # Send input result to the client
            emit('input_result', {
                'session_id': session_id,
                'result': result.get('result', {}),
                'timestamp': time.time()
            })
            
            # Send state update to all clients
            socketio.emit('state_update', {
                'session_id': session_id,
                'state': result.get('state', {}),
                'timestamp': time.time()
            }, room=session_id)
            
            logger.debug(f"Processed input for session {session_id} from client {client_id}")
        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            emit('error', {
                'message': f"Error processing input: {str(e)}"
            })

    @socketio.on_error()
    def handle_error(e):
        """Handle Socket.IO errors."""
        logger.error(f"Socket.IO error: {str(e)}")
        emit('error', {
            'message': str(e)
        })

# Global variables for Flask app
app = None
socketio = None 