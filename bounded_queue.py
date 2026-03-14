"""
Thread-safe bounded blocking queue implementation using raw threading primitives.
No queue.Queue allowed - built from scratch with Lock, Condition, etc.
"""

import threading
from typing import Any, Optional
from collections import deque


class BoundedQueue:
    """
    A thread-safe bounded blocking queue.
    
    - put(item): Blocks if the queue is full
    - get(): Blocks if the queue is empty
    - put_nowait(item): Raises QueueFull exception instead of blocking
    - get_nowait(): Raises QueueEmpty exception instead of blocking
    """
    
    def __init__(self, maxsize: int):
        if maxsize <= 0:
            raise ValueError("maxsize must be positive")
        
        self._maxsize = maxsize
        self._queue = deque()
        
        # Lock for mutual exclusion
        self._lock = threading.Lock()
        
        # Condition for waiting on put (when queue is full)
        self._not_full = threading.Condition(self._lock)
        
        # Condition for waiting on get (when queue is empty)
        self._not_empty = threading.Condition(self._lock)
    
    def put(self, item: Any, timeout: Optional[float] = None) -> None:
        """
        Put an item into the queue.
        
        Blocks if the queue is full, waiting until space is available.
        """
        with self._not_full:
            while len(self._queue) >= self._maxsize:
                self._not_full.wait(timeout)
            
            self._queue.append(item)
            self._not_empty.notify()
    
    def get(self, timeout: Optional[float] = None) -> Any:
        """
        Remove and return an item from the queue.
        
        Blocks if the queue is empty, waiting until an item is available.
        """
        with self._not_empty:
            while len(self._queue) == 0:
                self._not_empty.wait(timeout)
            
            item = self._queue.popleft()
            self._not_full.notify()
            return item
    
    def put_nowait(self, item: Any) -> None:
        """
        Put an item into the queue without blocking.
        
        Raises QueueFull if the queue is full.
        """
        with self._lock:
            if len(self._queue) >= self._maxsize:
                raise QueueFull("Queue is full")
            
            self._queue.append(item)
            self._not_empty.notify()
    
    def get_nowait(self) -> Any:
        """
        Remove and return an item from the queue without blocking.
        
        Raises QueueEmpty if the queue is empty.
        """
        with self._lock:
            if len(self._queue) == 0:
                raise QueueEmpty("Queue is empty")
            
            item = self._queue.popleft()
            self._not_full.notify()
            return item
    
    def size(self) -> int:
        """Return current size of the queue."""
        with self._lock:
            return len(self._queue)
    
    def empty(self) -> bool:
        """Return True if queue is empty."""
        with self._lock:
            return len(self._queue) == 0
    
    def full(self) -> bool:
        """Return True if queue is full."""
        with self._lock:
            return len(self._queue) >= self._maxsize


class QueueEmpty(Exception):
    """Exception raised when get_nowait is called on an empty queue."""
    pass


class QueueFull(Exception):
    """Exception raised when put_nowait is called on a full queue."""
    pass


if __name__ == "__main__":
    # Basic sanity test
    q = BoundedQueue(2)
    
    q.put_nowait(1)
    q.put_nowait(2)
    
    try:
        q.put_nowait(3)  # Should raise QueueFull
        print("ERROR: Should have raised QueueFull")
    except QueueFull:
        print("✓ QueueFull raised correctly")
    
    assert q.get_nowait() == 1
    assert q.get_nowait() == 2
    
    try:
        q.get_nowait()  # Should raise QueueEmpty
        print("ERROR: Should have raised QueueEmpty")
    except QueueEmpty:
        print("✓ QueueEmpty raised correctly")
    
    print("✓ Basic sanity tests passed")