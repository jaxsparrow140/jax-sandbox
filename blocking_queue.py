"""
Thread-safe bounded blocking queue using only threading primitives.
No queue.Queue allowed.
"""

import threading


class Full(Exception):
    """Raised by put_nowait when the queue is full."""


class Empty(Exception):
    """Raised by get_nowait when the queue is empty."""


class BoundedBlockingQueue:
    """
    A fixed-capacity, thread-safe FIFO queue.

    - put(item)       blocks until space is available
    - get()           blocks until an item is available
    - put_nowait()    raises Full immediately if no space
    - get_nowait()    raises Empty immediately if no items
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        self._capacity = capacity
        self._buf: list = []
        self._lock = threading.Lock()
        # Signalled when an item is added (waiters: consumers)
        self._not_empty = threading.Condition(self._lock)
        # Signalled when an item is removed (waiters: producers)
        self._not_full = threading.Condition(self._lock)

    # ── core API ──────────────────────────────────────────────

    def put(self, item) -> None:
        """Block until space is available, then enqueue *item*."""
        with self._not_full:
            while len(self._buf) >= self._capacity:
                self._not_full.wait()
            self._buf.append(item)
            self._not_empty.notify()

    def get(self):
        """Block until an item is available, then dequeue and return it."""
        with self._not_empty:
            while len(self._buf) == 0:
                self._not_empty.wait()
            item = self._buf.pop(0)
            self._not_full.notify()
            return item

    def put_nowait(self, item) -> None:
        """Enqueue *item* if space is available; otherwise raise Full."""
        with self._lock:
            if len(self._buf) >= self._capacity:
                raise Full(f"queue is full (capacity={self._capacity})")
            self._buf.append(item)
            self._not_empty.notify()

    def get_nowait(self):
        """Dequeue an item if one exists; otherwise raise Empty."""
        with self._lock:
            if len(self._buf) == 0:
                raise Empty("queue is empty")
            item = self._buf.pop(0)
            self._not_full.notify()
            return item

    # ── introspection (all thread-safe) ───────────────────────

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
