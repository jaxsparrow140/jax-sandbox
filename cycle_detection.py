#!/usr/bin/env python3
"""
Cycle detection in linked list using Floyd's algorithm
Detects if a cycle exists and returns the node where the cycle begins.
"""

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def detect_cycle(head):
    """
    Detects if a linked list has a cycle and returns the node where the cycle begins.
    Uses Floyd's cycle-finding algorithm (tortoise and hare).
    Time: O(n), Space: O(1)
    """
    if not head or not head.next:
        return None
    
    # Phase 1: Detect if cycle exists using slow and fast pointers
    slow = head
    fast = head
    
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        
        if slow == fast:
            break
    else:
        # No cycle found
        return None
    
    # Phase 2: Find the start of the cycle
    # Move one pointer to head, keep other at meeting point
    # Move both at same speed until they meet
    slow = head
    while slow != fast:
        slow = slow.next
        fast = fast.next
    
    return slow  # This is the start of the cycle

# Test function
if __name__ == "__main__":
    # Create a linked list with cycle starting at 3rd node (index 2)
    # Nodes: 1 -> 2 -> 3 -> 4 -> 5 -> 3 (cycle back to node 3)
    
    # Create nodes
    node1 = ListNode(1)
    node2 = ListNode(2)
    node3 = ListNode(3)
    node4 = ListNode(4)
    node5 = ListNode(5)
    
    # Link nodes
    node1.next = node2
    node2.next = node3
    node3.next = node4
    node4.next = node5
    node5.next = node3  # Create cycle back to node 3
    
    # Detect cycle
    cycle_start = detect_cycle(node1)
    
    if cycle_start:
        print(f"Cycle detected starting at node with value: {cycle_start.val}")
    else:
        print("No cycle detected")

    # Verify the result
    if cycle_start and cycle_start.val == 3:
        print("Test passed: Cycle detected at 3rd node as expected")
    else:
        print("Test failed: Cycle not detected at expected position")

    # Test with no cycle
    node6 = ListNode(6)
    node7 = ListNode(7)
    node8 = ListNode(8)
    node6.next = node7
    node7.next = node8
    
    no_cycle = detect_cycle(node6)
    if no_cycle is None:
        print("Test passed: No cycle detected in linear list")
    else:
        print("Test failed: False cycle detected in linear list")