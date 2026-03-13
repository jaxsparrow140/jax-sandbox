"""
LRU Cache — from scratch, no functools, no external libs.

Uses a doubly-linked list + hash map for O(1) get and put.
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

    get(key)        -> value | -1          O(1)
    put(key, value) -> None                O(1)

    When capacity is exceeded the least-recently-used entry is evicted.
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        self.capacity = capacity
        self.cache: dict[int, _Node] = {}

        # Sentinel nodes — avoids edge-case branching on empty list.
        self._head = _Node()  # most recently used end
        self._tail = _Node()  # least recently used end
        self._head.next = self._tail
        self._tail.prev = self._head

    # ── public API ───────────────────────────────────────────────

    def get(self, key: int) -> int:
        """Return value for key (marking it as recently used), or -1 if absent."""
        node = self.cache.get(key)
        if node is None:
            return -1
        self._move_to_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        """Insert or update key/value. Evicts LRU entry if at capacity."""
        node = self.cache.get(key)
        if node is not None:
            node.value = value
            self._move_to_front(node)
            return

        if len(self.cache) >= self.capacity:
            self._evict_lru()

        new_node = _Node(key, value)
        self.cache[key] = new_node
        self._push_front(new_node)

    # ── internals ────────────────────────────────────────────────

    def _remove(self, node: _Node) -> None:
        """Unlink a node from the doubly-linked list."""
        node.prev.next = node.next  # type: ignore[union-attr]
        node.next.prev = node.prev  # type: ignore[union-attr]

    def _push_front(self, node: _Node) -> None:
        """Insert node right after the head sentinel (MRU position)."""
        node.prev = self._head
        node.next = self._head.next
        self._head.next.prev = node  # type: ignore[union-attr]
        self._head.next = node

    def _move_to_front(self, node: _Node) -> None:
        """Move an existing node to the MRU position."""
        self._remove(node)
        self._push_front(node)

    def _evict_lru(self) -> None:
        """Remove the least-recently-used node (just before the tail sentinel)."""
        lru = self._tail.prev
        assert lru is not self._head, "evict called on empty cache"
        self._remove(lru)  # type: ignore[arg-type]
        del self.cache[lru.key]  # type: ignore[union-attr]

    # ── helpers ──────────────────────────────────────────────────

    def __len__(self) -> int:
        return len(self.cache)

    def __contains__(self, key: int) -> bool:
        return key in self.cache

    def __repr__(self) -> str:
        items = []
        cur = self._head.next
        while cur is not self._tail:
            items.append(f"{cur.key}:{cur.value}")  # type: ignore[union-attr]
            cur = cur.next  # type: ignore[union-attr]
        return f"LRUCache(cap={self.capacity}, MRU→LRU=[{', '.join(items)}])"


# ═══════════════════════════════════════════════════════════════════
#  Tests
# ═══════════════════════════════════════════════════════════════════

def test_basic_get_put():
    """LeetCode 146 example."""
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    assert c.get(1) == 1       # hit
    c.put(3, 3)                # evicts key 2 (LRU)
    assert c.get(2) == -1      # miss
    c.put(4, 4)                # evicts key 1 (LRU)
    assert c.get(1) == -1      # miss
    assert c.get(3) == 3       # hit
    assert c.get(4) == 4       # hit
    print("✓ basic get/put")


def test_update_existing_key():
    c = LRUCache(2)
    c.put(1, 10)
    c.put(2, 20)
    c.put(1, 100)              # update key 1 (moves to MRU)
    assert c.get(1) == 100
    c.put(3, 30)               # evicts key 2 (now LRU)
    assert c.get(2) == -1
    assert c.get(1) == 100
    assert c.get(3) == 30
    print("✓ update existing key")


def test_capacity_one():
    c = LRUCache(1)
    c.put(1, 1)
    assert c.get(1) == 1
    c.put(2, 2)                # evicts key 1
    assert c.get(1) == -1
    assert c.get(2) == 2
    print("✓ capacity = 1")


def test_get_promotes_to_mru():
    """Accessing a key should protect it from eviction."""
    c = LRUCache(3)
    c.put(1, 1)
    c.put(2, 2)
    c.put(3, 3)
    c.get(1)                   # promote key 1 — LRU order now: 2, 3, 1
    c.put(4, 4)                # evicts key 2 (LRU)
    assert c.get(2) == -1
    assert c.get(1) == 1
    assert c.get(3) == 3
    assert c.get(4) == 4
    print("✓ get promotes to MRU")


def test_eviction_order():
    """Fill to capacity, then keep inserting — oldest should always be evicted."""
    c = LRUCache(3)
    for i in range(6):
        c.put(i, i * 10)
    # Only keys 3, 4, 5 should remain
    for i in range(3):
        assert c.get(i) == -1, f"key {i} should have been evicted"
    for i in range(3, 6):
        assert c.get(i) == i * 10, f"key {i} should still be present"
    print("✓ eviction order")


def test_repr():
    c = LRUCache(3)
    c.put(1, 10)
    c.put(2, 20)
    c.put(3, 30)
    r = repr(c)
    assert "3:30" in r and "1:10" in r
    print(f"✓ repr → {r}")


if __name__ == "__main__":
    test_basic_get_put()
    test_update_existing_key()
    test_capacity_one()
    test_get_promotes_to_mru()
    test_eviction_order()
    test_repr()
    print("\nAll tests passed.")
