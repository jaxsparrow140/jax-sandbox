"""
LRU Cache — from scratch, no functools, no external libs.

Uses a doubly-linked list + hashmap for O(1) get and put.
"""


class _Node:
    """Doubly-linked list node."""

    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key: int = 0, value: int = 0):
        self.key = key
        self.value = value
        self.prev: "_Node | None" = None
        self.next: "_Node | None" = None


class LRUCache:
    """
    Least-Recently-Used cache with fixed capacity.

    get(key)        → value or -1          O(1)
    put(key, value) → None (evicts LRU)    O(1)
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        self.capacity = capacity
        self.cache: dict[int, _Node] = {}

        # Sentinel head/tail so we never deal with None edge cases.
        self.head = _Node()  # MRU side
        self.tail = _Node()  # LRU side
        self.head.next = self.tail
        self.tail.prev = self.head

    # ── internal helpers ──────────────────────────────────────────

    def _remove(self, node: _Node) -> None:
        """Unlink a node from the list."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _insert_after_head(self, node: _Node) -> None:
        """Insert node right after head (most-recently-used spot)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    # ── public API ────────────────────────────────────────────────

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        # Move to front (mark as most recently used).
        self._remove(node)
        self._insert_after_head(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Update existing node and move to front.
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._insert_after_head(node)
        else:
            if len(self.cache) >= self.capacity:
                # Evict LRU (node just before tail sentinel).
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]
            node = _Node(key, value)
            self.cache[key] = node
            self._insert_after_head(node)

    # ── convenience ───────────────────────────────────────────────

    def __len__(self) -> int:
        return len(self.cache)

    def __repr__(self) -> str:
        items = []
        cur = self.head.next
        while cur is not self.tail:
            items.append(f"{cur.key}:{cur.value}")
            cur = cur.next
        return f"LRUCache(cap={self.capacity}, MRU→LRU=[{', '.join(items)}])"


# ═══════════════════════════════════════════════════════════════════
#  Tests
# ═══════════════════════════════════════════════════════════════════

def test_basic_get_put():
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    assert c.get(1) == 1       # hit
    c.put(3, 3)                # evicts key 2 (LRU)
    assert c.get(2) == -1      # miss
    c.put(4, 4)                # evicts key 1 (LRU after 3 was just inserted)
    assert c.get(1) == -1
    assert c.get(3) == 3
    assert c.get(4) == 4
    print("✓ test_basic_get_put")


def test_update_existing_key():
    c = LRUCache(2)
    c.put(1, 10)
    c.put(2, 20)
    c.put(1, 100)              # update key 1 → moves to MRU
    c.put(3, 30)               # should evict key 2, not key 1
    assert c.get(2) == -1
    assert c.get(1) == 100
    assert c.get(3) == 30
    print("✓ test_update_existing_key")


def test_capacity_one():
    c = LRUCache(1)
    c.put(1, 1)
    assert c.get(1) == 1
    c.put(2, 2)                # evicts 1
    assert c.get(1) == -1
    assert c.get(2) == 2
    print("✓ test_capacity_one")


def test_get_promotes_to_mru():
    c = LRUCache(3)
    c.put(1, 1)
    c.put(2, 2)
    c.put(3, 3)                # order MRU→LRU: 3, 2, 1
    c.get(1)                   # promotes 1 → MRU: 1, 3, 2
    c.put(4, 4)                # evicts 2 (now LRU)
    assert c.get(2) == -1
    assert c.get(1) == 1
    assert c.get(3) == 3
    assert c.get(4) == 4
    print("✓ test_get_promotes_to_mru")


def test_miss_returns_neg1():
    c = LRUCache(2)
    assert c.get(99) == -1
    print("✓ test_miss_returns_neg1")


def test_len_and_repr():
    c = LRUCache(3)
    c.put(1, 10)
    c.put(2, 20)
    assert len(c) == 2
    c.put(3, 30)
    c.put(4, 40)               # evicts 1
    assert len(c) == 3
    r = repr(c)
    assert "4:40" in r
    print(f"✓ test_len_and_repr  →  {r}")


if __name__ == "__main__":
    test_basic_get_put()
    test_update_existing_key()
    test_capacity_one()
    test_get_promotes_to_mru()
    test_miss_returns_neg1()
    test_len_and_repr()
    print("\nAll tests passed.")
