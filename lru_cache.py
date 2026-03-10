"""LRU Cache (Least Recently Used) implementation from scratch.

Requirements:
- O(1) average time for get(key) and put(key, value)
- Capacity limit; when full, evict least-recently-used item

Approach:
- Hash map: key -> node (O(1) access)
- Doubly-linked list to track recency (O(1) move-to-front / eviction)

Most-recently-used (MRU) is kept at the front (right after head sentinel).
Least-recently-used (LRU) is kept at the back (right before tail sentinel).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class _Node:
    key: Any
    value: Any
    prev: Optional["_Node"] = None
    next: Optional["_Node"] = None


class LRUCache:
    """An LRU cache with fixed capacity.

    get(key) -> value | None
        Returns the value and marks key as most-recently-used.
        Returns None if key is not present.

    put(key, value) -> None
        Inserts/updates value and marks key as most-recently-used.
        If capacity is exceeded, evicts the least-recently-used entry.
    """

    def __init__(self, capacity: int):
        if capacity < 0:
            raise ValueError("capacity must be >= 0")
        self.capacity = capacity
        self._nodes: Dict[Any, _Node] = {}

        # Sentinel nodes to avoid edge cases on insert/remove.
        self._head = _Node(key=None, value=None)  # MRU side
        self._tail = _Node(key=None, value=None)  # LRU side
        self._head.next = self._tail
        self._tail.prev = self._head

    def __len__(self) -> int:
        return len(self._nodes)

    def _remove(self, node: _Node) -> None:
        """Remove node from the linked list (but not from the dict)."""
        prev_node = node.prev
        next_node = node.next
        if prev_node is None or next_node is None:
            # Should never happen for nodes currently in the list.
            raise RuntimeError("attempted to remove a detached node")
        prev_node.next = next_node
        next_node.prev = prev_node
        node.prev = None
        node.next = None

    def _add_to_front(self, node: _Node) -> None:
        """Add node right after head (mark as MRU)."""
        first = self._head.next
        if first is None:
            raise RuntimeError("corrupt list: head.next is None")
        node.prev = self._head
        node.next = first
        self._head.next = node
        first.prev = node

    def _move_to_front(self, node: _Node) -> None:
        self._remove(node)
        self._add_to_front(node)

    def _evict_lru(self) -> None:
        """Evict the least-recently-used node (right before tail)."""
        lru = self._tail.prev
        if lru is None or lru is self._head:
            return  # nothing to evict
        self._remove(lru)
        self._nodes.pop(lru.key, None)

    def get(self, key: Any) -> Any:
        node = self._nodes.get(key)
        if node is None:
            return None
        self._move_to_front(node)
        return node.value

    def put(self, key: Any, value: Any) -> None:
        if self.capacity == 0:
            return

        node = self._nodes.get(key)
        if node is not None:
            node.value = value
            self._move_to_front(node)
            return

        new_node = _Node(key=key, value=value)
        self._nodes[key] = new_node
        self._add_to_front(new_node)

        if len(self._nodes) > self.capacity:
            self._evict_lru()

    def keys_mru_to_lru(self) -> list[Any]:
        """Debug helper: current keys ordered from most- to least-recently-used."""
        out: list[Any] = []
        cur = self._head.next
        while cur is not None and cur is not self._tail:
            out.append(cur.key)
            cur = cur.next
        return out
