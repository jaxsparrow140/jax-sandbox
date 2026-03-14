"""Cycle detection in a singly linked list (O(n) time, O(1) space).

Implements:
- Node
- LinkedList
- detect_cycle_start(head): returns the Node where the cycle begins, or None.

Algorithm: Floyd's tortoise-and-hare.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, TypeVar, Generic

T = TypeVar("T")


@dataclass(eq=False)
class Node(Generic[T]):
    value: T
    next: Optional["Node[T]"] = None

    def __repr__(self) -> str:  # helpful for debugging; avoids recursive next printing
        return f"Node(value={self.value!r})"


class LinkedList(Generic[T]):
    def __init__(self, values: Optional[Iterable[T]] = None):
        self.head: Optional[Node[T]] = None
        self.tail: Optional[Node[T]] = None

        if values is not None:
            for v in values:
                self.append(v)

    def append(self, value: T) -> Node[T]:
        node = Node(value)
        if self.head is None:
            self.head = self.tail = node
            return node

        assert self.tail is not None  # for type-checkers
        self.tail.next = node
        self.tail = node
        return node

    def node_at(self, index: int) -> Node[T]:
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
        """Connect tail.next to the node at entry_index to create a cycle."""
        if self.head is None:
            raise ValueError("cannot create a cycle in an empty list")
        if self.tail is None:
            raise ValueError("internal error: tail missing")

        entry = self.node_at(entry_index)
        self.tail.next = entry


def detect_cycle_start(head: Optional[Node[T]]) -> Optional[Node[T]]:
    """Return the node where the cycle begins, or None if no cycle exists."""
    if head is None:
        return None

    slow: Optional[Node[T]] = head
    fast: Optional[Node[T]] = head

    # Phase 1: detect if a cycle exists.
    while fast is not None and fast.next is not None:
        slow = slow.next  # type: ignore[assignment]
        fast = fast.next.next
        if slow is fast:
            break
    else:
        return None  # no cycle

    # Phase 2: find cycle entry.
    assert slow is not None
    ptr1: Node[T] = head
    ptr2: Node[T] = slow
    while ptr1 is not ptr2:
        assert ptr1.next is not None
        assert ptr2.next is not None
        ptr1 = ptr1.next
        ptr2 = ptr2.next
    return ptr1


if __name__ == "__main__":
    ll = LinkedList([1, 2, 3, 4, 5])
    ll.create_cycle(2)  # cycle starts at the 3rd node (value=3)

    start = detect_cycle_start(ll.head)
    print("cycle starts at:", start)
