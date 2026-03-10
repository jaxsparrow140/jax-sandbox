"""
LRU Cache — from scratch, no functools, no external libs.

Uses a doubly linked list + hash map for O(1) get and put.
- Doubly linked list tracks access order (most recent at head, least recent at tail).
- Hash map provides O(1) key → node lookup.
"""


class Node:
    """Doubly linked list node."""

    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key: int = 0, value: int = 0):
        self.key = key
        self.value = value
        self.prev: "Node | None" = None
        self.next: "Node | None" = None


class LRUCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self.cache: dict[int, Node] = {}

        # Sentinel nodes — avoids None checks on every insert/remove.
        self.head = Node()  # dummy head (most recently used side)
        self.tail = Node()  # dummy tail (least recently used side)
        self.head.next = self.tail
        self.tail.prev = self.head

    # ── internal helpers ──────────────────────────────────────────

    def _remove(self, node: Node) -> None:
        """Unlink a node from the list."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node: Node) -> None:
        """Insert node right after the dummy head (most recent position)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    # ── public API ────────────────────────────────────────────────

    def get(self, key: int) -> int:
        """Return value for key, or -1 if not found. Marks key as recently used."""
        if key not in self.cache:
            return -1
        node = self.cache[key]
        # Move to front (most recently used)
        self._remove(node)
        self._add_to_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        """Insert or update key-value pair. Evicts LRU item if at capacity."""
        if key in self.cache:
            # Update existing — remove, re-insert at front
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_front(node)
        else:
            if len(self.cache) >= self.capacity:
                # Evict least recently used (node just before dummy tail)
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]
            node = Node(key, value)
            self.cache[key] = node
            self._add_to_front(node)

    def __repr__(self) -> str:
        """Show contents in MRU → LRU order."""
        items = []
        cur = self.head.next
        while cur is not self.tail:
            items.append(f"{cur.key}:{cur.value}")
            cur = cur.next
        return f"LRUCache([{', '.join(items)}], cap={self.capacity})"


# ── Tests ─────────────────────────────────────────────────────────


def test_basic_operations():
    """Classic LeetCode 146 example."""
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1        # hit — 1 becomes most recent
    cache.put(3, 3)                  # evicts key 2 (LRU)
    assert cache.get(2) == -1       # miss
    cache.put(4, 4)                  # evicts key 1 (LRU)
    assert cache.get(1) == -1       # miss
    assert cache.get(3) == 3        # hit
    assert cache.get(4) == 4        # hit
    print("✓ basic_operations")


def test_update_existing_key():
    """Updating a key should refresh its position, not add a duplicate."""
    cache = LRUCache(2)
    cache.put(1, 10)
    cache.put(2, 20)
    cache.put(1, 100)               # update key 1 — now most recent
    cache.put(3, 30)                # should evict key 2 (LRU), not key 1
    assert cache.get(1) == 100
    assert cache.get(2) == -1
    assert cache.get(3) == 30
    print("✓ update_existing_key")


def test_capacity_one():
    """Edge case: cache that holds exactly one item."""
    cache = LRUCache(1)
    cache.put(1, 1)
    assert cache.get(1) == 1
    cache.put(2, 2)                  # evicts key 1
    assert cache.get(1) == -1
    assert cache.get(2) == 2
    print("✓ capacity_one")


def test_get_promotes_to_mru():
    """A get() should save a key from eviction."""
    cache = LRUCache(3)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.put(3, 3)
    cache.get(1)                     # promote key 1 → MRU
    cache.put(4, 4)                  # evicts key 2 (now the LRU)
    assert cache.get(2) == -1
    assert cache.get(1) == 1
    assert cache.get(3) == 3
    assert cache.get(4) == 4
    print("✓ get_promotes_to_mru")


def test_eviction_order():
    """Verify strict LRU eviction across a longer sequence."""
    cache = LRUCache(3)
    for i in range(1, 7):            # put 1..6 into cap-3 cache
        cache.put(i, i * 10)
    # Only 4, 5, 6 should survive
    for i in range(1, 4):
        assert cache.get(i) == -1, f"key {i} should have been evicted"
    for i in range(4, 7):
        assert cache.get(i) == i * 10, f"key {i} should still be present"
    print("✓ eviction_order")


if __name__ == "__main__":
    test_basic_operations()
    test_update_existing_key()
    test_capacity_one()
    test_get_promotes_to_mru()
    test_eviction_order()
    print("\nAll tests passed.")
