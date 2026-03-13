"""
Test script for BoundedBlockingQueue with 3 producers and 2 consumers.
"""

import threading
import time
import random
from bounded_queue import BoundedBlockingQueue

def producer(queue, producer_id, num_items):
    """Producer function that adds items to the queue."""
    for i in range(num_items):
        item = f"item-{producer_id}-{i}"
        # Simulate some work before producing
        time.sleep(random.uniform(0.1, 0.5))
        queue.put(item)
        print(f"Producer {producer_id} put {item}")
    print(f"Producer {producer_id} finished")

def consumer(queue, consumer_id):
    """Consumer function that removes items from the queue."""
    while True:
        try:
            # Simulate some work before consuming
            time.sleep(random.uniform(0.1, 0.3))
            item = queue.get(timeout=1)
            print(f"Consumer {consumer_id} got {item}")
        except BoundedBlockingQueue.Empty:
            # Timeout occurred, check if we should continue
            # We'll let consumers run until all producers are done
            continue

def main():
    # Create a bounded queue with capacity of 5
    queue = BoundedBlockingQueue(maxsize=5)
    
    # Create producer threads
    producer_threads = []
    num_producers = 3
    items_per_producer = 5
    
    for i in range(num_producers):
        t = threading.Thread(target=producer, args=(queue, i+1, items_per_producer))
        producer_threads.append(t)
        t.start()
    
    # Create consumer threads
    consumer_threads = []
    num_consumers = 2
    
    for i in range(num_consumers):
        t = threading.Thread(target=consumer, args=(queue, i+1))
        consumer_threads.append(t)
        t.start()
    
    # Wait for all producers to finish
    for t in producer_threads:
        t.join()
    
    # Let consumers finish processing remaining items
    # We'll wait a bit longer for consumers to process all items
    time.sleep(2)
    
    # Since consumers run indefinitely, we'll stop them by setting a flag
    # But for this test, we'll just let them timeout and exit naturally
    print("All producers finished. Waiting for consumers to finish processing...")
    
    # Give consumers time to process remaining items
    time.sleep(3)
    
    print("Test completed.")

if __name__ == "__main__":
    main()"""}}