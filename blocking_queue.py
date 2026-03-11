"""Thread-safe bounded blocking queue using only threading primitives.

No queue.Queue allowed — built from Lock, Condition, and a collections.deque.
"""

import threading
from collections import deque


class Full(Exception):
    """Raised by put_nowait when the queue is at capacity."""


class Empty(Exception):
    """Raised by get_nowait when the queue has no items."""


class BoundedBlockingQueue:
    """A fixed-capacity, thread-safe FIFO queue.

    - put(item)       blocks the caller until space is available.
    - get()           blocks the caller until an item is available.
    - put_nowait(item) raises Full immediately if the queue is at capacity.
    - get_nowait()     raises Empty immediately if the queue is empty.
    """

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        self._capacity = capacity
        self._buf: deque = deque()
        self._lock = threading.Lock()
        # Condition for "not full" — producers wait here
        self._not_full = threading.Condition(self._lock)
        # Condition for "not empty" — consumers wait here
        self._not_empty = threading.Condition(self._lock)

    # ---- blocking API ----

    def put(self, item: object) -> None:
        """Add *item* to the queue, blocking until space is available."""
        with self._not_full:
            while len(self._buf) >= self._capacity:
                self._not_full.wait()
            self._buf.append(item)
            self._not_empty.notify()

    def get(self) -> object:
        """Remove and return the oldest item, blocking until one exists."""
        with self._not_empty:
            while not self._buf:
                self._not_empty.wait()
            item = self._buf.popleft()
            self._not_full.notify()
            return item

    # ---- non-blocking API ----

    def put_nowait(self, item: object) -> None:
        """Add *item* immediately or raise Full."""
        with self._lock:
            if len(self._buf) >= self._capacity:
                raise Full(
                    f"queue is full (capacity={self._capacity})"
                )
            self._buf.append(item)
            self._not_empty.notify()

    def get_nowait(self) -> object:
        """Remove and return the oldest item immediately or raise Empty."""
        with self._lock:
            if not self._buf:
                raise Empty("queue is empty")
            item = self._buf.popleft()
            self._not_full.notify()
            return item

    # ---- introspection (all lock-protected) ----

    def qsize(self) -> int:
        with self._lock:
            return len(self._buf)

    @property
    def capacity(self) -> int:
        return self._capacity

    def __repr__(self) -> str:
        with self._lock:
            return (
                f"BoundedBlockingQueue(capacity={self._capacity}, "
                f"size={len(self._buf)})"
            )
