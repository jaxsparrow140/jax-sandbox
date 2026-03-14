"""
Producer-consumer test for BoundedBlockingQueue with 3 producers and 2 consumers.
"""

import threading
import time
import random
from queue import BoundedBlockingQueue

def producer(queue, producer_id, num_items):
    """Producer function that puts items into the queue."""
    for i in range(num_items):
        item = f"producer-{producer_id}-item-{i}"
        # Random delay to simulate variable production rates
        time.sleep(random.uniform(0.1, 0.5))
        queue.put(item)
        print(f"Producer {producer_id} put: {item}")
    print(f"Producer {producer_id} finished")

def consumer(queue, consumer_id):
    """Consumer function that gets items from the queue."""
    while True:
        try:
            # Random delay to simulate variable consumption rates
            time.sleep(random.uniform(0.1, 0.7))
            item = queue.get(timeout=2)
            print(f"Consumer {consumer_id} got: {item}")
            # Simulate work
            time.sleep(random.uniform(0.1, 0.3))
        except Exception as e:
            # Timeout or other exception - consumer stops
            print(f"Consumer {consumer_id} stopping: {e}")
            break

def main():
    # Create a bounded blocking queue with max size of 5
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
    # We'll wait for a reasonable time for all items to be processed
    time.sleep(5)
    
    # Print final queue status
    print(f"Final queue size: {queue.qsize()}")
    print("All producers finished, test complete")

if __name__ == "__main__":
    main()