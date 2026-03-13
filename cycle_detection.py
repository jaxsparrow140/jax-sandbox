"""
Linked List Cycle Detection

Implements Floyd's Cycle Detection Algorithm (Tortoise and Hare)
to detect cycles in a linked list and find the start of the cycle.

Time Complexity: O(n)
Space Complexity: O(1)
"""

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def detect_cycle(head):
    """
    Detects if a linked list has a cycle and returns the node where the cycle begins.
    
    Args:
        head: The head node of the linked list
        
    Returns:
        The node where the cycle begins, or None if no cycle exists
    """
    if not head or not head.next:
        return None
    
    # Phase 1: Detect if there's a cycle using Floyd's algorithm
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


def create_test_list_with_cycle():
    """
    Creates a test linked list with a cycle starting at the 3rd node.
    
    List structure: 1 -> 2 -> 3 -> 4 -> 5 -> 3 (cycle back to node 3)
    """
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
    
    return node1


def print_list(head, max_nodes=20):
    """
    Helper function to print the linked list (for debugging)
    """
    nodes = []
    current = head
    count = 0
    
    while current and count < max_nodes:
        nodes.append(str(current.val))
        current = current.next
        count += 1
        
        # Check if we're in a cycle
        if count > 1 and current == head:
            nodes.append("[cycle detected]")
            break
    
    return " -> ".join(nodes) + (" ..." if count >= max_nodes else "")


# Test the implementation
if __name__ == "__main__":
    # Create test list with cycle starting at 3rd node
    head = create_test_list_with_cycle()
    
    print("Linked list:", print_list(head))
    
    # Find cycle start
    cycle_start = detect_cycle(head)
    
    if cycle_start:
        print(f"Cycle detected! Starts at node with value: {cycle_start.val}")
    else:
        print("No cycle detected")

    # Verify the result
    if cycle_start:
        # The cycle should start at node 3
        assert cycle_start.val == 3, "Cycle should start at node with value 3"
        print("Test passed: Cycle detected at correct position")
    else:
        print("Test failed: No cycle detected when one exists")