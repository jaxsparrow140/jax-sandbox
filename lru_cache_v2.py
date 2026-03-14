"""
LRU Cache implementation from scratch using a doubly-linked list and hashmap.

Data structures:
- Doubly-linked list: Maintains access order. The head is the most recently used
  item and the tail is the least recently used. Nodes can be moved/removed in O(1).
- Hashmap (dict): Maps keys to their corresponding linked list nodes for O(1) lookup.

Together these give O(1) time complexity for both get() and put() operations.
"""


class _Node:
    """Doubly-linked list node storing a key-value pair."""

    __slots__ = ("key", "val", "prev", "next")

    def __init__(self, key: int = 0, val: int = 0):
        self.key = key
        self.val = val
        self.prev: "_Node | None" = None
        self.next: "_Node | None" = None


class LRUCache:
    """
    Least Recently Used (LRU) cache with O(1) get and put.

    Uses two sentinel nodes (head, tail) so that insert/remove never need
    to handle None edge cases — every real node is always between head and tail.
    """

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: dict[int, _Node] = {}
        # Sentinel nodes
        self.head = _Node()
        self.tail = _Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    # ---- internal helpers ----

    def _remove(self, node: _Node) -> None:
        """Unlink a node from the list."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _insert_after_head(self, node: _Node) -> None:
        """Insert a node right after the head sentinel (most-recently-used position)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    # ---- public API ----

    def get(self, key: int) -> int:
        """Return the value for *key*, or -1 if not present. Marks the key as recently used."""
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._insert_after_head(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        """
        Insert or update *key* with *value*.

        If the cache is at capacity, evict the least recently used item
        (the node just before the tail sentinel).
        """
        if key in self.cache:
            self._remove(self.cache[key])
        node = _Node(key, value)
        self.cache[key] = node
        self._insert_after_head(node)
        if len(self.cache) > self.capacity:
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]


# ---- tests ----

if __name__ == "__main__":
    results: list[tuple[str, bool]] = []

    def test(name: str, condition: bool) -> None:
        results.append((name, condition))

    # 1. Basic get/put
    c = LRUCache(2)
    c.put(1, 10)
    c.put(2, 20)
    test("basic put then get(1)", c.get(1) == 10)
    test("basic put then get(2)", c.get(2) == 20)

    # 2. Eviction of LRU item
    c.put(3, 30)  # evicts key 1 (LRU after get(2) above)
    test("evicted key returns -1", c.get(1) == -1)
    test("non-evicted key still present", c.get(3) == 30)

    # 3. Access promotes item (prevents eviction)
    c2 = LRUCache(2)
    c2.put(1, 1)
    c2.put(2, 2)
    c2.get(1)       # promotes key 1; key 2 is now LRU
    c2.put(3, 3)    # evicts key 2
    test("promoted key survives eviction", c2.get(1) == 1)
    test("non-promoted key evicted", c2.get(2) == -1)

    # 4. Update existing key
    c3 = LRUCache(2)
    c3.put(1, 1)
    c3.put(1, 100)
    test("update overwrites value", c3.get(1) == 100)

    # 5. Edge: get missing key
    c4 = LRUCache(3)
    test("get missing key returns -1", c4.get(99) == -1)

    # 6. Edge: capacity = 1
    c5 = LRUCache(1)
    c5.put(1, 1)
    c5.put(2, 2)  # evicts key 1
    test("cap=1: old key evicted", c5.get(1) == -1)
    test("cap=1: new key present", c5.get(2) == 2)

    # Print results
    for name, passed in results:
        print(f"{'PASS' if passed else 'FAIL'}: {name}")

    if all(p for _, p in results):
        print(f"\nAll {len(results)} tests passed.")
    else:
        print(f"\n{sum(not p for _, p in results)} test(s) FAILED.")
