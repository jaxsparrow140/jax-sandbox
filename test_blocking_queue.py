"""
Producer-consumer test for BoundedBlockingQueue.

3 producers, 2 consumers, small queue capacity to force blocking.
Validates correctness: every produced item is consumed exactly once.
"""

import threading
import time
import random

from blocking_queue import BoundedBlockingQueue, Full, Empty

# ── configuration ─────────────────────────────────────────────

QUEUE_CAPACITY = 4          # small on purpose — forces blocking
NUM_PRODUCERS = 3
NUM_CONSUMERS = 2
ITEMS_PER_PRODUCER = 50     # each producer sends 50 items
TOTAL_ITEMS = NUM_PRODUCERS * ITEMS_PER_PRODUCER

# ── helpers ───────────────────────────────────────────────────

produced_lock = threading.Lock()
consumed_lock = threading.Lock()
produced: list[tuple[int, int]] = []   # (producer_id, seq)
consumed: list[tuple[int, int]] = []   # same tuples, collected by consumers


def producer(q: BoundedBlockingQueue, pid: int) -> None:
    """Produce ITEMS_PER_PRODUCER tagged items into *q*."""
    for seq in range(ITEMS_PER_PRODUCER):
        item = (pid, seq)
        q.put(item)
        with produced_lock:
            produced.append(item)
        # tiny jitter so threads actually interleave
        if random.random() < 0.1:
            time.sleep(random.uniform(0, 0.002))


def consumer(q: BoundedBlockingQueue, sentinel: object) -> None:
    """Consume items until *sentinel* is received."""
    while True:
        item = q.get()
        if item is sentinel:
            return
        with consumed_lock:
            consumed.append(item)
        if random.random() < 0.1:
            time.sleep(random.uniform(0, 0.002))


# ── main test ─────────────────────────────────────────────────

def test_producer_consumer() -> None:
    q = BoundedBlockingQueue(QUEUE_CAPACITY)
    sentinel = object()

    # start consumers first so they block waiting
    consumers = [
        threading.Thread(target=consumer, args=(q, sentinel), name=f"consumer-{i}")
        for i in range(NUM_CONSUMERS)
    ]
    for c in consumers:
        c.start()

    # start producers
    producers = [
        threading.Thread(target=producer, args=(q, pid), name=f"producer-{pid}")
        for pid in range(NUM_PRODUCERS)
    ]
    for p in producers:
        p.start()

    # wait for all producers to finish
    for p in producers:
        p.join()

    # send one sentinel per consumer to unblock them
    for _ in consumers:
        q.put(sentinel)

    for c in consumers:
        c.join()

    # ── assertions ────────────────────────────────────────────

    assert len(produced) == TOTAL_ITEMS, (
        f"expected {TOTAL_ITEMS} produced, got {len(produced)}"
    )
    assert len(consumed) == TOTAL_ITEMS, (
        f"expected {TOTAL_ITEMS} consumed, got {len(consumed)}"
    )
    # every item consumed exactly once
    assert sorted(produced) == sorted(consumed), (
        "produced and consumed item sets differ"
    )
    # queue should be drained
    assert q.qsize() == 0, f"queue not empty after test: {q.qsize()}"

    print(f"✓ {TOTAL_ITEMS} items produced and consumed correctly "
          f"({NUM_PRODUCERS}P / {NUM_CONSUMERS}C, capacity={QUEUE_CAPACITY})")


def test_nowait_raises() -> None:
    """put_nowait / get_nowait raise on boundary conditions."""
    q = BoundedBlockingQueue(2)

    # get_nowait on empty
    try:
        q.get_nowait()
        assert False, "expected Empty"
    except Empty:
        pass

    # fill it up
    q.put_nowait("a")
    q.put_nowait("b")

    # put_nowait on full
    try:
        q.put_nowait("c")
        assert False, "expected Full"
    except Full:
        pass

    # drain via nowait
    assert q.get_nowait() == "a"
    assert q.get_nowait() == "b"

    # empty again
    try:
        q.get_nowait()
        assert False, "expected Empty"
    except Empty:
        pass

    print("✓ put_nowait / get_nowait edge cases passed")


def test_blocking_semantics() -> None:
    """Verify that put blocks when full and get blocks when empty."""
    q = BoundedBlockingQueue(1)
    blocked = threading.Event()
    unblocked = threading.Event()

    # fill the queue
    q.put("x")

    def blocking_put():
        blocked.set()          # signal that we're about to block
        q.put("y")             # should block until consumer drains
        unblocked.set()

    t = threading.Thread(target=blocking_put)
    t.start()

    blocked.wait(timeout=2)
    # give the thread a moment to actually enter the wait
    time.sleep(0.05)
    assert not unblocked.is_set(), "put should be blocking but isn't"

    # drain one item — should unblock the producer
    assert q.get() == "x"
    unblocked.wait(timeout=2)
    assert unblocked.is_set(), "put didn't unblock after get"
    assert q.get() == "y"

    t.join()
    print("✓ blocking semantics verified")


def test_capacity_validation() -> None:
    """Zero or negative capacity should raise."""
    for bad in (0, -1, -100):
        try:
            BoundedBlockingQueue(bad)
            assert False, f"expected ValueError for capacity={bad}"
        except ValueError:
            pass
    print("✓ capacity validation passed")


# ── run ───────────────────────────────────────────────────────

if __name__ == "__main__":
    test_capacity_validation()
    test_nowait_raises()
    test_blocking_semantics()
    test_producer_consumer()
    print("\nAll tests passed.")
