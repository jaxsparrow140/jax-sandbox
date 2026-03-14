"""
Sliding Window Rate Limiter Implementation

Implements the sliding window log algorithm for rate limiting.
Allows N requests per M seconds with burst handling.
"""

import time
from typing import List

class SlidingWindowRateLimiter:
    """
    Sliding Window Rate Limiter using log-based approach.
    
    Allows N requests per M seconds. Tracks request timestamps in a list,
    removing old entries outside the window.
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests (int): Maximum number of requests allowed in the window
            window_seconds (int): Size of the time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_timestamps: List[float] = []
    
    def allow_request(self) -> bool:
        """
        Check if a request is allowed based on the sliding window algorithm.
        
        Returns:
            bool: True if request is allowed, False otherwise
        """
        current_time = time.time()
        
        # Remove timestamps that are outside the sliding window
        while self.request_timestamps and self.request_timestamps[0] < current_time - self.window_seconds:
            self.request_timestamps.pop(0)
        
        # Check if we can allow the request
        if len(self.request_timestamps) < self.max_requests:
            self.request_timestamps.append(current_time)
            return True
        else:
            return False
    
    def get_current_requests(self) -> int:
        """
        Get the number of requests in the current window.
        
        Returns:
            int: Number of requests within the current window
        """
        current_time = time.time()
        # Clean old timestamps
        while self.request_timestamps and self.request_timestamps[0] < current_time - self.window_seconds:
            self.request_timestamps.pop(0)
        return len(self.request_timestamps)
    
    def reset(self):
        """
        Reset the rate limiter (clear all timestamps).
        """
        self.request_timestamps = []
