import time
import threading
from collections import defaultdict


class SlidingWindowRateLimiter:
    """Thread-safe sliding window rate limiter.

    Tracks per-client request timestamps in a rolling window.
    All public methods are safe to call concurrently from multiple threads.
    """

    def __init__(self, max_requests: int, window_seconds: float):
        if max_requests <= 0:
            raise ValueError("max_requests must be > 0")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be > 0")
        self.max_requests = int(max_requests)
        self.window_seconds = float(window_seconds)
        self._requests: dict = defaultdict(list)  # client_id -> [timestamps]
        self._lock = threading.Lock()

    def _cleanup(self, client_id: str, now: float) -> None:
        """Prune timestamps outside the current window. Must hold _lock."""
        cutoff = now - self.window_seconds
        self._requests[client_id] = [
            ts for ts in self._requests[client_id] if ts > cutoff
        ]

    def is_allowed(self, client_id: str) -> bool:
        """Return True and record the request if the client is within quota."""
        now = time.time()
        with self._lock:
            self._cleanup(client_id, now)
            if len(self._requests[client_id]) < self.max_requests:
                self._requests[client_id].append(now)
                return True
            return False

    def get_remaining(self, client_id: str) -> int:
        """Return how many more requests the client can make in the current window."""
        now = time.time()
        with self._lock:
            self._cleanup(client_id, now)
            return self.max_requests - len(self._requests[client_id])

    def reset(self, client_id: str) -> None:
        """Clear the request log for a specific client."""
        with self._lock:
            self._requests[client_id] = []
