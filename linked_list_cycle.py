"""
Linked list cycle detection using Floyd's Tortoise and Hare algorithm.
O(n) time, O(1) space — no hash sets.
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
    """Return the node where the cycle begins, or None if acyclic.

    Phase 1 — find meeting point:
        slow moves 1 step, fast moves 2 steps.
        If they meet, a cycle exists.

    Phase 2 — find cycle entry:
        Reset one pointer to head; advance both at 1 step.
        They meet at the cycle's start node.
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
    entry = head
    while entry is not slow:
        entry = entry.next
        slow = slow.next

    return entry


# ── Test ─────────────────────────────────────────────────────────────
def test_cycle_at_third_node():
    # Build: 1 → 2 → 3 → 4 → 5 → back to 3
    nodes = [ListNode(i) for i in range(1, 6)]
    for i in range(len(nodes) - 1):
        nodes[i].next = nodes[i + 1]
    nodes[-1].next = nodes[2]  # 5 → 3 (cycle starts at 3rd node)

    result = detect_cycle(nodes[0])
    assert result is nodes[2], f"Expected node 3, got {result}"
    assert result.val == 3
    print(f"✓ Cycle detected — starts at {result}")


def test_no_cycle():
    nodes = [ListNode(i) for i in range(1, 4)]
    nodes[0].next = nodes[1]
    nodes[1].next = nodes[2]

    result = detect_cycle(nodes[0])
    assert result is None, f"Expected None, got {result}"
    print("✓ No cycle — returned None")


def test_single_node_self_loop():
    node = ListNode(42)
    node.next = node

    result = detect_cycle(node)
    assert result is node
    print(f"✓ Self-loop detected — starts at {result}")


def test_empty_list():
    assert detect_cycle(None) is None
    print("✓ Empty list — returned None")


if __name__ == "__main__":
    test_cycle_at_third_node()
    test_no_cycle()
    test_single_node_self_loop()
    test_empty_list()
    print("\nAll tests passed.")
