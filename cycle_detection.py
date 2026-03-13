"""
Floyd's Cycle Detection — O(n) time, O(1) space.

Detects whether a linked list has a cycle and returns the node
where the cycle begins (or None if acyclic).
"""
from __future__ import annotations
from typing import Optional


class ListNode:
    def __init__(self, val: int, next: Optional["ListNode"] = None):
        self.val = val
        self.next = next

    def __repr__(self) -> str:
        return f"ListNode({self.val})"


def detect_cycle(head: Optional[ListNode]) -> Optional[ListNode]:
    """Return the node where the cycle starts, or None if no cycle exists.

    Uses Floyd's tortoise-and-hare algorithm:
      1. slow moves 1 step, fast moves 2 steps until they meet (or fast hits None).
      2. Reset one pointer to head; advance both at 1 step — they meet at the cycle entry.

    Time:  O(n)
    Space: O(1)
    """
    slow = fast = head

    # Phase 1: detect whether a cycle exists
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            break
    else:
        return None  # no cycle

    # Phase 2: find the entry point
    slow = head
    while slow is not fast:
        slow = slow.next
        fast = fast.next

    return slow


# --------------- tests ---------------

def test_cycle_at_third_node():
    """Build 1 -> 2 -> 3 -> 4 -> 5 -> (back to 3) and verify detection."""
    nodes = [ListNode(i) for i in range(1, 6)]
    for a, b in zip(nodes, nodes[1:]):
        a.next = b
    # create cycle: 5 -> 3 (index 2)
    nodes[4].next = nodes[2]

    entry = detect_cycle(nodes[0])
    assert entry is nodes[2], f"Expected node 3, got {entry}"
    print(f"✓ Cycle detected — entry node: {entry}")


def test_no_cycle():
    nodes = [ListNode(i) for i in range(1, 4)]
    for a, b in zip(nodes, nodes[1:]):
        a.next = b

    assert detect_cycle(nodes[0]) is None
    print("✓ No cycle correctly returns None")


def test_single_node_self_loop():
    node = ListNode(42)
    node.next = node

    assert detect_cycle(node) is node
    print(f"✓ Self-loop detected — entry node: {node}")


def test_empty_list():
    assert detect_cycle(None) is None
    print("✓ Empty list returns None")


def test_cycle_at_head():
    """Entire list is one big loop: 1 -> 2 -> 3 -> 1."""
    nodes = [ListNode(i) for i in range(1, 4)]
    for a, b in zip(nodes, nodes[1:]):
        a.next = b
    nodes[2].next = nodes[0]

    entry = detect_cycle(nodes[0])
    assert entry is nodes[0], f"Expected node 1, got {entry}"
    print(f"✓ Full-loop cycle detected — entry node: {entry}")


if __name__ == "__main__":
    test_cycle_at_third_node()
    test_no_cycle()
    test_single_node_self_loop()
    test_empty_list()
    test_cycle_at_head()
    print("\nAll tests passed.")
