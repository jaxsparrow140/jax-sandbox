"""Thread-safe bounded blocking queue using only threading primitives."""

import threading
from collections import deque


class QueueFull(Exception):
    """Raised by put_nowait when the queue is full."""


class QueueEmpty(Exception):
    """Raised by get_nowait when the queue is empty."""


class BoundedBlockingQueue:
    def __init__(self, maxsize: int):
        if maxsize <= 0:
            raise ValueError("maxsize must be a positive integer")
        self._maxsize = maxsize
        self._queue: deque = deque()
        self._lock = threading.Lock()
        self._not_full = threading.Condition(self._lock)
        self._not_empty = threading.Condition(self._lock)

    def put(self, item, timeout=None):
        """Block until space is available, then enqueue item."""
        with self._not_full:
            while len(self._queue) >= self._maxsize:
                self._not_full.wait(timeout=timeout)
                if len(self._queue) >= self._maxsize and timeout is not None:
                    raise QueueFull("timed out waiting for space")
            self._queue.append(item)
            self._not_empty.notify()

    def get(self, timeout=None):
        """Block until an item is available, then dequeue and return it."""
        with self._not_empty:
            while len(self._queue) == 0:
                self._not_empty.wait(timeout=timeout)
                if len(self._queue) == 0 and timeout is not None:
                    raise QueueEmpty("timed out waiting for item")
            item = self._queue.popleft()
            self._not_full.notify()
            return item

    def put_nowait(self, item):
        """Enqueue item immediately or raise QueueFull."""
        with self._lock:
            if len(self._queue) >= self._maxsize:
                raise QueueFull("queue is full")
            self._queue.append(item)
            self._not_empty.notify()

    def get_nowait(self):
        """Dequeue and return an item immediately or raise QueueEmpty."""
        with self._lock:
            if len(self._queue) == 0:
                raise QueueEmpty("queue is empty")
            item = self._queue.popleft()
            self._not_full.notify()
            return item

    def qsize(self) -> int:
        with self._lock:
            return len(self._queue)

    def empty(self) -> bool:
        with self._lock:
            return len(self._queue) == 0

    def full(self) -> bool:
        with self._lock:
            return len(self._queue) >= self._maxsize
