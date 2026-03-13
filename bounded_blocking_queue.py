"""Thread-safe bounded blocking queue (built from scratch).

Requirements (per prompt):
- put(item): blocks if full
- get(): blocks if empty
- put_nowait(item): raises instead of blocking
- get_nowait(): raises instead of blocking

Implementation uses only threading primitives (Lock + Condition). No queue.Queue.
"""

from __future__ import annotations

import threading
from collections import deque
from typing import Deque, Generic, TypeVar


T = TypeVar("T")


class QueueFull(Exception):
    """Raised by put_nowait when the queue is at capacity."""


class QueueEmpty(Exception):
    """Raised by get_nowait when the queue is empty."""


class BoundedBlockingQueue(Generic[T]):
    """A fixed-capacity, thread-safe FIFO queue."""

    def __init__(self, maxsize: int) -> None:
        if maxsize <= 0:
            raise ValueError("maxsize must be a positive integer")

        self._maxsize = maxsize
        self._buf: Deque[T] = deque()

        self._lock = threading.Lock()
        self._not_full = threading.Condition(self._lock)
        self._not_empty = threading.Condition(self._lock)

    # --- blocking API ---

    def put(self, item: T) -> None:
        """Put *item* into the queue, blocking while the queue is full."""
        with self._not_full:
            while len(self._buf) >= self._maxsize:
                self._not_full.wait()
            self._buf.append(item)
            self._not_empty.notify()

    def get(self) -> T:
        """Remove and return the oldest item, blocking while the queue is empty."""
        with self._not_empty:
            while not self._buf:
                self._not_empty.wait()
            item = self._buf.popleft()
            self._not_full.notify()
            return item

    # --- non-blocking API ---

    def put_nowait(self, item: T) -> None:
        """Put *item* into the queue or raise QueueFull immediately."""
        with self._lock:
            if len(self._buf) >= self._maxsize:
                raise QueueFull(f"queue is full (maxsize={self._maxsize})")
            self._buf.append(item)
            self._not_empty.notify()

    def get_nowait(self) -> T:
        """Get an item from the queue or raise QueueEmpty immediately."""
        with self._lock:
            if not self._buf:
                raise QueueEmpty("queue is empty")
            item = self._buf.popleft()
            self._not_full.notify()
            return item

    # --- helpers ---

    def qsize(self) -> int:
        with self._lock:
            return len(self._buf)

    def empty(self) -> bool:
        return self.qsize() == 0

    def full(self) -> bool:
        with self._lock:
            return len(self._buf) >= self._maxsize

    @property
    def maxsize(self) -> int:
        return self._maxsize

    def __repr__(self) -> str:
        with self._lock:
            return f"BoundedBlockingQueue(maxsize={self._maxsize}, size={len(self._buf)})"
