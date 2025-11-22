"""
Performance Metrics for MetaMindIQTrain Server

This module provides a performance metrics collector for the server implementations.
It tracks requests, errors, response times, and more.
"""

import time
from typing import Dict, Any, List, Optional

class MetricsCollector:
    """Performance metrics collector for the MetaMindIQTrain server.
    
    This class collects and provides access to performance metrics such as
    request counts, error counts, and response times.
    """
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.metrics = {
            'requests': 0,
            'websocket_events': 0,
            'errors': 0,
            'start_time': time.time(),
            'response_times': []  # List of recent response times in ms
        }
    
    def record_request(self) -> None:
        """Record an HTTP request."""
        self.metrics['requests'] += 1
    
    def record_websocket_event(self) -> None:
        """Record a WebSocket event."""
        self.metrics['websocket_events'] += 1
    
    def record_error(self) -> None:
        """Record an error."""
        self.metrics['errors'] += 1
    
    def record_response_time(self, response_time: float) -> None:
        """Record a response time.
        
        Args:
            response_time: Response time in milliseconds
        """
        self.metrics['response_times'].append(response_time)
        
        # Keep only the last 100 response times
        if len(self.metrics['response_times']) > 100:
            self.metrics['response_times'] = self.metrics['response_times'][-100:]
    
    def get_uptime(self) -> float:
        """Get server uptime in seconds.
        
        Returns:
            Server uptime in seconds
        """
        return time.time() - self.metrics['start_time']
    
    def get_average_response_time(self) -> Optional[float]:
        """Get average response time.
        
        Returns:
            Average response time in milliseconds, or None if no responses have been recorded
        """
        if self.metrics['response_times']:
            return sum(self.metrics['response_times']) / len(self.metrics['response_times'])
        return None
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics.
        
        Returns:
            Dictionary of all metrics
        """
        return {
            'uptime': self.get_uptime(),
            'requests': self.metrics['requests'],
            'websocket_events': self.metrics['websocket_events'],
            'errors': self.metrics['errors'],
            'avg_response_time': self.get_average_response_time()
        } 