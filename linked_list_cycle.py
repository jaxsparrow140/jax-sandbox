"""linked_list_cycle.py

Detect whether a singly linked list contains a cycle and, if so, return the
node where the cycle begins.

Constraints:
- O(n) time
- O(1) extra space
- No hash sets

Uses Floyd's Tortoise-and-Hare algorithm.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass
class ListNode:
    val: int
    next: Optional["ListNode"] = None

    def __repr__(self) -> str:  # helpful for debugging / tests
        return f"ListNode({self.val})"


class LinkedList:
    """Minimal singly-linked list wrapper."""

    def __init__(self, values: Optional[Iterable[int]] = None):
        self.head: Optional[ListNode] = None
        self.tail: Optional[ListNode] = None
        self._len = 0

        if values is not None:
            for v in values:
                self.append(v)

    def __len__(self) -> int:
        return self._len

    def append(self, val: int) -> ListNode:
        node = ListNode(val)
        if self.head is None:
            self.head = self.tail = node
        else:
            assert self.tail is not None
            self.tail.next = node
            self.tail = node
        self._len += 1
        return node

    def node_at(self, index: int) -> ListNode:
        """Return the node at 0-based position `index`.

        Raises IndexError if out of range.
        """
        if index < 0:
            raise IndexError("index must be non-negative")

        cur = self.head
        i = 0
        while cur is not None and i < index:
            cur = cur.next
            i += 1

        if cur is None:
            raise IndexError("index out of range")
        return cur

    def create_cycle(self, entry_index: int) -> None:
        """Make the list cyclic by pointing tail.next to node_at(entry_index)."""
        if self.head is None:
            raise ValueError("cannot create cycle on an empty list")
        if self.tail is None:
            raise ValueError("list has no tail")

        entry = self.node_at(entry_index)
        self.tail.next = entry


def detect_cycle_start(head: Optional[ListNode]) -> Optional[ListNode]:
    """Return the node where the cycle begins, or None if the list is acyclic."""

    # Phase 1: detect whether a cycle exists (find meeting point)
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            break
    else:
        return None

    # Phase 2: find entry point
    entry = head
    while entry is not slow:
        assert entry is not None and slow is not None  # for type-checkers
        entry = entry.next
        slow = slow.next

    return entry


# ── Tests ─────────────────────────────────────────────────────────────

def test_cycle_starts_at_third_node() -> None:
    # Build: 1 → 2 → 3 → 4 → 5 → back to 3
    ll = LinkedList([1, 2, 3, 4, 5])
    third = ll.node_at(2)  # 3rd node (0-based index 2)
    ll.create_cycle(2)

    result = detect_cycle_start(ll.head)
    assert result is third, f"Expected entry {third}, got {result}"
    assert result is not None and result.val == 3


def test_no_cycle() -> None:
    ll = LinkedList([10, 20, 30])
    assert detect_cycle_start(ll.head) is None


def test_single_node_self_loop() -> None:
    ll = LinkedList([42])
    assert ll.tail is not None
    ll.tail.next = ll.head
    assert detect_cycle_start(ll.head) is ll.head


def test_empty_list() -> None:
    assert detect_cycle_start(None) is None


if __name__ == "__main__":
    test_cycle_starts_at_third_node()
    test_no_cycle()
    test_single_node_self_loop()
    test_empty_list()
    print("All tests passed.")
