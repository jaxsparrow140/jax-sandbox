"""
Sliding Window Log Rate Limiter
================================
Implements the sliding window log algorithm.

Allows N requests per M seconds.  Stores exact request timestamps in a
deque; on each call to allow_request() it evicts entries that have fallen
outside the window, then either admits (and logs) the request or rejects it.

Key properties
--------------
* Exact – no approximation error from bucketing
* Burst-safe – a burst of N+1 simultaneous requests will allow exactly N
* O(1) amortised per call (each timestamp is enqueued and dequeued once)
* Deterministic / testable – allow_request() accepts an optional `now`
  argument so tests can inject a fake clock without monkey-patching

Window boundary convention
--------------------------
A request logged at time t is valid while ``now - window_seconds < t``.
Requests *on* the left boundary (t == now - window_seconds) are considered
expired and evicted.  This is a half-open window  (t, t + window_seconds].
"""

from __future__ import annotations

import time
from collections import deque
from typing import Optional


class RateLimiter:
    """
    Sliding window log rate limiter.

    Parameters
    ----------
    max_requests:
        Maximum number of requests allowed inside any window of
        ``window_seconds`` seconds.
    window_seconds:
        Size of the sliding window in seconds.
    """

    def __init__(self, max_requests: int, window_seconds: float) -> None:
        if max_requests <= 0:
            raise ValueError("max_requests must be > 0")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be > 0")

        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Timestamps of accepted requests, oldest first.
        self._log: deque[float] = deque()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def allow_request(self, now: Optional[float] = None) -> bool:
        """
        Decide whether to admit a new request.

        Parameters
        ----------
        now:
            Current time in seconds (float).  Defaults to ``time.time()``.
            Inject a value in tests to avoid real-time dependencies.

        Returns
        -------
        bool
            ``True``  – request is allowed and has been logged.
            ``False`` – rate limit exceeded; request is dropped.
        """
        t = time.time() if now is None else now
        self._evict(t)

        if len(self._log) >= self.max_requests:
            return False

        self._log.append(t)
        return True

    def current_count(self, now: Optional[float] = None) -> int:
        """Number of requests currently inside the window."""
        t = time.time() if now is None else now
        self._evict(t)
        return len(self._log)

    def time_until_next(self, now: Optional[float] = None) -> float:
        """
        Seconds until at least one slot opens up.

        Returns 0.0 if a request would be admitted right now.
        """
        t = time.time() if now is None else now
        self._evict(t)
        if len(self._log) < self.max_requests:
            return 0.0
        # The oldest entry in the log will expire at oldest_ts + window_seconds.
        return max(0.0, self._log[0] + self.window_seconds - t)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _evict(self, now: float) -> None:
        """Remove all log entries that are outside the current window."""
        cutoff = now - self.window_seconds
        # Pop from the left while the oldest timestamp is <= cutoff (expired).
        while self._log and self._log[0] <= cutoff:
            self._log.popleft()


# ---------------------------------------------------------------------------
# Legacy alias – kept so existing code that imports SlidingWindowRateLimiter
# continues to work unchanged.
# ---------------------------------------------------------------------------

class SlidingWindowRateLimiter(RateLimiter):
    """
    Backward-compatible alias for :class:`RateLimiter`.

    ``allow_request()`` here uses real wall-clock time (no ``now`` arg)
    so it works as a drop-in for the original interface.
    """

    def allow_request(self, now: Optional[float] = None) -> bool:  # type: ignore[override]
        return super().allow_request(now=now)

    def get_current_count(self) -> int:
        return self.current_count()
