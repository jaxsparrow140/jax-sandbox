import threading
import unittest

from bounded_queue import BoundedBlockingQueue, QueueEmpty, QueueFull


class TestBoundedBlockingQueue(unittest.TestCase):
    def test_producer_consumer(self):
        q = BoundedBlockingQueue(maxsize=5)
        produced = []
        consumed = []
        produced_lock = threading.Lock()
        consumed_lock = threading.Lock()

        def producer(start):
            for i in range(start, start + 10):
                with produced_lock:
                    produced.append(i)
                q.put(i)

        def consumer():
            while True:
                item = q.get()
                if item is None:
                    break
                with consumed_lock:
                    consumed.append(item)

        producers = [threading.Thread(target=producer, args=(i * 10,)) for i in range(3)]
        consumers = [threading.Thread(target=consumer) for _ in range(2)]

        for t in consumers:
            t.start()
        for t in producers:
            t.start()

        for t in producers:
            t.join()

        # Send sentinel for each consumer
        for _ in range(2):
            q.put(None)

        for t in consumers:
            t.join()

        self.assertEqual(sorted(produced), sorted(consumed))
        self.assertEqual(len(consumed), 30)

    def test_put_nowait_raises_queue_full(self):
        q = BoundedBlockingQueue(maxsize=2)
        q.put_nowait(1)
        q.put_nowait(2)
        with self.assertRaises(QueueFull):
            q.put_nowait(3)

    def test_get_nowait_raises_queue_empty(self):
        q = BoundedBlockingQueue(maxsize=2)
        with self.assertRaises(QueueEmpty):
            q.get_nowait()


if __name__ == "__main__":
    unittest.main()
