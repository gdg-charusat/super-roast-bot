"""
Simple thread-safe rate limiter for RoastBot.
Implements a sliding window log to prevent abuse and API quota exhaustion.
"""

import time
import threading
from collections import defaultdict, deque
from typing import Dict, Deque


class RateLimiter:
    """
    A sliding window log rate limiter.
    
    Tracks request timestamps per client IP/session and enforces a maximum
    number of allowed requests within a specific time window.
    """

    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        """
        Initialize the rate limiter.

        Args:
            max_requests: Maximum number of requests allowed in the window.
            window_seconds: The time window in seconds.
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        
        # Dictionary mapping client_id to a deque of request timestamps
        self.clients: Dict[str, Deque[float]] = defaultdict(deque)
        
        # Lock to ensure thread safety
        self.lock = threading.Lock()

    def is_allowed(self, client_id: str) -> bool:
        """
        Check if the client is allowed to make a request at the current time.
        If allowed, records the request timestamp.

        Args:
            client_id: A unique identifier for the client (e.g., IP address or session ID).

        Returns:
            bool: True if the request is allowed, False if the limit is exceeded.
        """
        now = time.time()
        
        with self.lock:
            # Get the timestamp history for this client
            history = self.clients[client_id]
            
            # Remove timestamps that are older than the time window
            window_start = now - self.window_seconds
            while history and history[0] <= window_start:
                history.popleft()
            
            # Check if the limit has been reached
            if len(history) >= self.max_requests:
                return False
            
            # If allowed, record the new request
            history.append(now)
            return True

    def get_wait_time(self, client_id: str) -> float:
        """
        Calculate how long the client needs to wait before making another request.

        Args:
            client_id: The unique identifier for the client.

        Returns:
            float: Seconds to wait. Returns 0.0 if the client is currently allowed.
        """
        now = time.time()
        
        with self.lock:
            history = self.clients[client_id]
            
            # Clean up old entries
            window_start = now - self.window_seconds
            while history and history[0] <= window_start:
                history.popleft()
                
            # If under the limit, no wait is needed
            if len(history) < self.max_requests:
                return 0.0
            
            # The wait time is the time until the oldest request falls out of the window
            oldest_request = history[0]
            wait_time = (oldest_request + self.window_seconds) - now
            
            # Ensure we don't return negative times
            return max(0.0, wait_time)

