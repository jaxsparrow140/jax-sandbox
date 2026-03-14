"""
Producer-consumer test for BoundedBlockingQueue.

Creates 3 producers and 2 consumers with a queue of size 5.
"""

import threading
import time
import random
from bounded_queue import BoundedBlockingQueue, Empty, Full

def producer(queue, producer_id, num_items):
    """Producer function that puts items into the queue."""
    for i in range(num_items):
        item = f"producer-{producer_id}-item-{i}"
        # Random delay to simulate variable production rates
        time.sleep(random.uniform(0.1, 0.5))
        try:
            queue.put(item)
            print(f"Producer {producer_id} put: {item}")
        except Full:
            print(f"Producer {producer_id} failed to put: {item} (queue full)")

def consumer(queue, consumer_id):
    """Consumer function that gets items from the queue."""
    while True:
        try:
            # Random delay to simulate variable consumption rates
            time.sleep(random.uniform(0.1, 0.8))
            item = queue.get(timeout=1.0)
            print(f"Consumer {consumer_id} got: {item}")
        except Empty:
            print(f"Consumer {consumer_id} timed out waiting for items")
            break
        except Exception as e:
            print(f"Consumer {consumer_id} error: {e}")
            break

def main():
    # Create a bounded queue with max size of 5
    queue = BoundedBlockingQueue(maxsize=5)
    
    # Create 3 producer threads
    producer_threads = []
    for i in range(3):
        t = threading.Thread(target=producer, args=(queue, i+1, 10))
        producer_threads.append(t)
        t.start()
    
    # Create 2 consumer threads
    consumer_threads = []
    for i in range(2):
        t = threading.Thread(target=consumer, args=(queue, i+1))
        consumer_threads.append(t)
        t.start()
    
    # Wait for all producers to finish
    for t in producer_threads:
        t.join()
    
    # Let consumers run for a bit longer to clear the queue
    time.sleep(5)
    
    # Stop consumers (they'll exit when queue is empty and timeout occurs)
    for t in consumer_threads:
        t.join()
    
    print("All producers and consumers finished.")
    print(f"Final queue size: {queue.qsize()}")

if __name__ == "__main__":
    main()"""}}