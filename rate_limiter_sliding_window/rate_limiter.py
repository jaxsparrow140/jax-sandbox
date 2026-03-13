"""
Sliding Window Log Rate Limiter
Allows N requests per M seconds using sliding window algorithm.
"""

class SlidingWindowRateLimiter:
    def __init__(self, max_requests, window_seconds):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests (int): Maximum number of requests allowed
            window_seconds (int): Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_timestamps = []
    
    def allow_request(self):
        """
        Check if a request is allowed based on the sliding window algorithm.
        
        Returns:
            bool: True if request is allowed, False otherwise
        """
        current_time = self._get_current_time()
        
        # Remove timestamps older than the window
        while self.request_timestamps and self.request_timestamps[0] <= current_time - self.window_seconds:
            self.request_timestamps.pop(0)
        
        # Check if we're under the limit
        if len(self.request_timestamps) < self.max_requests:
            self.request_timestamps.append(current_time)
            return True
        else:
            return False
    
    def _get_current_time(self):
        """
        Get current time in seconds as a float.
        
        Returns:
            float: Current time in seconds since epoch
        """
        import time
        return time.time()
