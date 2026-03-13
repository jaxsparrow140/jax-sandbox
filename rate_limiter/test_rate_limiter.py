"""
Test for SlidingWindowRateLimiter with 100 requests over 10 seconds
and a limit of 10 requests per 5 seconds.
"""

import time
from sliding_window_rate_limiter import SlidingWindowRateLimiter

def test_sliding_window_rate_limiter():
    """
    Test the sliding window rate limiter with:
    - 100 requests over 10 seconds
    - Limit: 10 requests per 5 seconds
    """
    # Initialize limiter: 10 requests per 5 seconds
    limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=5)
    
    # Track results
    allowed_count = 0
    denied_count = 0
    
    print("Starting test: 100 requests over 10 seconds with limit of 10 requests per 5 seconds")
    
    # Simulate 100 requests over 10 seconds
    # We'll space them out evenly over 10 seconds
    for i in range(100):
        # Simulate request at time i * 0.1 seconds (so 100 requests over 10 seconds)
        time.sleep(0.1)  # Wait 0.1 seconds between requests
        
        if limiter.allow_request():
            allowed_count += 1
            print(f"Request {i+1}: ALLOWED (total allowed: {allowed_count})")
        else:
            denied_count += 1
            print(f"Request {i+1}: DENIED (total denied: {denied_count})")
        
        # Show current window count every 10 requests for visibility
        if (i + 1) % 10 == 0:
            current_count = limiter.get_current_request_count()
            print(f"--- After {i+1} requests: {current_count} requests in current window ---")
    
    print(f"\nFinal Results:")
    print(f"Allowed requests: {allowed_count}")
    print(f"Denied requests: {denied_count}")
    print(f"Total requests: {allowed_count + denied_count}")
    
    # Verify that the rate limiting works as expected
    # With 10 requests per 5 seconds, over 10 seconds we should allow approximately 20 requests
    # (10 in first 5 seconds + 10 in second 5 seconds)
    # Due to the sliding window, we might allow slightly more than 20
    
    # The sliding window should allow bursts but still respect the rate limit
    # We expect to see a pattern where requests are allowed in bursts then denied
    # as the window slides
    
    # Since we're making 100 requests over 10 seconds with a limit of 10 per 5 seconds,
    # we expect the limiter to allow roughly 20 requests (the theoretical maximum)
    # but due to the sliding window algorithm, it might allow slightly more
    # in the transition between windows
    
    # The key test is that it doesn't allow more than ~20 requests in total
    # over the 10 second period
    
    assert allowed_count <= 25, f"Expected at most 25 allowed requests, got {allowed_count}"
    assert denied_count >= 75, f"Expected at least 75 denied requests, got {denied_count}"
    
    print("\nTest passed! Rate limiter is working as expected.")
    
if __name__ == "__main__":
    test_sliding_window_rate_limiter()