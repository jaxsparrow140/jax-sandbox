import time
import threading
from collections import defaultdict


class SlidingWindowRateLimiter:
    """Thread-safe sliding window rate limiter."""

    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests = defaultdict(list)  # client_id -> [timestamps]
        self._lock = threading.Lock()

    def _cleanup_old_requests(self, client_id: str):
        """Remove timestamps outside the current window. Must be called with _lock held."""
        cutoff = time.time() - self.window_seconds
        self._requests[client_id] = [
            ts for ts in self._requests[client_id] if ts > cutoff
        ]

    def is_allowed(self, client_id: str) -> bool:
        """Check if a request is allowed and record it if so."""
        with self._lock:
            # Cleanup, check, and record must be atomic under one lock
            # acquisition. Without this, two threads can both pass the count
            # check before either appends its timestamp (TOCTOU race), causing
            # the per-client limit to be exceeded under concurrent load.
            self._cleanup_old_requests(client_id)
            if len(self._requests[client_id]) < self.max_requests:
                self._requests[client_id].append(time.time())
                return True
            return False

    def get_remaining(self, client_id: str) -> int:
        """Return number of requests remaining in current window."""
        with self._lock:
            self._cleanup_old_requests(client_id)
            return self.max_requests - len(self._requests[client_id])

    def reset(self, client_id: str):
        """Reset rate limit for a specific client."""
        with self._lock:
            self._requests[client_id] = []
