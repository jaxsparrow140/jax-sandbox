"""
Linked list cycle detection — Floyd's tortoise and hare algorithm.

Detection:     O(n) time, O(1) space
Cycle start:   O(n) time, O(1) space
No hash sets.

Key math:
  Let F = distance from head to cycle start
      C = cycle length
      a = distance from cycle start to meeting point (inside cycle)

  When slow and fast first meet:
    slow traveled: F + a
    fast traveled: F + a + k*C  (k full laps ahead)
    fast = 2 * slow  →  2(F+a) = F + a + k*C
                       →  F + a = k*C
                       →  F = k*C - a

  So: if we reset one pointer to head and advance both one step at a time,
  they meet exactly at the cycle start after F more steps.
"""


class Node:
    def __init__(self, val: int):
        self.val = val
        self.next: "Node | None" = None

    def __repr__(self):
        return f"Node({self.val})"


class LinkedList:
    def __init__(self):
        self.head: Node | None = None

    def append(self, val: int) -> Node:
        """Append a node to the tail; return the new node."""
        new_node = Node(val)
        if self.head is None:
            self.head = new_node
        else:
            cur = self.head
            while cur.next is not None:
                cur = cur.next
            cur.next = new_node
        return new_node

    def create_cycle(self, cycle_start_index: int) -> None:
        """
        Connect the tail back to the node at `cycle_start_index` (0-based).
        Raises ValueError if the index is out of range.
        """
        if self.head is None:
            raise ValueError("List is empty")

        nodes = []
        cur = self.head
        while cur is not None:
            nodes.append(cur)
            cur = cur.next

        if cycle_start_index < 0 or cycle_start_index >= len(nodes):
            raise ValueError(
                f"cycle_start_index {cycle_start_index} out of range "
                f"(list has {len(nodes)} nodes)"
            )

        nodes[-1].next = nodes[cycle_start_index]

    def to_list(self, limit: int = 1000) -> list:
        """
        Return values as a plain list (safe on cyclic lists via a step cap).
        """
        result = []
        cur = self.head
        steps = 0
        while cur is not None and steps < limit:
            result.append(cur.val)
            cur = cur.next
            steps += 1
        return result


# ---------------------------------------------------------------------------
# Core algorithm
# ---------------------------------------------------------------------------

def detect_cycle(head):
    """
    Return the node where the cycle begins, or None if there is no cycle.

    Phase 1 — Detection:
        Move `slow` one step and `fast` two steps per iteration.
        If they ever point to the same node, a cycle exists.

    Phase 2 — Finding the start:
        Reset `slow` to head.  Advance both pointers one step at a time.
        Where they meet is the cycle start (see module docstring for proof).

    Time:  O(n)
    Space: O(1)
    """
    if head is None or head.next is None:
        return None

    slow = head
    fast = head

    # Phase 1: detect
    while fast.next is not None and fast.next.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            break
    else:
        return None  # fast hit a None — no cycle

    # Phase 2: find start
    slow = head
    while slow is not fast:
        slow = slow.next
        fast = fast.next

    return slow  # both pointers now sit at cycle start


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def run_tests():
    print("=" * 60)
    print("Test 1: cycle starting at the 3rd node (index 2)")
    print("=" * 60)

    ll = LinkedList()
    nodes = [ll.append(v) for v in [10, 20, 30, 40, 50, 60]]
    # 10 → 20 → 30 → 40 → 50 → 60 → (back to 30)
    ll.create_cycle(cycle_start_index=2)

    cycle_node = detect_cycle(ll.head)
    assert cycle_node is not None, "Expected a cycle, got None"
    assert cycle_node is nodes[2], (
        f"Expected cycle start at Node(30), got {cycle_node}"
    )
    print(f"  Cycle detected ✓  |  Cycle start: {cycle_node}  (expected Node(30))\n")

    # ------------------------------------------------------------------
    print("=" * 60)
    print("Test 2: no cycle")
    print("=" * 60)

    ll2 = LinkedList()
    for v in [1, 2, 3, 4, 5]:
        ll2.append(v)

    result = detect_cycle(ll2.head)
    assert result is None, f"Expected None, got {result}"
    print(f"  No cycle detected ✓\n")

    # ------------------------------------------------------------------
    print("=" * 60)
    print("Test 3: cycle at head (index 0) — entire list is a loop")
    print("=" * 60)

    ll3 = LinkedList()
    nodes3 = [ll3.append(v) for v in [7, 8, 9]]
    ll3.create_cycle(cycle_start_index=0)

    result3 = detect_cycle(ll3.head)
    assert result3 is nodes3[0], f"Expected Node(7), got {result3}"
    print(f"  Cycle detected ✓  |  Cycle start: {result3}  (expected Node(7))\n")

    # ------------------------------------------------------------------
    print("=" * 60)
    print("Test 4: single-node self-loop")
    print("=" * 60)

    solo = Node(42)
    solo.next = solo  # points to itself

    result4 = detect_cycle(solo)
    assert result4 is solo, f"Expected Node(42), got {result4}"
    print(f"  Cycle detected ✓  |  Cycle start: {result4}  (expected Node(42))\n")

    # ------------------------------------------------------------------
    print("=" * 60)
    print("Test 5: cycle at the last node (tail points to itself)")
    print("=" * 60)

    ll5 = LinkedList()
    nodes5 = [ll5.append(v) for v in [100, 200, 300]]
    ll5.create_cycle(cycle_start_index=2)

    result5 = detect_cycle(ll5.head)
    assert result5 is nodes5[2], f"Expected Node(300), got {result5}"
    print(f"  Cycle detected ✓  |  Cycle start: {result5}  (expected Node(300))\n")

    print("All tests passed ✓")


if __name__ == "__main__":
    run_tests()
