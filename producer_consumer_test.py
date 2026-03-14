"""Producer-consumer test for BoundedBlockingQueue.

- 3 producers
- 2 consumers

Run:
  python producer_consumer_test.py

This is a lightweight integration test (no external frameworks required).
"""

from __future__ import annotations

import threading
import time

from bounded_blocking_queue import BoundedBlockingQueue, QueueEmpty, QueueFull


def test_nowait_exceptions() -> None:
    q = BoundedBlockingQueue[int](maxsize=2)

    q.put_nowait(1)
    q.put_nowait(2)
    try:
        q.put_nowait(3)
        raise AssertionError("expected QueueFull")
    except QueueFull:
        pass

    assert q.get_nowait() == 1
    assert q.get_nowait() == 2
    try:
        q.get_nowait()
        raise AssertionError("expected QueueEmpty")
    except QueueEmpty:
        pass


def test_producer_consumer() -> None:
    NUM_PRODUCERS = 3
    NUM_CONSUMERS = 2
    ITEMS_PER_PRODUCER = 200

    q: BoundedBlockingQueue[object] = BoundedBlockingQueue(maxsize=5)  # small -> forces blocking
    sentinel = object()

    produced: set[int] = set()
    consumed: set[int] = set()
    produced_lock = threading.Lock()
    consumed_lock = threading.Lock()

    start = threading.Barrier(NUM_PRODUCERS + NUM_CONSUMERS)

    def producer(pid: int) -> None:
        start.wait()
        base = pid * ITEMS_PER_PRODUCER
        for i in range(ITEMS_PER_PRODUCER):
            item = base + i
            q.put(item)
            with produced_lock:
                produced.add(item)
            # tiny sleep helps interleaving, increasing contention
            if i % 17 == 0:
                time.sleep(0.001)

    def consumer() -> None:
        start.wait()
        while True:
            item = q.get()
            if item is sentinel:
                return
            assert isinstance(item, int)
            with consumed_lock:
                if item in consumed:
                    raise AssertionError(f"duplicate consume: {item}")
                consumed.add(item)

    producers = [threading.Thread(target=producer, args=(i,), name=f"producer-{i}") for i in range(NUM_PRODUCERS)]
    consumers = [threading.Thread(target=consumer, name=f"consumer-{i}") for i in range(NUM_CONSUMERS)]

    for t in producers + consumers:
        t.start()

    for t in producers:
        t.join()

    # shut down consumers
    for _ in range(NUM_CONSUMERS):
        q.put(sentinel)

    for t in consumers:
        t.join()

    expected = set(range(NUM_PRODUCERS * ITEMS_PER_PRODUCER))
    assert produced == expected, f"produced mismatch: {len(produced)} vs {len(expected)}"
    assert consumed == expected, f"consumed mismatch: {len(consumed)} vs {len(expected)}"
    assert q.qsize() == 0


if __name__ == "__main__":
    test_nowait_exceptions()
    test_producer_consumer()
    print("OK")
