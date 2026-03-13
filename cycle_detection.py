"""
Linked List Cycle Detection

Implements Floyd's Cycle Detection Algorithm (Tortoise and Hare)
to detect cycles in a linked list and find the start of the cycle in O(n) time and O(1) space.
"""

class ListNode:
    """Definition for singly-linked list node."""
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def detect_cycle(head):
    """
    Detects if a linked list has a cycle and returns the node where the cycle begins.
    If no cycle exists, returns None.
    
    Uses Floyd's Cycle Detection Algorithm (Tortoise and Hare)
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not head or not head.next:
        return None
    
    # Phase 1: Detect if there's a cycle
    slow = head
    fast = head
    
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        
        if slow == fast:
            break
    else:
        # No cycle detected
        return None
    
    # Phase 2: Find the start of the cycle
    # Move one pointer to head, keep the other at meeting point
    # Then move both at same speed until they meet
    slow = head
    while slow != fast:
        slow = slow.next
        fast = fast.next
    
    return slow

# Test function
if __name__ == "__main__":
    # Create a linked list with cycle starting at 3rd node
    # Nodes: 1 -> 2 -> 3 -> 4 -> 5 -> 3 (cycle back to 3)
    node1 = ListNode(1)
    node2 = ListNode(2)
    node3 = ListNode(3)
    node4 = ListNode(4)
    node5 = ListNode(5)
    
    node1.next = node2
    node2.next = node3
    node3.next = node4
    node4.next = node5
    node5.next = node3  # Cycle back to 3rd node
    
    cycle_start = detect_cycle(node1)
    
    if cycle_start:
        print(f"Cycle detected starting at node with value: {cycle_start.val}")
    else:
        print("No cycle detected")
    
    # Verify the result
    assert cycle_start.val == 3, "Cycle should start at node with value 3"
    print("Test passed!")