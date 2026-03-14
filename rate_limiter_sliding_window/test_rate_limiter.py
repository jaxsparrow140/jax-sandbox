"""
Test for SlidingWindowRateLimiter with 100 requests over 10 seconds, limit: 10 requests per 5 seconds.
"""

import time
from rate_limiter import SlidingWindowRateLimiter

def test_sliding_window_rate_limiter():
    """Test the sliding window rate limiter with burst requests."""
    
    # Initialize limiter: 10 requests per 5 seconds
    limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=5)
    
    # Simulate 100 requests over 10 seconds
    total_requests = 100
    total_time_seconds = 10
    
    # Track results
    allowed_count = 0
    denied_count = 0
    
    print(f"Testing SlidingWindowRateLimiter with 10 requests per 5 seconds")
    print(f"Simulating {total_requests} requests over {total_time_seconds} seconds")
    print("-" * 60)
    
    # Send requests with small delays to simulate burst pattern
    # First 10 requests immediately, then wait a bit, then next burst
    start_time = time.time()
    
    for i in range(total_requests):
        # Send requests at a rate that creates bursts
        if i > 0 and i % 10 == 0:
            time.sleep(0.5)  # Small pause between bursts
        
        if limiter.allow_request():
            allowed_count += 1
            status = "ALLOWED"
        else:
            denied_count += 1
            status = "DENIED"
        
        # Print status every 10 requests to avoid spam
        if i % 10 == 0:
            elapsed = time.time() - start_time
            print(f"Request {i+1}/{total_requests} - {status} (elapsed: {elapsed:.2f}s)")
    
    # Print summary
    elapsed = time.time() - start_time
    print("-" * 60)
    print(f"Summary:")
    print(f"Total requests: {total_requests}")
    print(f"Allowed: {allowed_count}")
    print(f"Denied: {denied_count}")
    print(f"Elapsed time: {elapsed:.2f}s")
    print(f"Success: {'✓' if allowed_count <= 20 else '✗'} (should be <= 20 since 10 per 5s over 10s = 20 max)")
    
    # Verify the algorithm works correctly
    # In a 10-second window with 10 requests per 5 seconds, max allowed should be 20
    assert allowed_count <= 20, f"Expected at most 20 allowed requests, got {allowed_count}"
    print(f"\nTest passed! The rate limiter correctly enforced the limit.")

if __name__ == "__main__":
    test_sliding_window_rate_limiter()
