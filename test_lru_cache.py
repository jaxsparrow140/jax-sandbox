from lru_cache import LRUCache


def test_basic_eviction_and_recency():
    cache = LRUCache(capacity=2)

    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1  # a becomes MRU

    # Cache is full; inserting c should evict LRU (which is b)
    cache.put("c", 3)
    assert cache.get("b") is None
    assert cache.get("c") == 3
    assert cache.get("a") == 1

    # Access order should now be: a (MRU), c (LRU)
    assert cache.keys_mru_to_lru() == ["a", "c"]


def test_update_moves_to_front():
    cache = LRUCache(capacity=2)
    cache.put(1, "one")
    cache.put(2, "two")

    # Update key 1; should become MRU
    cache.put(1, "ONE")
    assert cache.get(1) == "ONE"
    assert cache.keys_mru_to_lru() == [1, 2]


def test_capacity_zero_is_noop():
    cache = LRUCache(capacity=0)
    cache.put("x", 99)
    assert cache.get("x") is None
    assert len(cache) == 0


if __name__ == "__main__":
    test_basic_eviction_and_recency()
    test_update_moves_to_front()
    test_capacity_zero_is_noop()

    print("All tests passed.")
