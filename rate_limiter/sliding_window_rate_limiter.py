"""
Sliding Window Rate Limiter Implementation

Implements a sliding window log algorithm that allows N requests per M seconds.
Tracks request timestamps in a list and removes old ones as the window slides.
"""

import time
from typing import List

class SlidingWindowRateLimiter:
    """
    Rate limiter using sliding window log algorithm.
    
    Allows N requests per M seconds. Uses a list to track request timestamps.
    When a new request comes in, removes all timestamps older than the current window.
    """
    
    def __init__(self, max_requests: int, window_seconds: float):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests (int): Maximum number of requests allowed in the window
            window_seconds (float): Size of the sliding window in seconds
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
        
        # Remove timestamps that are outside the current window
        # This is the sliding window part - we only keep requests within the time window
        self.request_timestamps = [
            ts for ts in self.request_timestamps 
            if current_time - ts < self.window_seconds
        ]
        
        # Check if we can allow this request
        if len(self.request_timestamps) < self.max_requests:
            # Add current request timestamp
            self.request_timestamps.append(current_time)
            return True
        else:
            return False
    
    def get_current_request_count(self) -> int:
        """
        Get the number of requests in the current window.
        
        Returns:
            int: Number of requests in the current sliding window
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