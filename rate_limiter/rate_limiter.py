"""
Sliding Window Log Rate Limiter

Implements a sliding window log algorithm that tracks request timestamps
and allows N requests per M seconds, even during bursts.
"""

import time
from typing import List

class SlidingWindowRateLimiter:
    """
    Rate limiter using sliding window log algorithm.
    
    Allows N requests per M seconds.
    Tracks exact request timestamps to handle bursts correctly.
    """
    
    def __init__(self, max_requests: int, window_seconds: float):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests (int): Maximum number of requests allowed in the window
            window_seconds (float): Length of the time window in seconds
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
        cutoff_time = current_time - self.window_seconds
        self.request_timestamps = [
            ts for ts in self.request_timestamps 
            if ts > cutoff_time
        ]
        
        # Check if we have room for another request
        if len(self.request_timestamps) < self.max_requests:
            # Add current request timestamp
            self.request_timestamps.append(current_time)
            return True
        else:
            return False
    
    def get_current_requests(self) -> int:
        """
        Get the current number of requests in the window.
        
        Returns:
            int: Number of requests currently in the window
        """
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds
        return len([ts for ts in self.request_timestamps if ts > cutoff_time])
    
    def reset(self):
        """
        Clear all request timestamps.
        """
        self.request_timestamps = []
