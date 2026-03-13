"""
Linked List Cycle Detection

Implements Floyd's Cycle Detection Algorithm (Tortoise and Hare)
to detect cycles in a linked list and find the start of the cycle in O(n) time and O(1) space.
"""

class ListNode:
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
        # No cycle found
        return None
    
    # Phase 2: Find the start of the cycle
    # Move slow to head, keep fast at meeting point
    slow = head
    while slow != fast:
        slow = slow.next
        fast = fast.next
    
    return slow  # This is the start of the cycle

# Test function
if __name__ == "__main__":
    # Create a linked list with a cycle starting at the 3rd node
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
    node5.next = node3  # Create cycle starting at node 3
    
    # Test the function
    cycle_start = detect_cycle(node1)
    
    if cycle_start:
        print(f"Cycle detected starting at node with value: {cycle_start.val}")
        print(f"Expected: 3 (3rd node) - {'PASS' if cycle_start.val == 3 else 'FAIL'}")
    else:
        print("No cycle detected")
    
    # Test with no cycle
    node6 = ListNode(6)
    node7 = ListNode(7)
    node6.next = node7
    
    no_cycle = detect_cycle(node6)
    print(f"No cycle test: {'PASS' if no_cycle is None else 'FAIL'}")
    
    # Test with single node
    single_node = ListNode(8)
    single_cycle = detect_cycle(single_node)
    print(f"Single node test: {'PASS' if single_cycle is None else 'FAIL'}")
    
    # Test with two nodes, no cycle
    two_nodes = ListNode(9)
    two_nodes.next = ListNode(10)
    two_cycle = detect_cycle(two_nodes)
    print(f"Two nodes no cycle test: {'PASS' if two_cycle is None else 'FAIL'}")
    
    # Test with two nodes, cycle
    two_cycle_nodes = ListNode(11)
    two_cycle_nodes.next = ListNode(12)
    two_cycle_nodes.next.next = two_cycle_nodes  # Cycle back to itself
    
    two_cycle_start = detect_cycle(two_cycle_nodes)
    print(f"Two nodes cycle test: {'PASS' if two_cycle_start.val == 11 else 'FAIL'}")