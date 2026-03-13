"""Unittest suite for a sliding-window-log rate limiter.

Requirement in prompt:
- Implement sliding window log algorithm (see rate_limiter.RateLimiter)
- Test: simulate 100 requests over 10 seconds with limit 10 requests per 5 seconds
- Correct under bursts

Run:
    python -m unittest -q
"""

from __future__ import annotations

import unittest

from rate_limiter import RateLimiter


class TestSlidingWindowLogRateLimiter(unittest.TestCase):
    def test_allow_request_returns_bool(self) -> None:
        rl = RateLimiter(max_requests=1, window_seconds=1.0)
        out = rl.allow_request(now=0.0)
        self.assertIsInstance(out, bool)

    def test_simulate_100_requests_over_10_seconds_limit_10_per_5_seconds(self) -> None:
        max_req = 10
        window_s = 5.0

        rl = RateLimiter(max_requests=max_req, window_seconds=window_s)

        allowed_times: list[float] = []
        allowed = denied = 0

        # 100 requests evenly spaced over 10 seconds => 0.1s interval.
        for i in range(100):
            now = i * 0.1
            if rl.allow_request(now=now):
                allowed += 1
                allowed_times.append(now)
            else:
                denied += 1

        # With evenly-spaced requests at 0.1s intervals, the limiter should accept
        # 10 quickly, then another 10 once the first batch ages out.
        self.assertEqual(allowed, 20)
        self.assertEqual(denied, 80)

        # Sliding window invariant: no 5-second window contains > 10 allowed.
        for t0 in allowed_times:
            in_window = sum(1 for t in allowed_times if t0 <= t < t0 + window_s)
            self.assertLessEqual(in_window, max_req)

    def test_handles_bursts(self) -> None:
        rl = RateLimiter(max_requests=10, window_seconds=5.0)

        burst1 = [rl.allow_request(now=0.0) for _ in range(50)]
        self.assertEqual(burst1.count(True), 10)
        self.assertEqual(burst1.count(False), 40)

        # At t=5.0, the t=0.0 requests are exactly at the boundary and should be
        # evicted (window is (now - window, now]) based on the implementation.
        burst2 = [rl.allow_request(now=5.0) for _ in range(50)]
        self.assertEqual(burst2.count(True), 10)
        self.assertEqual(burst2.count(False), 40)


if __name__ == "__main__":
    unittest.main()
