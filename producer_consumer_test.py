"""Producer-consumer test: 3 producers, 2 consumers."""

import threading
import time
from bounded_queue import BoundedQueue, QueueEmpty, QueueFull


def test_exceptions():
    """Test put_nowait/get_nowait exceptions."""
    print("\n=== Testing exceptions ===")
    q = BoundedQueue(2)
    
    q.put_nowait(1)
    q.put_nowait(2)
    
    try:
        q.put_nowait(3)
        print("FAIL: Should raise QueueFull")
        return False
    except QueueFull:
        print("✓ QueueFull raised correctly")
    
    q.get_nowait()
    q.get_nowait()
    
    try:
        q.get_nowait()
        print("FAIL: Should raise QueueEmpty")
        return False
    except QueueEmpty:
        print("✓ QueueEmpty raised correctly")
    
    return True


def test_producer_consumer():
    """3 producers, 2 consumers."""
    print("\n=== Producer-Consumer Test ===")
    
    queue = BoundedQueue(5)
    produced_count = 0
    consumed_count = 0
    producers_done = False
    
    def producer(pid):
        for i in range(5):
            item = f"P{pid}-{i}"
            queue.put(item)
            nonlocal produced_count
            produced_count += 1
            print(f"[Producer {pid}] Put: {item}")
            time.sleep(0.05)
    
    def consumer(cid):
        while True:
            try:
                item = queue.get(timeout=0.3)
                nonlocal consumed_count
                consumed_count += 1
                print(f"[Consumer {cid}] Got: {item}")
                time.sleep(0.05)
            except:
                if producers_done and queue.empty():
                    break
    
    # Start 3 producers
    producers = [threading.Thread(target=producer, args=(i,)) for i in range(3)]
    
    # Start 2 consumers
    consumers = [threading.Thread(target=consumer, args=(i,)) for i in range(2)]
    
    # Start all
    for p in producers:
        p.start()
    for c in consumers:
        c.start()
    
    # Wait for producers to finish
    for p in producers:
        p.join()
    
    producers_done = True
    print("[Main] Producers done, waiting for consumers...")
    
    # Wait for consumers
    for c in consumers:
        c.join()
    
    print(f"\n=== Results ===")
    print(f"Produced: {produced_count}")
    print(f"Consumed: {consumed_count}")
    print(f"Queue remaining: {queue.size()}")
    
    return produced_count == 15 and consumed_count == 15


if __name__ == "__main__":
    if test_exceptions() and test_producer_consumer():
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Tests failed")
        exit(1)