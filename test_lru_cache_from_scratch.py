import unittest

from lru_cache_from_scratch import LRUCache


class TestLRUCacheFromScratch(unittest.TestCase):
    def test_basic_get_put_and_eviction(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)

        self.assertEqual(cache.get("a"), 1)  # a becomes MRU

        cache.put("c", 3)  # should evict b
        self.assertIsNone(cache.get("b"))
        self.assertEqual(cache.get("a"), 1)
        self.assertEqual(cache.get("c"), 3)

    def test_update_refreshes_recency(self):
        cache = LRUCache(2)
        cache.put(1, "one")
        cache.put(2, "two")

        cache.put(1, "ONE")  # update + refresh
        cache.put(3, "three")  # should evict 2

        self.assertIsNone(cache.get(2))
        self.assertEqual(cache.get(1), "ONE")
        self.assertEqual(cache.get(3), "three")

    def test_get_default(self):
        cache = LRUCache(1)
        self.assertEqual(cache.get("missing", default=123), 123)

    def test_capacity_must_be_positive(self):
        with self.assertRaises(ValueError):
            LRUCache(0)


if __name__ == "__main__":
    unittest.main()
