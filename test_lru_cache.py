import sys
from lru_cache import LRUCache


def run_tests() -> bool:
    all_passed = True

    def check(name: str, condition: bool) -> None:
        nonlocal all_passed
        status = "PASS" if condition else "FAIL"
        if not condition:
            all_passed = False
        print(f"[{status}] {name}")

    # 1. Basic put/get
    c = LRUCache(2)
    c.put(1, 10)
    c.put(2, 20)
    check("basic put/get", c.get(1) == 10 and c.get(2) == 20)

    # 2. LRU eviction
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    c.put(3, 3)  # evicts key 1
    check("LRU eviction (oldest key gone)", c.get(1) == -1)
    check("LRU eviction (newer keys remain)", c.get(2) == 2 and c.get(3) == 3)

    # 3. get reorders priority
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    c.get(1)     # key 1 is now most-recently used
    c.put(3, 3)  # should evict key 2, not key 1
    check("get reorders priority (accessed key survives)", c.get(1) == 1)
    check("get reorders priority (unaccessed key evicted)", c.get(2) == -1)

    # 4. Overwrite existing key
    c = LRUCache(2)
    c.put(1, 1)
    c.put(1, 100)
    check("overwrite existing key", c.get(1) == 100)

    # 5. Capacity-1 edge case
    c = LRUCache(1)
    c.put(1, 1)
    c.put(2, 2)  # evicts key 1
    check("capacity-1 edge case (eviction)", c.get(1) == -1 and c.get(2) == 2)

    return all_passed


if __name__ == "__main__":
    passed = run_tests()
    sys.exit(0 if passed else 1)
