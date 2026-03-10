"""
Sliding Window Log Rate Limiter

Implements the sliding window log algorithm:
- Keeps a log (sorted list) of timestamps for each request.
- On each new request, prune entries older than the window (M seconds).
- Allow the request only if the count of remaining entries < N.

Time complexity:  O(log n) amortized per request (bisect + deque pop)
Space complexity: O(N) — at most N timestamps kept per key
"""

import time
from collections import deque
from typing import Optional
import bisect


class RateLimiter:
    """
    Sliding-window-log rate limiter.

    Parameters
    ----------
    max_requests : int
        Maximum number of requests allowed within the window.
    window_seconds : float
        Length of the sliding window in seconds.
    """

    def __init__(self, max_requests: int, window_seconds: float) -> None:
        if max_requests <= 0:
            raise ValueError("max_requests must be > 0")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be > 0")

        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Deque of timestamps (floats, seconds since epoch).
        # Oldest entries are at the left, newest at the right.
        self._log: deque = deque()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def allow_request(self, now: Optional[float] = None) -> bool:
        """
        Decide whether a new request should be allowed.

        Parameters
        ----------
        now : float | None
            Current timestamp (seconds).  Defaults to ``time.time()``.
            Accepting an explicit timestamp makes the limiter fully
            testable without sleep().

        Returns
        -------
        bool
            True  → request is within the rate limit (and is recorded).
            False → request exceeds the rate limit (not recorded).
        """
        if now is None:
            now = time.time()

        # Evict timestamps that have fallen outside the window.
        cutoff = now - self.window_seconds
        while self._log and self._log[0] <= cutoff:
            self._log.popleft()

        if len(self._log) < self.max_requests:
            self._log.append(now)
            return True

        return False

    def current_count(self, now: Optional[float] = None) -> int:
        """Return the number of requests currently in the window."""
        if now is None:
            now = time.time()
        cutoff = now - self.window_seconds
        # Use bisect to count without mutating the deque.
        log_list = list(self._log)
        idx = bisect.bisect_right(log_list, cutoff)
        return len(log_list) - idx

    def reset(self) -> None:
        """Clear all recorded timestamps."""
        self._log.clear()

    def __repr__(self) -> str:
        return (
            f"RateLimiter(max_requests={self.max_requests}, "
            f"window_seconds={self.window_seconds})"
        )
