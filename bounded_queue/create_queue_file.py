"""
Script to create bounded_queue.py with correct content.
"""

import os

# Define the content of bounded_queue.py
content = '''"""
Thread-safe bounded blocking queue implementation using only threading primitives.
No queue.Queue allowed.
"""

import threading
import time

class BoundedBlockingQueue:
    """
    A thread-safe bounded blocking queue.
    Supports:
    - put(item): blocks if queue is full
    - get(): blocks if queue is empty
    - put_nowait(item): raises Full exception if queue is full
    - get_nowait(): raises Empty exception if queue is empty
    """
    
    class Empty(Exception):
        """Exception raised when get() or get_nowait() is called on an empty queue."""
        pass
    
    class Full(Exception):
        """Exception raised when put() or put_nowait() is called on a full queue."""
        pass
    
    def __init__(self, maxsize):
        """Initialize the queue with a maximum size."""
        self.maxsize = maxsize
        self.queue = []
        self._mutex = threading.Lock()
        self._not_empty = threading.Condition(self._mutex)
        self._not_full = threading.Condition(self._mutex)
    
    def put(self, item, block=True, timeout=None):
        """Put an item into the queue.
        
        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until a free slot is available.
        If 'timeout' is a positive number, it blocks at most 'timeout' seconds and raises
        the Full exception if no free slot was available within that time.
        Otherwise ('block' is false), put an item on the queue if a free slot is
        immediately available, else raise the Full exception.
        """
        with self._not_full:
            if block:
                if timeout is None:
                    while len(self.queue) >= self.maxsize:
                        self._not_full.wait()
                else:
                    end_time = time.time() + timeout
                    while len(self.queue) >= self.maxsize:
                        remaining = end_time - time.time()
                        if remaining <= 0.0:
                            raise self.Full
                        self._not_full.wait(remaining)
                self.queue.append(item)
                self._not_empty.notify()
            else:
                if len(self.queue) >= self.maxsize:
                    raise self.Full
                self.queue.append(item)
                self._not_empty.notify()
    
    def put_nowait(self, item):
        """Put an item into the queue without blocking.
        
        If no free slot is immediately available, raise the Full exception.
        """
        return self.put(item, block=False)
    
    def get(self, block=True, timeout=None):
        """Remove and return an item from the queue.
        
        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until an item is available.
        If 'timeout' is a positive number, it blocks at most 'timeout' seconds and raises
        the Empty exception if no item was available within that time.
        Otherwise ('block' is false), get an item if one is immediately available, else
        raise the Empty exception.
        """
        with self._not_empty:
            if block:
                if timeout is None:
                    while len(self.queue) == 0:
                        self._not_empty.wait()
                else:
                    end_time = time.time() + timeout
                    while len(self.queue) == 0:
                        remaining = end_time - time.time()
                        if remaining <= 0.0:
                            raise self.Empty
                        self._not_empty.wait(remaining)
                item = self.queue.pop(0)
                self._not_full.notify()
                return item
            else:
                if len(self.queue) == 0:
                    raise self.Empty
                item = self.queue.pop(0)
                self._not_full.notify()
                return item
    
    def get_nowait(self):
        """Remove and return an item from the queue without blocking.
        
        If no item is immediately available, raise the Empty exception.
        """
        return self.get(block=False)
    
    def qsize(self):
        """Return the approximate size of the queue."""
        with self._mutex:
            return len(self.queue)
    
    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        with self._mutex:
            return len(self.queue) == 0
    
    def full(self):
        """Return True if the queue is full, False otherwise."""
        with self._mutex:
            return len(self.queue) >= self.maxsize"""
'''

# Create the directory if it doesn't exist
os.makedirs(os.path.expanduser("~/jax-sandbox/bounded_queue"), exist_ok=True)

# Write the content to the file
with open(os.path.expanduser("~/jax-sandbox/bounded_queue/bounded_queue.py"), "w") as f:
    f.write(content)

print("bounded_queue.py created successfully!")"""}}