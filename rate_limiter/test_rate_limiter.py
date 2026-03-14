"""
Test for SlidingWindowRateLimiter with 100 requests over 10 seconds
and a limit of 10 requests per 5 seconds.
"""

import time
import unittest
from rate_limiter import SlidingWindowRateLimiter

class TestSlidingWindowRateLimiter(unittest.TestCase):
    
    def test_sliding_window_burst(self):
        """
        Test the sliding window rate limiter with 100 requests over 10 seconds
        with a limit of 10 requests per 5 seconds.
        """
        # Initialize limiter: 10 requests per 5 seconds
        limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=5)
        
        # Simulate 100 requests over 10 seconds
        # We'll send requests in bursts to test the sliding window behavior
        allowed_count = 0
        denied_count = 0
        
        # Send requests in a burst pattern over 10 seconds
        for i in range(100):
            # Simulate time passing (roughly 0.1 seconds between requests)
            # This creates a bursty pattern
            if i > 0 and i % 10 == 0:
                time.sleep(0.1)  # Pause briefly every 10 requests
            
            if limiter.allow_request():
                allowed_count += 1
            else:
                denied_count += 1
        
        # After 100 requests, we expect:
        # - In a 5-second window, max 10 requests allowed
        # - Over 10 seconds, we should be able to make roughly 20 requests (10 per 5s)
        #   but due to the sliding window and burst pattern, we might get slightly more
        #   as requests from the first 5 seconds expire and make room
        
        print(f"Allowed requests: {allowed_count}")
        print(f"Denied requests: {denied_count}")
        
        # The sliding window should allow approximately 20 requests
        # (10 in first 5s, then 10 more as the first 10 expire)
        # But due to the burst pattern and timing, we might get slightly more
        # Let's assert we're in a reasonable range
        self.assertGreaterEqual(allowed_count, 15)  # Should get at least 15
        self.assertLessEqual(allowed_count, 25)     # Should get at most 25
        self.assertEqual(allowed_count + denied_count, 100)
        
        # Verify the current request count is within limits
        current_requests = limiter.get_current_requests()
        self.assertLessEqual(current_requests, 10)
        
        print(f"Current requests in window: {current_requests}")
        
if __name__ == '__main__':
    unittest.main()