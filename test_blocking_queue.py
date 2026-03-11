"""Producer-consumer test for BoundedBlockingQueue.

3 producers, 2 consumers, small queue capacity to force contention.
Also includes unit tests for the nowait variants and edge cases.
"""

import threading
import time
import unittest

from blocking_queue import BoundedBlockingQueue, Empty, Full


# ---------------------------------------------------------------------------
# Producer-consumer integration test
# ---------------------------------------------------------------------------

class TestProducerConsumer(unittest.TestCase):
    """3 producers each push ITEMS_PER_PRODUCER items into a tiny queue;
    2 consumers drain it.  At the end every item must appear exactly once."""

    ITEMS_PER_PRODUCER = 200
    NUM_PRODUCERS = 3
    NUM_CONSUMERS = 2
    QUEUE_CAPACITY = 5  # deliberately small → lots of blocking

    def test_all_items_transferred(self) -> None:
        q: BoundedBlockingQueue = BoundedBlockingQueue(self.QUEUE_CAPACITY)
        sentinel = object()  # poison pill

        produced: list[list[int]] = [[] for _ in range(self.NUM_PRODUCERS)]
        consumed: list[list[int]] = [[] for _ in range(self.NUM_CONSUMERS)]

        def producer(pid: int) -> None:
            for i in range(self.ITEMS_PER_PRODUCER):
                item = pid * self.ITEMS_PER_PRODUCER + i
                q.put(item)
                produced[pid].append(item)
            # each producer sends one sentinel so consumers can shut down
            # (we'll send exactly NUM_CONSUMERS sentinels total — see below)

        def consumer(cid: int) -> None:
            while True:
                item = q.get()
                if item is sentinel:
                    return
                consumed[cid].append(item)

        # --- launch threads ---
        producers = [
            threading.Thread(target=producer, args=(i,), name=f"prod-{i}")
            for i in range(self.NUM_PRODUCERS)
        ]
        consumers = [
            threading.Thread(target=consumer, args=(i,), name=f"cons-{i}")
            for i in range(self.NUM_CONSUMERS)
        ]

        for t in consumers + producers:
            t.start()

        # wait for producers to finish, then inject poison pills
        for t in producers:
            t.join()
        for _ in range(self.NUM_CONSUMERS):
            q.put(sentinel)
        for t in consumers:
            t.join()

        # --- assertions ---
        all_produced = sorted(v for sub in produced for v in sub)
        all_consumed = sorted(v for sub in consumed for v in sub)

        expected = sorted(range(self.NUM_PRODUCERS * self.ITEMS_PER_PRODUCER))
        self.assertEqual(all_produced, expected, "producers missed items")
        self.assertEqual(all_consumed, expected, "consumers missed items")

        # queue should be empty
        self.assertEqual(q.qsize(), 0)


# ---------------------------------------------------------------------------
# Unit tests for blocking & non-blocking behaviour
# ---------------------------------------------------------------------------

class TestBlockingBehavior(unittest.TestCase):
    """Verify that put blocks when full and get blocks when empty."""

    def test_get_blocks_on_empty(self) -> None:
        q = BoundedBlockingQueue(2)
        result: list = []

        def delayed_put() -> None:
            time.sleep(0.1)
            q.put("hello")

        threading.Thread(target=delayed_put).start()
        result.append(q.get())  # should block ~100 ms then return
        self.assertEqual(result, ["hello"])

    def test_put_blocks_on_full(self) -> None:
        q = BoundedBlockingQueue(1)
        q.put("a")  # fills the queue

        unblocked = threading.Event()

        def delayed_get() -> None:
            time.sleep(0.1)
            q.get()

        def blocking_put() -> None:
            q.put("b")  # should block until delayed_get runs
            unblocked.set()

        threading.Thread(target=delayed_get).start()
        threading.Thread(target=blocking_put).start()

        self.assertTrue(
            unblocked.wait(timeout=2),
            "put never unblocked after get drained the queue",
        )


class TestNowait(unittest.TestCase):
    """Non-blocking put_nowait / get_nowait semantics."""

    def test_get_nowait_empty_raises(self) -> None:
        q = BoundedBlockingQueue(5)
        with self.assertRaises(Empty):
            q.get_nowait()

    def test_put_nowait_full_raises(self) -> None:
        q = BoundedBlockingQueue(2)
        q.put_nowait("a")
        q.put_nowait("b")
        with self.assertRaises(Full):
            q.put_nowait("c")

    def test_nowait_round_trip(self) -> None:
        q = BoundedBlockingQueue(3)
        for i in range(3):
            q.put_nowait(i)
        self.assertEqual(q.qsize(), 3)
        for i in range(3):
            self.assertEqual(q.get_nowait(), i)
        self.assertEqual(q.qsize(), 0)


class TestEdgeCases(unittest.TestCase):

    def test_invalid_capacity(self) -> None:
        with self.assertRaises(ValueError):
            BoundedBlockingQueue(0)
        with self.assertRaises(ValueError):
            BoundedBlockingQueue(-3)

    def test_capacity_one(self) -> None:
        q = BoundedBlockingQueue(1)
        q.put("only")
        self.assertEqual(q.get(), "only")

    def test_fifo_order(self) -> None:
        q = BoundedBlockingQueue(10)
        items = list(range(10))
        for i in items:
            q.put(i)
        result = [q.get() for _ in items]
        self.assertEqual(result, items)

    def test_repr(self) -> None:
        q = BoundedBlockingQueue(4)
        q.put("x")
        self.assertIn("capacity=4", repr(q))
        self.assertIn("size=1", repr(q))


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
