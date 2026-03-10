#!/usr/bin/env python3
"""
Linked List Cycle Detection

Detects if a linked list has a cycle and returns the node where the cycle begins.
Uses Floyd's Cycle Detection Algorithm (two pointers) for O(n) time and O(1) space.
"""


class ListNode:
    """A node in the linked list."""
    
    def __init__(self, value):
        self.value = value
        self.next = None
    
    def __repr__(self):
        return f"ListNode({self.value})"


class LinkedList:
    """A singly linked list with cycle detection."""
    
    def __init__(self):
        self.head = None
    
    def append(self, value):
        """Append a node to the end of the list."""
        new_node = ListNode(value)
        if not self.head:
            self.head = new_node
            return
        
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
    
    def to_list(self):
        """Convert the linked list to a Python list (for non-cyclic portion)."""
        result = []
        current = self.head
        while current:
            result.append(current.value)
            current = current.next
        return result
    
    def __repr__(self):
        values = self.to_list()
        return f"LinkedList({values})"


def detect_cycle_start(head):
    """
    Detect if a linked list has a cycle and return the node where the cycle begins.
    
    Uses Floyd's Cycle Detection Algorithm (two pointers):
    1. Use slow and fast pointers to detect if a cycle exists
    2. When they meet, reset one pointer to head
    3. Move both at same speed until they meet again - that's the cycle start
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    
    Args:
        head: The head node of the linked list
        
    Returns:
        The node where the cycle begins, or None if no cycle exists
    """
    if not head or not head.next:
        return None
    
    # Phase 1: Detect if there's a cycle using two pointers
    slow = head
    fast = head
    
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        
        # If they meet, there's a cycle
        if slow == fast:
            break
    
    # If fast reached the end, there's no cycle
    if not fast or not fast.next:
        return None
    
    # Phase 2: Find the start of the cycle
    # Reset one pointer to head, keep the other at meeting point
    # Move both at same speed until they meet
    slow = head
    while slow != fast:
        slow = slow.next
        fast = fast.next
    
    # They meet at the cycle start
    return slow


def create_cycle_at_node(linked_list, cycle_start_index):
    """
    Create a cycle in the linked list starting at the given index.
    
    Args:
        linked_list: The LinkedList object
        cycle_start_index: The index (0-based) where the cycle should start
    
    Returns:
        The node where the cycle begins
    """
    if not linked_list.head:
        return None
    
    # Find the node at cycle_start_index
    cycle_start_node = linked_list.head
    for i in range(cycle_start_index):
        if cycle_start_node.next:
            cycle_start_node = cycle_start_node.next
        else:
            return None  # Index out of bounds
    
    # Find the last node and connect it to cycle_start_node
    current = linked_list.head
    while current.next:
        current = current.next
    
    current.next = cycle_start_node
    return cycle_start_node


def test_cycle_detection():
    """Test the cycle detection algorithm."""
    print("=" * 60)
    print("Testing Linked List Cycle Detection")
    print("=" * 60)
    
    # Test 1: Create a list with 5 nodes and cycle starting at 3rd node (index 2)
    print("\n[Test 1] Creating linked list: [1, 2, 3, 4, 5]")
    print("Creating cycle starting at 3rd node (value: 3)...")
    
    ll = LinkedList()
    for i in range(1, 6):
        ll.append(i)
    
    cycle_node = create_cycle_at_node(ll, 2)  # Index 2 = 3rd node
    print(f"Cycle created at node: {cycle_node}")
    
    # Detect the cycle start
    result = detect_cycle_start(ll.head)
    
    print(f"\nCycle detection result: {result}")
    print(f"Expected: ListNode(3)")
    print(f"Match: {result == cycle_node}")
    
    # Test 2: List with no cycle
    print("\n[Test 2] Testing list with no cycle...")
    ll2 = LinkedList()
    for i in range(1, 4):
        ll2.append(i)
    
    result2 = detect_cycle_start(ll2.head)
    print(f"Result: {result2}")
    print(f"Expected: None")
    print(f"Match: {result2 is None}")
    
    # Test 3: Cycle at first node (index 0)
    print("\n[Test 3] Creating cycle at first node (index 0)...")
    ll3 = LinkedList()
    for i in range(1, 4):
        ll3.append(i)
    
    cycle_node3 = create_cycle_at_node(ll3, 0)
    result3 = detect_cycle_start(ll3.head)
    print(f"Result: {result3}")
    print(f"Expected: ListNode(1)")
    print(f"Match: {result3 == cycle_node3}")
    
    # Test 4: Single node with no cycle
    print("\n[Test 4] Testing single node with no cycle...")
    ll4 = LinkedList()
    ll4.append(1)
    
    result4 = detect_cycle_start(ll4.head)
    print(f"Result: {result4}")
    print(f"Expected: None")
    print(f"Match: {result4 is None}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_cycle_detection()
