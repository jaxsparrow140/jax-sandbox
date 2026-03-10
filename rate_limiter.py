"""rate_limiter.py

Sliding Window Log rate limiter.

Algorithm (sliding window log):
- Keep a log of timestamps for *accepted* requests.
- Before each decision, prune timestamps older than the window.
- Allow if the remaining count is < N.

This implementation is safe under bursts (many requests at the same timestamp)
and is testable without sleeping by passing an explicit `now`.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from typing import Callable, Deque, Optional


class SlidingWindowLogRateLimiter:
    """Allow at most `max_requests` per `window_seconds` using a sliding window log."""

    def __init__(
        self,
        max_requests: int,
        window_seconds: float,
        *,
        time_func: Optional[Callable[[], float]] = None,
    ) -> None:
        if max_requests <= 0:
            raise ValueError("max_requests must be > 0")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be > 0")

        self.max_requests = int(max_requests)
        self.window_seconds = float(window_seconds)
        self._time = time_func or time.monotonic

        self._log: Deque[float] = deque()
        self._lock = threading.Lock()

    def _prune(self, now: float) -> None:
        cutoff = now - self.window_seconds
        while self._log and self._log[0] <= cutoff:
            self._log.popleft()

    def allow_request(self, now: Optional[float] = None) -> bool:
        """Return True if the request is allowed; otherwise False.

        Parameters
        ----------
        now:
            Timestamp (seconds) to use for the decision. If omitted, uses the
            injected `time_func` (defaults to `time.monotonic`).
        """
        if now is None:
            now = self._time()

        with self._lock:
            self._prune(now)
            if len(self._log) < self.max_requests:
                self._log.append(now)
                return True
            return False

    def current_count(self, now: Optional[float] = None) -> int:
        """Number of accepted requests currently in the window."""
        if now is None:
            now = self._time()

        with self._lock:
            self._prune(now)
            return len(self._log)

    def reset(self) -> None:
        """Clear all recorded timestamps."""
        with self._lock:
            self._log.clear()

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"{self.__class__.__name__}(max_requests={self.max_requests}, "
            f"window_seconds={self.window_seconds})"
        )


class RateLimiter(SlidingWindowLogRateLimiter):
    """Backward-compatible alias for `SlidingWindowLogRateLimiter`."""
