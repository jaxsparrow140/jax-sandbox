"""
Thread-safe bounded blocking queue implementation using threading primitives.

This implementation provides:
- put(item): Blocks if queue is full
- get(): Blocks if queue is empty
- put_nowait(item): Raises Full exception if queue is full
- get_nowait(): Raises Empty exception if queue is empty
"""

import threading

class Empty(Exception):
    """Exception raised when get() or get_nowait() is called on an empty queue."""
    pass

class Full(Exception):
    """Exception raised when put() or put_nowait() is called on a full queue."""
    pass

class BoundedBlockingQueue:
    """A thread-safe bounded blocking queue."""
    
    def __init__(self, maxsize):
        """Initialize the queue with a maximum size."""
        self.maxsize = maxsize
        self.queue = []
        self.mutex = threading.Lock()
        self.not_empty = threading.Condition(self.mutex)
        self.not_full = threading.Condition(self.mutex)
        self.all_tasks_done = threading.Condition(self.mutex)
        self.unfinished_tasks = 0
    
    def qsize(self):
        """Return the approximate size of the queue."""
        with self.mutex:
            return len(self.queue)
    
    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        with self.mutex:
            return len(self.queue) == 0
    
    def full(self):
        """Return True if the queue is full, False otherwise."""
        with self.mutex:
            return len(self.queue) >= self.maxsize
    
    def put(self, item, block=True, timeout=None):
        """Put an item into the queue.
        
        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until a free slot is available.
        If 'timeout' is a positive number, it blocks at most 'timeout' seconds
        and raises the Full exception if no free slot was available within that time.
        Otherwise ('block' is false), put an item on the queue if a free slot
        is immediately available, else raise the Full exception.
        """
        with self.not_full:
            if self.maxsize > 0:
                if not block:
                    if len(self.queue) >= self.maxsize:
                        raise Full
                elif timeout is None:
                    while len(self.queue) >= self.maxsize:
                        self.not_full.wait()
                else:
                    if timeout < 0:
                        raise ValueError("'timeout' must be a non-negative number")
                    endtime = threading._time() + timeout
                    while len(self.queue) >= self.maxsize:
                        remaining = endtime - threading._time()
                        if remaining <= 0.0:
                            raise Full
                        self.not_full.wait(remaining)
            self.queue.append(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()
    
    def put_nowait(self, item):
        """Put an item into the queue without blocking.
        
        If no free slot is immediately available, raise the Full exception.
        """
        return self.put(item, block=False)
    
    def get(self, block=True, timeout=None):
        """Remove and return an item from the queue.
        
        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until an item is available.
        If 'timeout' is a positive number, it blocks at most 'timeout' seconds
        and raises the Empty exception if no item was available within that time.
        Otherwise ('block' is false), return an item if one is immediately
        available, else raise the Empty exception.
        """
        with self.not_empty:
            if not block:
                if len(self.queue) == 0:
                    raise Empty
            elif timeout is None:
                while len(self.queue) == 0:
                    self.not_empty.wait()
            else:
                if timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                endtime = threading._time() + timeout
                while len(self.queue) == 0:
                    remaining = endtime - threading._time()
                    if remaining <= 0.0:
                        raise Empty
                    self.not_empty.wait(remaining)
            item = self.queue.pop(0)
            self.not_full.notify()
            return item
    
    def get_nowait(self):
        """Remove and return an item from the queue without blocking.
        
        If no item is immediately available, raise the Empty exception.
        """
        return self.get(block=False)
    
    def task_done(self):
        """Indicate that a formerly enqueued task is complete.
        
        Used by queue consumers. For each get() used to fetch a task,
        a subsequent call to task_done() tells the queue that the processing
        on the task is complete.
        """
        with self.all_tasks_done:
            unfinished = self.unfinished_tasks - 1
            if unfinished <= 0:
                if unfinished < 0:
                    raise ValueError('task_done() called too many times')
                self.all_tasks_done.notify_all()
            self.unfinished_tasks = unfinished
    
    def join(self):
        """Block until all items in the queue have been gotten and processed.
        
        The count of unfinished tasks goes up whenever an item is added to the
        queue. The count goes down whenever a consumer thread calls task_done()
        to indicate that the item was retrieved and all work on it is complete.
        When the count of unfinished tasks drops to zero, join() unblocks.
        """
        with self.all_tasks_done:
            while self.unfinished_tasks:
                self.all_tasks_done.wait()