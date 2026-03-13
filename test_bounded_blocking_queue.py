"""Producer-consumer test for BoundedBlockingQueue."""

import threading
import time
from collections import defaultdict

from bounded_blocking_queue import BoundedBlockingQueue, QueueFull, QueueEmpty

NUM_PRODUCERS = 3
ITEMS_PER_PRODUCER = 10
TOTAL_ITEMS = NUM_PRODUCERS * ITEMS_PER_PRODUCER
NUM_CONSUMERS = 2
QUEUE_MAXSIZE = 5


def producer(q: BoundedBlockingQueue, producer_id: int, stats: dict, lock: threading.Lock):
    for i in range(ITEMS_PER_PRODUCER):
        item = f"P{producer_id}-{i}"
        q.put(item)
        with lock:
            stats[producer_id] += 1


def consumer(q: BoundedBlockingQueue, consumer_id: int, consumed: list,
             stats: dict, lock: threading.Lock, remaining: list):
    while True:
        with lock:
            if remaining[0] <= 0:
                return
        try:
            item = q.get(timeout=1.0)
        except QueueEmpty:
            continue
        with lock:
            consumed.append(item)
            stats[consumer_id] += 1
            remaining[0] -= 1


def test_producer_consumer():
    q = BoundedBlockingQueue(QUEUE_MAXSIZE)
    consumed = []
    producer_stats = defaultdict(int)
    consumer_stats = defaultdict(int)
    stats_lock = threading.Lock()
    remaining = [TOTAL_ITEMS]

    producers = []
    for pid in range(NUM_PRODUCERS):
        t = threading.Thread(target=producer, args=(q, pid, producer_stats, stats_lock))
        producers.append(t)

    consumers = []
    for cid in range(NUM_CONSUMERS):
        t = threading.Thread(target=consumer, args=(q, cid, consumed, consumer_stats, stats_lock, remaining))
        consumers.append(t)

    start = time.monotonic()
    for t in consumers:
        t.start()
    for t in producers:
        t.start()

    for t in producers:
        t.join()
    for t in consumers:
        t.join()
    elapsed = time.monotonic() - start

    # Verify correctness
    assert len(consumed) == TOTAL_ITEMS, f"Expected {TOTAL_ITEMS} items, got {len(consumed)}"
    assert len(set(consumed)) == TOTAL_ITEMS, "Duplicate items detected"

    # Verify each producer's items are all present
    for pid in range(NUM_PRODUCERS):
        expected = {f"P{pid}-{i}" for i in range(ITEMS_PER_PRODUCER)}
        actual = {item for item in consumed if item.startswith(f"P{pid}-")}
        assert expected == actual, f"Producer {pid} items mismatch"

    assert q.empty(), "Queue should be empty after consuming all items"

    # Print stats
    print(f"All {TOTAL_ITEMS} items produced and consumed in {elapsed:.3f}s")
    print(f"Queue maxsize: {QUEUE_MAXSIZE}")
    print("\nProducer stats:")
    for pid in range(NUM_PRODUCERS):
        print(f"  Producer {pid}: {producer_stats[pid]} items")
    print("\nConsumer stats:")
    for cid in range(NUM_CONSUMERS):
        print(f"  Consumer {cid}: {consumer_stats[cid]} items")
    print("\nAll assertions passed!")


def test_nowait_methods():
    q = BoundedBlockingQueue(2)

    # Test put_nowait / get_nowait
    q.put_nowait("a")
    q.put_nowait("b")
    assert q.full()
    try:
        q.put_nowait("c")
        assert False, "Should have raised QueueFull"
    except QueueFull:
        pass

    assert q.get_nowait() == "a"
    assert q.get_nowait() == "b"
    assert q.empty()
    try:
        q.get_nowait()
        assert False, "Should have raised QueueEmpty"
    except QueueEmpty:
        pass

    print("nowait method tests passed!")


def test_qsize():
    q = BoundedBlockingQueue(3)
    assert q.qsize() == 0
    q.put_nowait("x")
    assert q.qsize() == 1
    q.get_nowait()
    assert q.qsize() == 0
    print("qsize tests passed!")


if __name__ == "__main__":
    test_nowait_methods()
    test_qsize()
    test_producer_consumer()
