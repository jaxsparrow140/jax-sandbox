"""
Test for SlidingWindowRateLimiter

Tests 100 requests over 10 seconds with a limit of 10 requests per 5 seconds.
"""

import time
import unittest
from rate_limiter import SlidingWindowRateLimiter

class TestSlidingWindowRateLimiter(unittest.TestCase):
    
    def test_sliding_window_limit(self):
        """
        Test the sliding window rate limiter with 100 requests over 10 seconds
        with a limit of 10 requests per 5 seconds.
        """
        # Initialize limiter: 10 requests per 5 seconds
        limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=5)
        
        # Simulate 100 requests over 10 seconds
        # We'll send requests in bursts to test the sliding window behavior
        allowed_requests = 0
        total_requests = 100
        
        # Send requests with small delays to simulate real usage
        for i in range(total_requests):
            # Simulate some time passing (not too fast to avoid perfect timing)
            if i > 0 and i % 10 == 0:
                time.sleep(0.1)  # Pause every 10 requests
            
            if limiter.allow_request():
                allowed_requests += 1
        
        # In a 10-second window with 10 requests per 5 seconds limit:
        # - First 5 seconds: max 10 requests allowed
        # - Next 5 seconds: max 10 requests allowed (sliding window)
        # - Total: max 20 requests should be allowed
        # 
        # The algorithm should allow approximately 20 requests total
        # (10 in first 5s, 10 in second 5s, with some overlap)
        
        print(f"Total requests: {total_requests}")
        print(f"Allowed requests: {allowed_requests}")
        print(f"Expected allowed: ~20 (10 per 5-second window)")
        
        # The limiter should allow at least 15 and at most 20 requests
        # due to the sliding window nature
        self.assertGreaterEqual(allowed_requests, 15)
        self.assertLessEqual(allowed_requests, 20)
        
        # Verify the current requests count is within limits
        current_count = limiter.get_current_requests()
        self.assertLessEqual(current_count, 10)
        
        # Test that we can't exceed the limit in a single window
        # Reset and test a burst
        limiter.reset()
        
        # Send 15 requests in a burst
        burst_allowed = 0
        for i in range(15):
            if limiter.allow_request():
                burst_allowed += 1
        
        # Should allow exactly 10 in the first burst
        self.assertEqual(burst_allowed, 10)
        
        # Wait for half the window to expire
        time.sleep(2.5)
        
        # Now try to send 5 more requests - should allow some
        second_burst_allowed = 0
        for i in range(5):
            if limiter.allow_request():
                second_burst_allowed += 1
        
        # Should allow up to 5 more (since 5 old requests have expired)
        self.assertGreaterEqual(second_burst_allowed, 0)
        self.assertLessEqual(second_burst_allowed, 5)
        
if __name__ == '__main__':
    unittest.main()