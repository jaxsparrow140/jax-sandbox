"""
A Python LRU (Least Recently Used) Cache implementation from scratch.

Uses a doubly linked list for ordering and a dictionary for O(1) lookups.
"""

class Node:
    """Doubly linked list node."""
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    """LRU Cache with O(1) get and put operations."""
    
    def __init__(self, capacity: int):
        """Initialize the LRU cache with given capacity."""
        self.capacity = capacity
        self.cache = {}  # key -> Node
        
        # Dummy head and tail nodes to simplify operations
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _add_node(self, node: Node):
        """Add a new node right after head."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def _remove_node(self, node: Node):
        """Remove an existing node from the linked list."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _move_to_head(self, node: Node):
        """Move a node to the head (most recently used)."""
        self._remove_node(node)
        self._add_node(node)
    
    def _pop_tail(self) -> Node:
        """Remove and return the tail node (least recently used)."""
        node = self.tail.prev
        self._remove_node(node)
        return node
    
    def get(self, key: int) -> int:
        """Get the value of the key if it exists, otherwise return -1."""
        if key in self.cache:
            node = self.cache[key]
            # Move this node to head (most recently used)
            self._move_to_head(node)
            return node.value
        return -1
    
    def put(self, key: int, value: int) -> None:
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
            
            # Check if we exceed capacity
            if len(self.cache) > self.capacity:
                # Remove tail (least recently used)
                tail_node = self._pop_tail()
                del self.cache[tail_node.key]

# Test the implementation
if __name__ == "__main__":
    # Test case 1: Basic functionality
    lru = LRUCache(2)
    lru.put(1, 1)
    lru.put(2, 2)
    print(f"get(1): {lru.get(1)}")  # returns 1
    lru.put(3, 3)  # evicts key 2
    print(f"get(2): {lru.get(2)}")  # returns -1 (not found)
    lru.put(4, 4)  # evicts key 1
    print(f"get(1): {lru.get(1)}")  # returns -1 (not found)
    print(f"get(3): {lru.get(3)}")  # returns 3
    print(f"get(4): {lru.get(4)}")  # returns 4
    
    # Test case 2: Edge case - capacity 1
    lru2 = LRUCache(1)
    lru2.put(2, 1)
    print(f"get(2): {lru2.get(2)}")  # returns 1
    lru2.put(3, 2)  # evicts key 2
    print(f"get(2): {lru2.get(2)}")  # returns -1
    print(f"get(3): {lru2.get(3)}")  # returns 2
    
    # Test case 3: Repeated access to same key
    lru3 = LRUCache(3)
    lru3.put(1, 1)
    lru3.put(2, 2)
    lru3.put(3, 3)
    print(f"get(1): {lru3.get(1)}")  # returns 1
    print(f"get(2): {lru3.get(2)}")  # returns 2
    print(f"get(3): {lru3.get(3)}")  # returns 3
    lru3.put(4, 4)  # evicts key 1 (least recently used)
    print(f"get(1): {lru3.get(1)}")  # returns -1
    print(f"get(4): {lru3.get(4)}")  # returns 4
    print(f"get(2): {lru3.get(2)}")  # returns 2 (still there)
    print(f"get(3): {lru3.get(3)}")  # returns 3 (still there)
    
    # Test case 4: Update existing key
    lru4 = LRUCache(2)
    lru4.put(1, 1)
    lru4.put(2, 2)
    lru4.put(1, 10)  # update key 1
    print(f"get(1): {lru4.get(1)}")  # returns 10
    lru4.put(3, 3)  # evicts key 2 (least recently used)
    print(f"get(2): {lru4.get(2)}")  # returns -1
    print(f"get(1): {lru4.get(1)}")  # returns 10
    print(f"get(3): {lru4.get(3)}")  # returns 3