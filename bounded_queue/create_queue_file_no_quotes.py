import os

# Define the content as a string without triple quotes
content = '''
Thread-safe bounded blocking queue implementation using only threading primitives.
No queue.Queue allowed.

import threading
import time

class BoundedBlockingQueue:
    class Empty(Exception):
        pass
    
    class Full(Exception):
        pass
    
    def __init__(self, maxsize):
        self.maxsize = maxsize
        self.queue = []
        self._mutex = threading.Lock()
        self._not_empty = threading.Condition(self._mutex)
        self._not_full = threading.Condition(self._mutex)
    
    def put(self, item, block=True, timeout=None):
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
        return self.put(item, block=False)
    
    def get(self, block=True, timeout=None):
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
        return self.get(block=False)
    
    def qsize(self):
        with self._mutex:
            return len(self.queue)
    
    def empty(self):
        with self._mutex:
            return len(self.queue) == 0
    
    def full(self):
        with self._mutex:
            return len(self.queue) >= self.maxsize'''

# Create the directory if it doesn't exist
os.makedirs(os.path.expanduser("~/jax-sandbox/bounded_queue"), exist_ok=True)

# Write the content to the file
with open(os.path.expanduser("~/jax-sandbox/bounded_queue/bounded_queue.py"), "w") as f:
    f.write(content)

print("bounded_queue.py created successfully!")"""}}