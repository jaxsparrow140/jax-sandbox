import time
import threading


class TTLCache:
    """Simple thread-safe cache with TTL expiration."""

    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self._store = {}
        self._lock = threading.Lock()

    def get(self, key: str):
        with self._lock:
            if key in self._store:
                value, expires_at = self._store[key]
                if time.time() < expires_at:
                    return value
                else:
                    del self._store[key]
        return None

    def set(self, key: str, value):
        expires_at = time.time() + self.ttl
        with self._lock:
            self._store[key] = (value, expires_at)

    def clear(self):
        with self._lock:          # ← was missing; this is the fix
            self._store.clear()   # in-place clear avoids reference aliasing
