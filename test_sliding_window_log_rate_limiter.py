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

    # ------------------------------------------------------------------
    # Basic / type checks
    # ------------------------------------------------------------------

    def test_allow_request_returns_bool(self) -> None:
        rl = RateLimiter(max_requests=1, window_seconds=1.0)
        out = rl.allow_request(now=0.0)
        self.assertIsInstance(out, bool)

    def test_first_request_always_allowed(self) -> None:
        rl = RateLimiter(max_requests=5, window_seconds=10.0)
        self.assertTrue(rl.allow_request(now=0.0))

    def test_limit_enforced_immediately(self) -> None:
        rl = RateLimiter(max_requests=3, window_seconds=10.0)
        for _ in range(3):
            self.assertTrue(rl.allow_request(now=0.0))
        # 4th request at same instant must be denied
        self.assertFalse(rl.allow_request(now=0.0))

    def test_window_expires_exactly_at_boundary(self) -> None:
        """Timestamps *on* the left boundary are evicted (half-open window)."""
        rl = RateLimiter(max_requests=1, window_seconds=5.0)
        rl.allow_request(now=0.0)          # fills the single slot
        self.assertFalse(rl.allow_request(now=4.9))   # still inside window
        # at t=5.0 the t=0.0 entry is exactly at the cutoff → evicted
        self.assertTrue(rl.allow_request(now=5.0))

    # ------------------------------------------------------------------
    # Core simulation: 100 requests over 10 seconds, 10 req / 5 s
    # ------------------------------------------------------------------

    def test_simulate_100_requests_over_10_seconds_limit_10_per_5_seconds(self) -> None:
        """
        100 requests spaced 0.1 s apart (t = 0.0, 0.1, …, 9.9).
        Limit: 10 req / 5 s.

        Expected outcome
        ----------------
        t = 0.0 – 0.9   → 10 allowed  (fills window 0-5 s)
        t = 1.0 – 4.9   → 40 denied   (window still full)
        t = 5.0 – 5.9   → 10 allowed  (t=0.0-0.9 entries expire one-by-one)
        t = 6.0 – 9.9   → 40 denied   (window full again with t=5.0-5.9 entries)
        ──────────────────────────────
        Total allowed   = 20, denied = 80
        """
        max_req = 10
        window_s = 5.0

        rl = RateLimiter(max_requests=max_req, window_seconds=window_s)

        allowed_times: list[float] = []
        allowed = denied = 0

        for i in range(100):
            now = round(i * 0.1, 10)
            if rl.allow_request(now=now):
                allowed += 1
                allowed_times.append(now)
            else:
                denied += 1

        self.assertEqual(allowed, 20, f"Expected 20 allowed, got {allowed}")
        self.assertEqual(denied, 80,  f"Expected 80 denied, got {denied}")

        # Sliding-window invariant: no 5-second window may contain > 10 allowed.
        for t0 in allowed_times:
            in_window = sum(1 for t in allowed_times if t0 <= t < t0 + window_s)
            self.assertLessEqual(
                in_window, max_req,
                f"Invariant violated: {in_window} requests in window starting at {t0}"
            )

    # ------------------------------------------------------------------
    # Burst handling
    # ------------------------------------------------------------------

    def test_handles_bursts(self) -> None:
        """50 simultaneous requests → only 10 pass; same for second burst."""
        rl = RateLimiter(max_requests=10, window_seconds=5.0)

        burst1 = [rl.allow_request(now=0.0) for _ in range(50)]
        self.assertEqual(burst1.count(True),  10)
        self.assertEqual(burst1.count(False), 40)

        # At t=5.0 all t=0.0 entries are exactly on the boundary → evicted.
        burst2 = [rl.allow_request(now=5.0) for _ in range(50)]
        self.assertEqual(burst2.count(True),  10)
        self.assertEqual(burst2.count(False), 40)

    def test_burst_then_trickle(self) -> None:
        """After a burst fills the window, individual later requests are denied
        until entries age out."""
        rl = RateLimiter(max_requests=5, window_seconds=10.0)

        for _ in range(5):
            self.assertTrue(rl.allow_request(now=0.0))

        # Still inside window
        self.assertFalse(rl.allow_request(now=5.0))
        self.assertFalse(rl.allow_request(now=9.99))

        # Window has fully slid past the burst
        self.assertTrue(rl.allow_request(now=10.0))

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------

    def test_current_count(self) -> None:
        rl = RateLimiter(max_requests=10, window_seconds=5.0)
        self.assertEqual(rl.current_count(now=0.0), 0)
        rl.allow_request(now=0.0)
        rl.allow_request(now=1.0)
        self.assertEqual(rl.current_count(now=1.0), 2)
        # After window expires the count should drop back to 0
        self.assertEqual(rl.current_count(now=10.0), 0)

    def test_time_until_next(self) -> None:
        rl = RateLimiter(max_requests=2, window_seconds=4.0)
        rl.allow_request(now=0.0)
        rl.allow_request(now=1.0)
        # Window is full; oldest entry is at 0.0, expires at 4.0
        wait = rl.time_until_next(now=2.0)
        self.assertAlmostEqual(wait, 2.0, places=9)

    def test_time_until_next_zero_when_space(self) -> None:
        rl = RateLimiter(max_requests=5, window_seconds=1.0)
        self.assertEqual(rl.time_until_next(now=0.0), 0.0)

    # ------------------------------------------------------------------
    # Edge / constructor validation
    # ------------------------------------------------------------------

    def test_invalid_max_requests_raises(self) -> None:
        with self.assertRaises(ValueError):
            RateLimiter(max_requests=0, window_seconds=1.0)

    def test_invalid_window_raises(self) -> None:
        with self.assertRaises(ValueError):
            RateLimiter(max_requests=1, window_seconds=0.0)

    def test_max_requests_one(self) -> None:
        """Edge case: only 1 request per window."""
        rl = RateLimiter(max_requests=1, window_seconds=1.0)
        self.assertTrue(rl.allow_request(now=0.0))
        self.assertFalse(rl.allow_request(now=0.5))
        self.assertTrue(rl.allow_request(now=1.0))   # previous expires at boundary


# ---------------------------------------------------------------------------
# Standalone demo: print a human-readable timeline (not a unittest)
# ---------------------------------------------------------------------------

def run_simulation_demo() -> None:
    """Print a visual summary of the 100-request simulation."""
    print("=" * 60)
    print("Sliding Window Log Rate Limiter — Simulation Demo")
    print("Config: 10 requests / 5 seconds | 100 reqs over 10 s")
    print("=" * 60)

    rl = RateLimiter(max_requests=10, window_seconds=5.0)
    results: list[tuple[int, float, bool]] = []

    for i in range(100):
        now = round(i * 0.1, 10)
        ok = rl.allow_request(now=now)
        results.append((i + 1, now, ok))

    allowed = sum(1 for _, _, ok in results if ok)
    denied  = sum(1 for _, _, ok in results if not ok)

    print(f"\n{'Req':>4}  {'Time':>6}  Status")
    print("-" * 26)
    for req_n, t, ok in results:
        marker = "✓ ALLOWED" if ok else "✗ denied "
        # Highlight allowed requests
        print(f"{req_n:>4}  {t:>6.2f}s  {marker}")

    print("-" * 26)
    print(f"Allowed: {allowed} / 100   Denied: {denied} / 100")
    print(f"{'PASS ✓' if allowed == 20 else 'FAIL ✗'}: expected 20 allowed, got {allowed}")


if __name__ == "__main__":
    run_simulation_demo()
    print("\n" + "=" * 60)
    print("Running unittest suite …")
    print("=" * 60 + "\n")
    unittest.main(argv=[""], exit=False, verbosity=2)
