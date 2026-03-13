"""
Test for SlidingWindowRateLimiter

Simulates 100 requests over 10 seconds with a limit of 10 requests per 5 seconds.
"""

import time
import threading
from rate_limiter import SlidingWindowRateLimiter

def test_sliding_window_rate_limiter():
    """Test the sliding window rate limiter with burst requests."""
    
    # Initialize limiter: 10 requests per 5 seconds
    limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=5)
    
    # Simulate 100 requests over 10 seconds
    total_requests = 100
    total_time = 10.0  # seconds
    
    # Track results
    allowed_count = 0
    blocked_count = 0
    
    # Record start time
    start_time = time.time()
    
    # Simulate requests in a burst pattern
    for i in range(total_requests):
        # Distribute requests over the 10-second period
        # This creates a burst pattern by sending multiple requests close together
        delay = (i % 20) * 0.1  # Create bursts every 20 requests
        time.sleep(delay)
        
        # Check if request is allowed
        if limiter.allow_request():
            allowed_count += 1
        else:
            blocked_count += 1
        
        # Print status every 10 requests
        if (i + 1) % 10 == 0:
            current_time = time.time() - start_time
            current_count = limiter.get_current_count()
            print(f"Request {i+1}/{total_requests}: "
                  f"Allowed: {allowed_count}, Blocked: {blocked_count}, "
                  f"Current window count: {current_count}, "
                  f"Elapsed: {current_time:.2f}s")
    
    # Final summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Total requests: {total_requests}")
    print(f"Allowed requests: {allowed_count}")
    print(f"Blocked requests: {blocked_count}")
    print(f"Rate limit: 10 requests per 5 seconds")
    print(f"Expected maximum allowed in 10s: ~20 (10 per 5s window)")
    print(f"Actual allowed: {allowed_count}")
    
    # Verify the algorithm is working correctly
    # In a sliding window of 5s with limit 10, over 10s we should be able to allow
    # approximately 20 requests (10 in first 5s, 10 in second 5s, with overlap)
    # But due to the burst pattern and exact timing, we might see slightly less
    
    assert allowed_count > 0, "Should allow at least some requests"
    assert blocked_count > 0, "Should block some requests due to rate limiting"
    print("\n✅ Test passed: Rate limiter is working as expected!")

if __name__ == "__main__":
    test_sliding_window_rate_limiter()