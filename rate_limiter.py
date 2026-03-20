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
        """Remove timestamps outside the current window.

        Must be called with self._lock already held.
        """
        cutoff = time.time() - self.window_seconds
        self._requests[client_id] = [
            ts for ts in self._requests[client_id] if ts > cutoff
        ]

    def is_allowed(self, client_id: str) -> bool:
        """Check if a request is allowed and record it if so.

        The check and the append are performed atomically under the lock,
        eliminating the TOCTOU race where multiple threads could each observe
        count < max_requests and all append before any of them incremented the
        shared count.
        """
        with self._lock:
            self._cleanup_old_requests(client_id)
            current_count = len(self._requests[client_id])
            if current_count < self.max_requests:
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
