"""
Thread-safe bounded blocking queue implementation using threading primitives.
No queue.Queue allowed - only raw threading primitives.
"""

import threading
from typing import Any, Optional


class BoundedBlockingQueue:
    """
    A thread-safe bounded blocking queue using threading primitives.
    
    - put(item): blocks if queue is full
    - get(): blocks if queue is empty
    - put_nowait(item): raises QueueFull exception if queue is full
    - get_nowait(): raises QueueEmpty exception if queue is empty
    """
    
    def __init__(self, maxsize: int):
        if maxsize <= 0:
            raise ValueError("maxsize must be positive")
        
        self._maxsize = maxsize
        self._queue = []
        
        # Mutex for protecting shared state
        self._mutex = threading.Lock()
        
        # Condition variable for waiting when queue is empty (for consumers)
        self._not_empty = threading.Condition(self._mutex)
        
        # Condition variable for waiting when queue is full (for producers)
        self._not_full = threading.Condition(self._mutex)
    
    def put(self, item: Any) -> None:
        """
        Put an item into the queue.
        Blocks if the queue is full until space becomes available.
        """
        with self._not_full:
            # Wait while queue is at capacity
            while len(self._queue) >= self._maxsize:
                self._not_full.wait()
            # Append and notify while still holding the lock
            self._queue.append(item)
            self._not_empty.notify()
    
    def get(self, timeout: Optional[float] = None) -> Any:
        """
        Get an item from the queue.
        Blocks if the queue is empty until an item becomes available.
        If timeout is provided, blocks at most timeout seconds.
        Returns None if timeout expires.
        """
        with self._not_empty:
            # Wait while queue is empty
            while len(self._queue) == 0:
                if timeout is not None:
                    if not self._not_empty.wait(timeout):
                        return None  # Timeout expired
                else:
                    self._not_empty.wait()
            # Pop and notify while still holding the lock
            item = self._queue.pop(0)  # FIFO
            self._not_full.notify()
        
        return item
    
    def put_nowait(self, item: Any) -> None:
        """
        Put an item into the queue without blocking.
        Raises QueueFull if the queue is full.
        """
        with self._mutex:
            if len(self._queue) >= self._maxsize:
                raise QueueFull("Queue is full")
            self._queue.append(item)
    
    def get_nowait(self) -> Any:
        """
        Get an item from the queue without blocking.
        Raises QueueEmpty if the queue is empty.
        """
        with self._mutex:
            if len(self._queue) == 0:
                raise QueueEmpty("Queue is empty")
            item = self._queue.pop(0)
            return item
    
    def size(self) -> int:
        """Return current size of the queue."""
        with self._mutex:
            return len(self._queue)


class QueueFull(Exception):
    """Exception raised when put_nowait is called on a full queue."""
    pass


class QueueEmpty(Exception):
    """Exception raised when get_nowait is called on an empty queue."""
    pass



# Backwards-compatible alias
BoundedQueue = BoundedBlockingQueue

# ============================================================================
# Producer-Consumer Test
# ============================================================================

def test_producer_consumer():
    """
    Test the bounded queue with 3 producers and 2 consumers.
    Uses blocking put() and get() operations.
    """
    import time
    
    queue = BoundedBlockingQueue(maxsize=5)
    produced_items = []
    consumed_items = []
    num_producers = 3
    num_consumers = 2
    
    # Each producer produces 5 items
    all_items = [[f"P{i}-{j}" for j in range(5)] for i in range(num_producers)]
    
    def producer(pid: int, items: list):
        """Producer thread that adds items to the queue."""
        for item in items:
            queue.put(item)  # Blocking put
            produced_items.append(item)
        print(f"[Producer {pid}] finished: {len(items)} items")
    
    def consumer(cid: int, stop_event: threading.Event):
        """Consumer thread that consumes items from the queue."""
        count = 0
        while not stop_event.is_set():
            try:
                # Use blocking get with timeout to allow checking stop_event
                item = queue.get(timeout=0.1)  # Blocking get with timeout
                if item is not None:
                    consumed_items.append(item)
                    count += 1
                    print(f"[Consumer {cid}] consumed: {item}")
            except Exception as e:
                print(f"[Consumer {cid}] error: {e}")
                break
        
        print(f"[Consumer {cid}] finished: consumed {count} items")
    
    # Use a stop event that gets set when all items are consumed
    stop_event = threading.Event()
    
    # Start consumers first
    consumer_threads = []
    for i in range(num_consumers):
        t = threading.Thread(target=consumer, args=(i, stop_event))
        consumer_threads.append(t)
        t.start()
    
    # Start producers
    producer_threads = []
    for i in range(num_producers):
        t = threading.Thread(target=producer, args=(i, all_items[i]))
        producer_threads.append(t)
        t.start()
    
    # Wait for all producers to finish
    for t in producer_threads:
        t.join()
    
    print("\nAll producers finished.")
    
    # Wait until all items are consumed
    while len(consumed_items) < 15:
        time.sleep(0.05)
    
    # Signal consumers to stop
    stop_event.set()
    
    # Wait for consumers to finish (they should exit quickly since stop_event is set)
    time.sleep(0.2)
    
    # Verify results
    print("\n=== Test Results ===")
    print(f"Total items produced: {len(produced_items)}")
    print(f"Total items consumed: {len(consumed_items)}")
    print(f"Items in queue: {queue.size()}")
    
    assert len(produced_items) == 15, f"Expected 15 produced items, got {len(produced_items)}"
    assert len(consumed_items) == 15, f"Expected 15 consumed items, got {len(consumed_items)}"
    
    print("\n✓ Test passed: All items were produced and consumed correctly!")
    
    # Test non-blocking operations
    print("\n=== Testing put_nowait / get_nowait ===")
    
    small_queue = BoundedBlockingQueue(maxsize=2)
    
    # Test put_nowait
    small_queue.put_nowait("item1")
    small_queue.put_nowait("item2")
    print("✓ put_nowait works for filling queue")
    
    # Test QueueFull exception
    try:
        small_queue.put_nowait("item3")
        print("✗ QueueFull exception not raised")
    except QueueFull:
        print("✓ QueueFull exception raised correctly")
    
    # Test get_nowait
    item1 = small_queue.get_nowait()
    item2 = small_queue.get_nowait()
    assert item1 == "item1"
    assert item2 == "item2"
    print("✓ get_nowait works for emptying queue")
    
    # Test QueueEmpty exception
    try:
        small_queue.get_nowait()
        print("✗ QueueEmpty exception not raised")
    except QueueEmpty:
        print("✓ QueueEmpty exception raised correctly")
    
    print("\n✓ All tests passed!")


if __name__ == "__main__":
    print("Starting bounded queue tests...\n")
    test_producer_consumer()
