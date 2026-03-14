"""
A pure Python LRU cache implementation with O(1) get and put operations.
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
    """
    LRU Cache with fixed capacity.
    Supports get(key) and put(key, value) with O(1) time complexity.
    Least recently used items are evicted when capacity is exceeded.
    """
    
    def __init__(self, capacity):
        """
        Initialize LRU cache with given capacity.
        
        Args:
            capacity (int): Maximum number of items the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self.cache = {}  # key -> Node
        
        # Dummy head and tail nodes to simplify operations
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _add_node(self, node):
        """Add a node right after head (most recently used)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def _remove_node(self, node):
        """Remove a node from the linked list."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _move_to_head(self, node):
        """Move a node to the head (most recently used)."""
        self._remove_node(node)
        self._add_node(node)
    
    def _pop_tail(self):
        """Remove and return the tail node (least recently used)."""
        node = self.tail.prev
        self._remove_node(node)
        return node
    
    def get(self, key):
        """
        Get the value of the key if it exists in the cache.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if key exists, None otherwise
        """
        if key in self.cache:
            # Move to head (mark as most recently used)
            node = self.cache[key]
            self._move_to_head(node)
            return node.value
        return None
    
    def put(self, key, value):
        """
        Add or update a key-value pair in the cache.
        
        Args:
            key: The key to add/update
            value: The value to store
        """
        if key in self.cache:
            # Update existing node
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            # Add new node
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_node(new_node)
            
            # If capacity exceeded, evict LRU item
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
    print(f"get(2): {cache.get(2)}")  # returns None (evicted)
    cache.put(4, 4)  # evicts key 1
    print(f"get(1): {cache.get(1)}")  # returns None (evicted)
    print(f"get(3): {cache.get(3)}")  # returns 3
    print(f"get(4): {cache.get(4)}")  # returns 4
    
    # Test case 2: Update existing key
    cache = LRUCache(3)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.put(3, 3)
    cache.put(2, 20)  # update key 2
    print(f"get(2): {cache.get(2)}")  # returns 20
    cache.put(4, 4)  # evicts key 1
    print(f"get(1): {cache.get(1)}")  # returns None
    print(f"get(2): {cache.get(2)}")  # returns 20
    print(f"get(3): {cache.get(3)}")  # returns 3
    print(f"get(4): {cache.get(4)}")  # returns 4
    
    # Test case 3: Capacity of 1
    cache = LRUCache(1)
    cache.put(1, 1)
    cache.put(2, 2)
    print(f"get(1): {cache.get(1)}")  # returns None
    print(f"get(2): {cache.get(2)}")  # returns 2
    
    # Test case 4: Edge case - capacity 0 (should raise error)
    try:
        cache = LRUCache(0)
    except ValueError as e:
        print(f"Error with capacity 0: {e}")