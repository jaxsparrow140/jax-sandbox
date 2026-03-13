"""
Sliding Window Log Rate Limiter

Algorithm: maintain a log of timestamps for each request. On each new request,
purge entries older than the window, then check if the remaining count is under
the limit. O(n) per call in the worst case but exact — no approximation error.
"""

from __future__ import annotations

import time
from collections import deque
from typing import Optional


class SlidingWindowRateLimiter:
    """
    Allows at most `max_requests` within any rolling window of `window_seconds`.

    Uses a sorted deque of timestamps (the "log"). On each call to
    allow_request(), expired entries are evicted from the left before
    checking the count.
    """

    def __init__(self, max_requests: int, window_seconds: float):
        if max_requests < 1:
            raise ValueError("max_requests must be >= 1")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be > 0")
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._log: deque[float] = deque()

    def allow_request(self, now: Optional[float] = None) -> bool:
        """
        Returns True and records the request if under the limit,
        False otherwise.

        Parameters
        ----------
        now : float, optional
            Current timestamp (seconds). Defaults to time.monotonic().
            Accepting an explicit value makes the limiter deterministically
            testable without monkeypatching.
        """
        if now is None:
            now = time.monotonic()

        # Evict everything outside the window
        cutoff = now - self.window_seconds
        while self._log and self._log[0] <= cutoff:
            self._log.popleft()

        if len(self._log) < self.max_requests:
            self._log.append(now)
            return True

        return False

    @property
    def current_count(self) -> int:
        """How many requests are in the current window (without evicting)."""
        return len(self._log)

    def __repr__(self) -> str:
        return (
            f"SlidingWindowRateLimiter(max_requests={self.max_requests}, "
            f"window_seconds={self.window_seconds}, "
            f"current_count={self.current_count})"
        )


# ---------------------------------------------------------------------------
# Test harness
# ---------------------------------------------------------------------------

def test_burst_simulation():
    """
    Simulate 100 requests over 10 seconds with a limit of 10 req / 5 sec.

    Strategy: fire requests at known timestamps and assert that the limiter
    never exceeds 10 accepts in any 5-second window.
    """
    LIMIT = 10
    WINDOW = 5.0
    TOTAL_REQUESTS = 100
    DURATION = 10.0

    limiter = SlidingWindowRateLimiter(max_requests=LIMIT, window_seconds=WINDOW)

    # --- build a mixed schedule: bursts + steady trickle ---
    # Burst 1: 20 requests crammed into t=0.00–0.19
    timestamps = [round(i * 0.01, 4) for i in range(20)]
    # Steady: 30 requests from t=1.0–4.0 (every ~100ms)
    timestamps += [round(1.0 + i * 0.1, 4) for i in range(30)]
    # Burst 2: 20 requests at t=5.00–5.19
    timestamps += [round(5.0 + i * 0.01, 4) for i in range(20)]
    # Steady: 15 requests from t=6.0–9.0 (~200ms apart)
    timestamps += [round(6.0 + i * 0.2, 4) for i in range(15)]
    # Burst 3: 15 requests at t=9.50–9.64
    timestamps += [round(9.5 + i * 0.01, 4) for i in range(15)]

    assert len(timestamps) == TOTAL_REQUESTS, f"Expected 100, got {len(timestamps)}"
    assert timestamps[-1] <= DURATION

    # --- run simulation ---
    results: list[tuple[float, bool]] = []
    for ts in timestamps:
        ok = limiter.allow_request(now=ts)
        results.append((ts, ok))

    accepted = [t for t, ok in results if ok]
    rejected = [t for t, ok in results if not ok]

    # --- invariant check ------------------------------------------------
    # The limiter's window is half-open: (now - W, now].  At any accepted
    # timestamp t, the log contains entries in (t - W, t] — at most LIMIT.
    # We verify this at every accepted time AND at every request time.
    all_check_points = sorted(set(t for t, _ in results))
    for t_now in all_check_points:
        count = sum(1 for t in accepted if (t_now - WINDOW) < t <= t_now)
        assert count <= LIMIT, (
            f"Violation at t={t_now}: {count} accepts in "
            f"({t_now - WINDOW}, {t_now}]"
        )

    # --- reporting ---
    print(f"{'='*60}")
    print(f"Sliding Window Log Rate Limiter — Burst Test")
    print(f"{'='*60}")
    print(f"Config:   {LIMIT} requests / {WINDOW}s window")
    print(f"Traffic:  {TOTAL_REQUESTS} requests over {DURATION}s")
    print(f"Accepted: {len(accepted)}")
    print(f"Rejected: {len(rejected)}")
    print(f"{'='*60}")

    # Per-second breakdown
    print(f"\n{'Second':<10} {'Sent':>6} {'Accepted':>10} {'Rejected':>10}")
    print(f"{'-'*40}")
    for sec in range(int(DURATION) + 1):
        sent = sum(1 for t, _ in results if sec <= t < sec + 1)
        acc = sum(1 for t, ok in results if sec <= t < sec + 1 and ok)
        rej = sum(1 for t, ok in results if sec <= t < sec + 1 and not ok)
        if sent:
            print(f"t={sec:<7} {sent:>6} {acc:>10} {rej:>10}")

    print(f"\n✅ All invariants hold — no window exceeds {LIMIT} accepts.")


if __name__ == "__main__":
    test_burst_simulation()
