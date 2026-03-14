"""
A simple LRU (Least Recently Used) cache implementation from scratch.

Uses a doubly linked list to maintain order of usage and a dictionary for O(1) lookups.
"""

class Node:
    """Doubly linked list node to store key-value pairs."""
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    """LRU Cache implementation with O(1) get and put operations."""
    
    def __init__(self, capacity):
        """Initialize the LRU cache with given capacity."""
        self.capacity = capacity
        self.cache = {}  # Dictionary to store key -> Node mapping
        
        # Dummy head and tail nodes to simplify edge cases
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _add_node(self, node):
        """Add a new node right after head."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def _remove_node(self, node):
        """Remove an existing node from the linked list."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _move_to_head(self, node):
        """Move a node to the head of the linked list (most recently used)."""
        self._remove_node(node)
        self._add_node(node)
    
    def _pop_tail(self):
        """Remove and return the tail node (least recently used)."""
        node = self.tail.prev
        self._remove_node(node)
        return node
    
    def get(self, key):
        """Get the value of the key if it exists in the cache, otherwise return -1."""
        if key in self.cache:
            node = self.cache[key]
            # Move this node to the head (most recently used)
            self._move_to_head(node)
            return node.value
        return -1
    
    def put(self, key, value):
        """Set or insert the value if the key is not already present."""
        if key in self.cache:
            # Update existing node
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            # Create new node
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_node(new_node)
            
            # If cache exceeds capacity, remove the least recently used item
            if len(self.cache) > self.capacity:
                tail_node = self._pop_tail()
                del self.cache[tail_node.key]

# Test the implementation
if __name__ == "__main__":
    # Test case 1: Basic functionality
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    print(f"get(1): {cache.get(1)}")  # returns 1
    cache.put(3, 3)  # evicts key 2
    print(f"get(2): {cache.get(2)}")  # returns -1 (not found)
    cache.put(4, 4)  # evicts key 1
    print(f"get(1): {cache.get(1)}")  # returns -1 (not found)
    print(f"get(3): {cache.get(3)}")  # returns 3
    print(f"get(4): {cache.get(4)}")  # returns 4
    
    # Test case 2: Capacity of 1
    cache = LRUCache(1)
    cache.put(2, 1)
    print(f"get(2): {cache.get(2)}")  # returns 1
    cache.put(3, 2)  # evicts key 2
    print(f"get(2): {cache.get(2)}")  # returns -1
    print(f"get(3): {cache.get(3)}")  # returns 2
    
    # Test case 3: Get operations without putting
    cache = LRUCache(3)
    print(f"get(1): {cache.get(1)}")  # returns -1 (not found)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.put(3, 3)
    print(f"get(1): {cache.get(1)}")  # returns 1
    print(f"get(2): {cache.get(2)}")  # returns 2
    print(f"get(3): {cache.get(3)}")  # returns 3
    cache.put(4, 4)  # evicts key 1 (least recently used)
    print(f"get(1): {cache.get(1)}")  # returns -1
    print(f"get(4): {cache.get(4)}")  # returns 4
    print(f"get(2): {cache.get(2)}")  # returns 2
    print(f"get(3): {cache.get(3)}")  # returns 3