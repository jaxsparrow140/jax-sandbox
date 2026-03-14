"""LRU cache (from scratch).

- No functools
- No external libraries
- O(1) get / put via: dict + doubly-linked list

API:
  - get(key, default=None) -> value (and marks key as most-recently-used)
  - put(key, value) -> None (inserts/updates and enforces capacity)

"""

from __future__ import annotations

from typing import Dict, Generic, Hashable, Optional, TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class _Node(Generic[K, V]):
    __slots__ = ("key", "value", "prev", "next")

    def __init__(
        self,
        key: Optional[K] = None,
        value: Optional[V] = None,
    ) -> None:
        self.key: Optional[K] = key
        self.value: Optional[V] = value
        self.prev: Optional[_Node[K, V]] = None
        self.next: Optional[_Node[K, V]] = None


class LRUCache(Generic[K, V]):
    """Least-Recently-Used cache with fixed capacity."""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be a positive integer")

        self._capacity = capacity
        self._by_key: Dict[K, _Node[K, V]] = {}

        # Sentinel nodes so insert/remove is uniform.
        self._head: _Node[K, V] = _Node()  # MRU is right after head
        self._tail: _Node[K, V] = _Node()  # LRU is right before tail
        self._head.next = self._tail
        self._tail.prev = self._head

    def __len__(self) -> int:
        return len(self._by_key)

    def _add_to_front(self, node: _Node[K, V]) -> None:
        """Insert node right after head (mark as MRU)."""
        first = self._head.next
        assert first is not None

        node.prev = self._head
        node.next = first
        self._head.next = node
        first.prev = node

    def _remove_node(self, node: _Node[K, V]) -> None:
        prev_node = node.prev
        next_node = node.next
        assert prev_node is not None and next_node is not None

        prev_node.next = next_node
        next_node.prev = prev_node

        node.prev = None
        node.next = None

    def _move_to_front(self, node: _Node[K, V]) -> None:
        self._remove_node(node)
        self._add_to_front(node)

    def _evict_lru(self) -> None:
        """Evict the least-recently-used entry (node before tail)."""
        lru = self._tail.prev
        assert lru is not None
        if lru is self._head:
            return  # empty

        self._remove_node(lru)
        assert lru.key is not None
        del self._by_key[lru.key]

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        node = self._by_key.get(key)
        if node is None:
            return default

        self._move_to_front(node)
        return node.value

    def put(self, key: K, value: V) -> None:
        node = self._by_key.get(key)
        if node is not None:
            node.value = value
            self._move_to_front(node)
            return

        new_node = _Node(key=key, value=value)
        self._by_key[key] = new_node
        self._add_to_front(new_node)

        if len(self._by_key) > self._capacity:
            self._evict_lru()

    def _debug_keys_mru_to_lru(self) -> list[K]:
        """For debugging/tests: list keys from MRU to LRU."""
        out: list[K] = []
        cur = self._head.next
        while cur is not None and cur is not self._tail:
            assert cur.key is not None
            out.append(cur.key)
            cur = cur.next
        return out


def _demo() -> None:
    cache: LRUCache[int, int] = LRUCache(2)

    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1

    # Accessing 1 makes 2 the LRU. Adding 3 evicts 2.
    cache.put(3, 3)
    assert cache.get(2) is None
    assert cache.get(1) == 1
    assert cache.get(3) == 3

    # Updating an existing key should refresh recency.
    cache.put(1, 10)
    assert cache.get(1) == 10

    print("demo OK")


if __name__ == "__main__":
    _demo()
