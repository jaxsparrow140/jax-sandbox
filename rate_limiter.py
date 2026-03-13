"""
Sliding Window Log Rate Limiter

Implements a sliding window log algorithm that tracks request timestamps
and allows N requests per M seconds.
"""

import time
from typing import List

class SlidingWindowRateLimiter:
    """
    Rate limiter using sliding window log algorithm.
    
    Allows N requests per M seconds.
    Tracks request timestamps and removes old ones from the log.
    """
    
    def __init__(self, max_requests: int, window_seconds: float):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests (int): Maximum number of requests allowed
            window_seconds (float): Time window in seconds
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
        self.request_timestamps = [
            ts for ts in self.request_timestamps 
            if current_time - ts < self.window_seconds
        ]
        
        # Check if we can allow a new request
        if len(self.request_timestamps) < self.max_requests:
            self.request_timestamps.append(current_time)
            return True
        else:
            return False
    
    def get_current_count(self) -> int:
        """
        Get the current number of requests in the window.
        
        Returns:
            int: Number of requests within the time window
        """
        current_time = time.time()
        return len([
            ts for ts in self.request_timestamps 
            if current_time - ts < self.window_seconds
        ])
    
    def clear(self):
        """
        Clear all request timestamps.
        """
        self.request_timestamps = []