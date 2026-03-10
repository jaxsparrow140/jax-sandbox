"""Thread-safe bounded blocking queue.

Implements a minimal subset of queue.Queue semantics without using queue.Queue.

- put(item): blocks while the queue is full
- get(): blocks while the queue is empty
- put_nowait(item): raises QueueFull if the queue is full
- get_nowait(): raises QueueEmpty if the queue is empty

Only threading primitives are used.
"""

from __future__ import annotations

import threading
from collections import deque
from typing import Deque, Generic, TypeVar


T = TypeVar("T")


class QueueFull(Exception):
    """Raised by put_nowait when the queue is full."""


class QueueEmpty(Exception):
    """Raised by get_nowait when the queue is empty."""


class BoundedBlockingQueue(Generic[T]):
    def __init__(self, maxsize: int):
        if maxsize <= 0:
            raise ValueError("maxsize must be > 0")

        self._maxsize = maxsize
        self._queue: Deque[T] = deque()

        # Both conditions share the same underlying lock.
        self._lock = threading.Lock()
        self._not_full = threading.Condition(self._lock)
        self._not_empty = threading.Condition(self._lock)

    def put(self, item: T) -> None:
        """Put item into the queue, blocking if the queue is full."""
        with self._not_full:
            while len(self._queue) >= self._maxsize:
                self._not_full.wait()
            self._queue.append(item)
            # Wake one waiter on not_empty (if any).
            self._not_empty.notify()

    def get(self) -> T:
        """Remove and return an item, blocking if the queue is empty."""
        with self._not_empty:
            while not self._queue:
                self._not_empty.wait()
            item = self._queue.popleft()
            # Wake one waiter on not_full (if any).
            self._not_full.notify()
            return item

    def put_nowait(self, item: T) -> None:
        """Put item into the queue without blocking.

        Raises:
            QueueFull: if the queue is full.
        """
        with self._lock:
            if len(self._queue) >= self._maxsize:
                raise QueueFull("Queue is full")
            self._queue.append(item)
            self._not_empty.notify()

    def get_nowait(self) -> T:
        """Get an item from the queue without blocking.

        Raises:
            QueueEmpty: if the queue is empty.
        """
        with self._lock:
            if not self._queue:
                raise QueueEmpty("Queue is empty")
            item = self._queue.popleft()
            self._not_full.notify()
            return item

    def qsize(self) -> int:
        """Return the approximate size of the queue."""
        with self._lock:
            return len(self._queue)

    def empty(self) -> bool:
        with self._lock:
            return not self._queue

    def full(self) -> bool:
        with self._lock:
            return len(self._queue) >= self._maxsize
