#!/usr/bin/env python3
"""
State Synchronization Module for MetaMindIQTrain

This module provides efficient state synchronization between the server and clients
using WebSockets and delta encoding. It minimizes network traffic by only sending
the changes between states rather than the full state each time.

Key features:
- Delta encoding for minimal network traffic
- Compression for further bandwidth reduction
- Automatic reconnection and state recovery
- Performance metrics tracking
"""

import json
import logging
import time
import asyncio
from typing import Dict, Any, List, Optional, Callable, Set, Tuple
import zlib
import base64

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StateSynchronizer:
    """
    Handles efficient state synchronization between server and clients.
    
    Uses delta encoding and compression for minimal network traffic.
    """
    
    def __init__(self, compression_threshold=512, send_full_state_interval=20):
        """
        Initialize the state synchronizer.
        
        Args:
            compression_threshold: Minimum size in bytes to apply compression
            send_full_state_interval: Send full state every N updates to prevent drift
        """
        self.clients = {}  # client_id -> {state, version, last_sync_time}
        self.compression_threshold = compression_threshold
        self.send_full_state_interval = send_full_state_interval
        
        # Statistics
        self.stats = {
            'total_updates': 0,
            'delta_updates': 0,
            'full_updates': 0,
            'compressed_updates': 0,
            'bytes_sent': 0,
            'bytes_saved': 0,
            'compression_ratio': 0
        }
    
    def register_client(self, client_id: str) -> None:
        """
        Register a new client for state synchronization.
        
        Args:
            client_id: Unique client identifier
        """
        self.clients[client_id] = {
            'state': {},
            'version': 0,
            'last_sync_time': time.time(),
            'update_count': 0
        }
        logger.debug(f"Registered client {client_id}")
    
    def unregister_client(self, client_id: str) -> None:
        """
        Unregister a client.
        
        Args:
            client_id: Client identifier to unregister
        """
        if client_id in self.clients:
            del self.clients[client_id]
            logger.debug(f"Unregistered client {client_id}")
    
    def compute_delta(self, previous_state: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute delta between previous and current state.
        
        Args:
            previous_state: Previous state dictionary
            current_state: Current state dictionary
            
        Returns:
            Delta dictionary with only changed values
        """
        if not previous_state:
            return current_state
            
        delta = {}
        self._compute_delta_recursive(previous_state, current_state, delta, "")
        return delta
    
    def _compute_delta_recursive(self, prev: Any, curr: Any, delta: Dict[str, Any], path: str) -> None:
        """
        Recursively compute delta between two states.
        
        Args:
            prev: Previous value
            curr: Current value
            delta: Output delta dictionary
            path: Current path in the state (for nested dicts)
        """
        # Handle different types
        if type(prev) != type(curr):
            # Types are different, include the entire current value
            if path:
                delta[path] = curr
            else:
                # Root level, copy all keys
                for key, value in curr.items():
                    delta[key] = value
            return
            
        # Handle dict type
        if isinstance(curr, dict):
            # Find keys only in current dict
            for key in set(curr.keys()) - set(prev.keys()):
                new_path = f"{path}.{key}" if path else key
                delta[new_path] = curr[key]
                
            # Find keys in both dicts
            for key in set(curr.keys()) & set(prev.keys()):
                new_path = f"{path}.{key}" if path else key
                if curr[key] != prev[key]:
                    if isinstance(curr[key], dict) and isinstance(prev[key], dict):
                        # Recurse for nested dicts
                        self._compute_delta_recursive(prev[key], curr[key], delta, new_path)
                    else:
                        # Add changed value
                        delta[new_path] = curr[key]
            
            # Keys only in previous dict are considered deleted
            for key in set(prev.keys()) - set(curr.keys()):
                new_path = f"{path}.{key}" if path else key
                delta[new_path] = None  # Null indicates deletion
                
        # Handle non-dict type
        elif curr != prev:
            delta[path] = curr
    
    def apply_delta(self, base_state: Dict[str, Any], delta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply delta to base state to get updated state.
        
        Args:
            base_state: Base state dictionary
            delta: Delta dictionary with changes
            
        Returns:
            Updated state dictionary
        """
        if not delta:
            return base_state
            
        # Make a deep copy of base state
        result = json.loads(json.dumps(base_state))
        
        # Apply each delta path
        for path, value in delta.items():
            if path == "_meta":
                continue  # Skip metadata
                
            if "." in path:
                # Handle nested path
                parts = path.split(".")
                curr = result
                
                # Navigate to parent object
                for part in parts[:-1]:
                    if part not in curr:
                        curr[part] = {}
                    curr = curr[part]
                    
                # Set or delete value
                if value is None:
                    # Delete key
                    if parts[-1] in curr:
                        del curr[parts[-1]]
                else:
                    # Set value
                    curr[parts[-1]] = value
            else:
                # Handle top-level path
                if value is None:
                    # Delete key
                    if path in result:
                        del result[path]
                else:
                    # Set value
                    result[path] = value
                    
        return result
    
    def prepare_update(self, client_id: str, current_state: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, bool]:
        """
        Prepare an update for a client.
        
        Args:
            client_id: Client identifier
            current_state: Current full state
            
        Returns:
            Tuple of (update data, is_delta, is_compressed)
        """
        if client_id not in self.clients:
            self.register_client(client_id)
            
        client_data = self.clients[client_id]
        client_data['update_count'] += 1
        
        # Send full state periodically to prevent drift or on first update
        send_full = (client_data['update_count'] % self.send_full_state_interval == 0 or 
                    client_data['version'] == 0)
        
        # Update statistics
        self.stats['total_updates'] += 1
        
        if send_full:
            # Full state update
            update_data = current_state.copy()
            update_data['_meta'] = {
                'version': client_data['version'] + 1,
                'is_delta': False,
                'timestamp': time.time()
            }
            
            # Calculate full data size for statistics
            full_data_size = len(json.dumps(update_data))
            self.stats['bytes_sent'] += full_data_size
            self.stats['full_updates'] += 1
            
            # Update client state
            client_data['state'] = update_data
            client_data['version'] += 1
            client_data['last_sync_time'] = time.time()
            
            return update_data, False, False
        else:
            # Delta update
            delta = self.compute_delta(client_data['state'], current_state)
            
            # Add metadata
            delta['_meta'] = {
                'version': client_data['version'] + 1,
                'is_delta': True,
                'base_version': client_data['version'],
                'timestamp': time.time()
            }
            
            # Calculate data sizes for statistics
            delta_size = len(json.dumps(delta))
            full_size = len(json.dumps(current_state))
            self.stats['bytes_saved'] += (full_size - delta_size)
            self.stats['bytes_sent'] += delta_size
            self.stats['delta_updates'] += 1
            
            # Check if full state would be smaller (rare but possible)
            if delta_size > full_size:
                # Full state is smaller, use that instead
                update_data = current_state.copy()
                update_data['_meta'] = {
                    'version': client_data['version'] + 1,
                    'is_delta': False,
                    'timestamp': time.time()
                }
                
                # Update statistics
                self.stats['bytes_sent'] -= delta_size
                self.stats['bytes_sent'] += full_size
                self.stats['bytes_saved'] -= (full_size - delta_size)
                self.stats['delta_updates'] -= 1
                self.stats['full_updates'] += 1
                
                # Update client state
                client_data['state'] = update_data
                client_data['version'] += 1
                client_data['last_sync_time'] = time.time()
                
                return update_data, False, False
                
            # Update client state
            client_data['state'] = current_state
            client_data['version'] += 1
            client_data['last_sync_time'] = time.time()
            
            return delta, True, False
    
    def compress_data(self, data: Dict[str, Any]) -> Tuple[str, bool]:
        """
        Compress data if it's large enough.
        
        Args:
            data: Data to compress
            
        Returns:
            Tuple of (compressed data string, is_compressed)
        """
        # Convert to JSON string
        json_str = json.dumps(data)
        
        # Only compress if above threshold
        if len(json_str) < self.compression_threshold:
            return json_str, False
            
        # Compress using zlib
        compressed = zlib.compress(json_str.encode('utf-8'))
        
        # Encode as base64 for safe transmission
        b64_data = base64.b64encode(compressed).decode('ascii')
        
        # Update statistics
        self.stats['compressed_updates'] += 1
        
        return b64_data, True
    
    def decompress_data(self, data: str, is_compressed: bool) -> Dict[str, Any]:
        """
        Decompress data if it's compressed.
        
        Args:
            data: Compressed or uncompressed data
            is_compressed: Whether the data is compressed
            
        Returns:
            Decompressed data dictionary
        """
        if not is_compressed:
            return json.loads(data)
            
        # Decode from base64
        binary_data = base64.b64decode(data)
        
        # Decompress
        decompressed = zlib.decompress(binary_data).decode('utf-8')
        
        # Parse JSON
        return json.loads(decompressed)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get synchronization statistics.
        
        Returns:
            Dictionary with statistics
        """
        # Calculate compression ratio
        if self.stats['compressed_updates'] > 0:
            total_potential = self.stats['bytes_sent'] + self.stats['bytes_saved']
            self.stats['compression_ratio'] = total_potential / self.stats['bytes_sent'] if self.stats['bytes_sent'] > 0 else 0
            
        return self.stats.copy()
    
    def reset_statistics(self) -> None:
        """Reset synchronization statistics."""
        self.stats = {
            'total_updates': 0,
            'delta_updates': 0,
            'full_updates': 0,
            'compressed_updates': 0,
            'bytes_sent': 0,
            'bytes_saved': 0,
            'compression_ratio': 0
        }

class WebSocketStateManager:
    """
    Manages WebSocket state synchronization for training modules.
    """
    
    def __init__(self, socketio, state_sync_interval=0.1):
        """
        Initialize the WebSocket state manager.
        
        Args:
            socketio: SocketIO server instance
            state_sync_interval: Time interval between state updates (seconds)
        """
        self.socketio = socketio
        self.state_sync_interval = state_sync_interval
        self.synchronizer = StateSynchronizer()
        
        # Active sessions: client_id -> {module, session_id}
        self.active_sessions = {}
        
        # Last update times: session_id -> last_update_time
        self.last_updates = {}
        
        # Update loop running flag
        self.is_running = False
        
        # Logger
        self.logger = logger
    
    def register_client(self, client_id: str) -> None:
        """
        Register a new client.
        
        Args:
            client_id: Client identifier (SocketIO SID)
        """
        self.synchronizer.register_client(client_id)
        self.logger.info(f"Client {client_id} connected")
    
    def unregister_client(self, client_id: str) -> None:
        """
        Unregister a client.
        
        Args:
            client_id: Client identifier to unregister
        """
        # End any active session for this client
        if client_id in self.active_sessions:
            self.end_session(client_id)
            
        self.synchronizer.unregister_client(client_id)
        self.logger.info(f"Client {client_id} disconnected")
    
    def start_session(self, client_id: str, module_instance: Any) -> Dict[str, Any]:
        """
        Start a new training session for a client.
        
        Args:
            client_id: Client identifier
            module_instance: TrainingModule instance
            
        Returns:
            Session information dictionary
        """
        # End any existing session for this client
        if client_id in self.active_sessions:
            self.end_session(client_id)
            
        session_id = module_instance.session_id
        
        # Store session information
        self.active_sessions[client_id] = {
            'module': module_instance,
            'session_id': session_id,
            'start_time': time.time()
        }
        
        self.last_updates[session_id] = time.time()
        
        # Send initial full state
        initial_state = module_instance.get_full_state()
        
        # Start update loop if not already running
        if not self.is_running:
            self._start_update_loop()
            
        self.logger.info(f"Started session {session_id} for client {client_id}")
        
        return {
            'module_id': module_instance.__class__.__name__,
            'session_id': session_id
        }
    
    def end_session(self, client_id: str) -> None:
        """
        End a training session for a client.
        
        Args:
            client_id: Client identifier
        """
        if client_id in self.active_sessions:
            session = self.active_sessions[client_id]
            session_id = session['session_id']
            
            # Clean up module
            session['module'].cleanup()
            
            # Remove from tracking
            del self.active_sessions[client_id]
            if session_id in self.last_updates:
                del self.last_updates[session_id]
                
            self.logger.info(f"Ended session {session_id} for client {client_id}")
    
    def handle_client_input(self, client_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle input from a client and update module state.
        
        Args:
            client_id: Client identifier
            input_data: Input data from client
            
        Returns:
            Result of handling the input
        """
        if client_id not in self.active_sessions:
            self.logger.warning(f"Received input from client {client_id} with no active session")
            return {'error': 'No active session'}
            
        # Get active module
        session = self.active_sessions[client_id]
        module = session['module']
        session_id = session['session_id']
        
        # Handle input based on type
        input_type = input_data.get('type', 'unknown')
        result = {}
        
        if input_type == 'click':
            # Handle click input
            x = input_data.get('x', 0)
            y = input_data.get('y', 0)
            result = module.handle_click(x, y)
        elif input_type == 'key':
            # Handle key input (if the module supports it)
            if hasattr(module, 'handle_key'):
                key = input_data.get('key', '')
                result = module.handle_key(key)
        elif input_type == 'full_state_request':
            # Client is requesting a full state update
            # This might be needed after a reconnection
            result = {'full_state_sent': True}
            
            # Force a full state update on next cycle
            if client_id in self.synchronizer.clients:
                self.synchronizer.clients[client_id]['version'] = 0
                
        # Update last update time
        self.last_updates[session_id] = time.time()
        
        return result
    
    def update_module_state(self, module: Any, dt: float) -> None:
        """
        Update a module's state.
        
        Args:
            module: TrainingModule instance
            dt: Time delta since last update (seconds)
        """
        module.update(dt)
    
    def send_update(self, client_id: str) -> None:
        """
        Send a state update to a client.
        
        Args:
            client_id: Client identifier
        """
        if client_id not in self.active_sessions:
            return
            
        # Get active module and current state
        session = self.active_sessions[client_id]
        module = session['module']
        current_state = module.get_state()
        
        # Prepare update (delta or full)
        update_data, is_delta, _ = self.synchronizer.prepare_update(client_id, current_state)
        
        # Compress if large
        compressed_data, is_compressed = self.synchronizer.compress_data(update_data)
        
        # Send via socketio
        self.socketio.emit('state_update', {
            'data': compressed_data,
            'is_delta': is_delta,
            'is_compressed': is_compressed
        }, room=client_id)
    
    def _start_update_loop(self) -> None:
        """Start the background update loop."""
        self.is_running = True
        self._schedule_update()
    
    def _schedule_update(self) -> None:
        """Schedule the next update cycle."""
        if not self.is_running:
            return
            
        # Schedule next update
        self.socketio.sleep(self.state_sync_interval)
        self._update_loop()
    
    def _update_loop(self) -> None:
        """Main update loop for all sessions."""
        # Get current time for delta calculation
        current_time = time.time()
        
        # Update all active modules
        for client_id, session in list(self.active_sessions.items()):
            module = session['module']
            session_id = session['session_id']
            
            # Calculate time since last update
            dt = current_time - self.last_updates.get(session_id, current_time)
            
            # Update the module
            self.update_module_state(module, dt)
            self.last_updates[session_id] = current_time
            
            # Send update to client
            self.send_update(client_id)
        
        # Schedule next update if we have any sessions
        if self.active_sessions:
            self._schedule_update()
        else:
            self.is_running = False 