"""
Sliding Window Log Rate Limiter

Implements the sliding window log algorithm:
- Maintains a log of timestamps for each request
- Allows N requests per M seconds window
- Checks if the count of requests in the current window exceeds the limit
"""

import time
from collections import deque
from typing import Optional


class SlidingWindowLogRateLimiter:
    """
    Rate limiter using the sliding window log algorithm.
    
    Tracks exact timestamps of requests and counts how many fall within
    the current sliding window. More accurate than counter-based approaches
    but requires more memory (stores all timestamps within the window).
    """
    
    def __init__(self, max_requests: int, window_seconds: float):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in the window
            window_seconds: Size of the sliding window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_log: deque[float] = deque()
    
    def _cleanup_old_requests(self, current_time: float) -> None:
        """
        Remove requests that are outside the current window.
        
        Args:
            current_time: Current timestamp
        """
        window_start = current_time - self.window_seconds
        
        # Remove all timestamps older than the window start
        while self.request_log and self.request_log[0] <= window_start:
            self.request_log.popleft()
    
    def allow_request(self) -> bool:
        """
        Check if a new request is allowed.
        
        Returns:
            True if the request is allowed, False if rate limit exceeded
        """
        current_time = time.time()
        
        # Clean up old requests outside the window
        self._cleanup_old_requests(current_time)
        
        # Check if we're at the limit
        if len(self.request_log) >= self.max_requests:
            return False
        
        # Allow the request and log it
        self.request_log.append(current_time)
        return True
    
    def get_current_count(self) -> int:
        """
        Get the current number of requests in the window.
        
        Returns:
            Number of requests in the current sliding window
        """
        current_time = time.time()
        self._cleanup_old_requests(current_time)
        return len(self.request_log)
    
    def get_wait_time(self) -> float:
        """
        Get the time to wait before the next request is allowed.
        
        Returns:
            Seconds until next request is allowed (0 if allowed now)
        """
        current_time = time.time()
        self._cleanup_old_requests(current_time)
        
        if len(self.request_log) < self.max_requests:
            return 0.0
        
        # Need to wait until the oldest request expires
        oldest = self.request_log[0]
        wait_time = (oldest + self.window_seconds) - current_time
        return max(0.0, wait_time)


def test_rate_limiter():
    """
    Test the rate limiter with 100 requests over 10 seconds.
    Limit: 10 requests per 5 seconds.
    
    Expected behavior:
    - First 10 requests should be allowed (0-5s window)
    - Requests 11-20 should be denied until window slides
    - As window slides, more requests should be allowed
    - Total allowed should be approximately 20 (2 windows × 10 requests)
    """
    print("Testing Sliding Window Log Rate Limiter")
    print("Configuration: 10 requests per 5 seconds")
    print("Test: 100 requests over 10 seconds\n")
    
    limiter = SlidingWindowLogRateLimiter(max_requests=10, window_seconds=5.0)
    
    allowed_count = 0
    denied_count = 0
    results = []
    
    # Simulate 100 requests over 10 seconds (10 requests per second)
    # We'll patch time.time() to use simulated timestamps
    base_time = 1000.0  # Use a fixed base time for simulation
    
    for i in range(100):
        # Calculate simulated time for this request
        simulated_time = base_time + (i * 0.1)  # 0.1 seconds between requests
        
        # Temporarily patch time.time() for this call
        import time
        original_time = time.time
        time.time = lambda: simulated_time
        
        # Allow request at simulated time
        allowed = limiter.allow_request()
        
        # Restore original time.time
        time.time = original_time
        
        if allowed:
            allowed_count += 1
            results.append((i, True, simulated_time - base_time))
        else:
            denied_count += 1
            results.append((i, False, simulated_time - base_time))
    
    # Print results
    print(f"Results:")
    print(f"  Total requests: 100")
    print(f"  Allowed: {allowed_count}")
    print(f"  Denied: {denied_count}")
    print(f"  Allowed rate: {allowed_count/100*100:.1f}%\n")
    
    # Show timeline of allowed/denied
    print("Timeline (first 20 requests):")
    for req_num, allowed, elapsed in results[:20]:
        status = "✓ ALLOWED" if allowed else "✗ DENIED"
        print(f"  Request {req_num+1}: {status} at {elapsed:.2f}s")
    
    # Show when requests start being allowed again
    print("\nTimeline (requests 50-60 - should show second window opening):")
    for req_num, allowed, elapsed in results[50:60]:
        status = "✓ ALLOWED" if allowed else "✗ DENIED"
        print(f"  Request {req_num+1}: {status} at {elapsed:.2f}s")
    
    print("\nTimeline (requests 90-100):")
    for req_num, allowed, elapsed in results[90:100]:
        status = "✓ ALLOWED" if allowed else "✗ DENIED"
        print(f"  Request {req_num+1}: {status} at {elapsed:.2f}s")
    
    # Verify expected behavior
    print("\nExpected behavior analysis:")
    print("  - Window size: 5 seconds")
    print("  - Limit: 10 requests per window")
    print("  - Over 10 seconds, we expect ~20 requests allowed (2 full windows)")
    print(f"  - Actual allowed: {allowed_count}")
    
    # The sliding window should allow roughly 20 requests
    # (10 in first 5s window, 10 in second 5s window)
    if 18 <= allowed_count <= 22:
        print("  ✓ Test PASSED: Allowed count within expected range")
        return True
    else:
        print("  ✗ Test FAILED: Allowed count outside expected range")
        return False


if __name__ == "__main__":
    test_rate_limiter()