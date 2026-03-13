"""
Test script for BoundedBlockingQueue with 3 producers and 2 consumers.
"""

import threading
import time
import random
from bounded_queue import BoundedBlockingQueue, Empty, Full

def producer(queue, producer_id, num_items):
    """Producer function that adds items to the queue."""
    for i in range(num_items):
        item = f"producer-{producer_id}-item-{i}"
        # Random delay to simulate varying production rates
        time.sleep(random.uniform(0.1, 0.5))
        try:
            queue.put(item)
            print(f"Producer {producer_id} put: {item}")
        except Full:
            print(f"Producer {producer_id} failed to put {item}: queue full")

def consumer(queue, consumer_id):
    """Consumer function that removes items from the queue."""
    while True:
        try:
            # Random delay to simulate varying consumption rates
            time.sleep(random.uniform(0.1, 0.7))
            item = queue.get()
            print(f"Consumer {consumer_id} got: {item}")
            # Simulate some work
            time.sleep(random.uniform(0.1, 0.5))
            queue.task_done()
        except Empty:
            print(f"Consumer {consumer_id} found queue empty, exiting")
            break

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
    
    # Wait for all items to be processed
    queue.join()
    
    # Signal consumers to exit (by putting None values)
    for _ in range(num_consumers):
        queue.put(None)
    
    # Wait for all consumers to finish
    for t in consumer_threads:
        t.join()
    
    print("All producers and consumers have finished.")

if __name__ == "__main__":
    main()