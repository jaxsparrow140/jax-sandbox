import threading
from collections import deque


class QueueFull(Exception):
    pass


class QueueEmpty(Exception):
    pass


class BoundedBlockingQueue:
    def __init__(self, maxsize: int):
        self._maxsize = maxsize
        self._queue = deque()
        self._lock = threading.Lock()
        self._not_full = threading.Condition(self._lock)
        self._not_empty = threading.Condition(self._lock)

    def put(self, item):
        with self._not_full:
            while len(self._queue) >= self._maxsize:
                self._not_full.wait()
            self._queue.append(item)
            self._not_empty.notify()

    def get(self):
        with self._not_empty:
            while len(self._queue) == 0:
                self._not_empty.wait()
            item = self._queue.popleft()
            self._not_full.notify()
            return item

    def put_nowait(self, item):
        with self._lock:
            if len(self._queue) >= self._maxsize:
                raise QueueFull("Queue is full")
            self._queue.append(item)
            self._not_empty.notify()

    def get_nowait(self):
        with self._lock:
            if len(self._queue) == 0:
                raise QueueEmpty("Queue is empty")
            item = self._queue.popleft()
            self._not_full.notify()
            return item
