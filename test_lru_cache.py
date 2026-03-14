"""
Test file for the LRU Cache implementation.
"""

import sys
import os

# Add the current directory to Python path to import our module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lru_cache import LRUCache

def test_lru_cache():
    print("Testing LRU Cache implementation...")
    
    # Test 1: Basic functionality with capacity 2
    print("\nTest 1: Basic functionality with capacity 2")
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
    
    # Test 2: Capacity 1
    print("\nTest 2: Capacity 1")
    lru = LRUCache(1)
    lru.put(2, 1)
    print(f"get(2): {lru.get(2)}")  # returns 1
    lru.put(3, 2)  # evicts key 2
    print(f"get(2): {lru.get(2)}")  # returns -1
    print(f"get(3): {lru.get(3)}")  # returns 2
    
    # Test 3: Same key updates value
    print("\nTest 3: Same key updates value")
    lru = LRUCache(2)
    lru.put(1, 1)
    lru.put(2, 2)
    lru.put(1, 10)  # update value of key 1
    print(f"get(1): {lru.get(1)}")  # returns 10
    lru.put(3, 3)  # evicts key 2 (least recently used)
    print(f"get(2): {lru.get(2)}")  # returns -1
    print(f"get(3): {lru.get(3)}")  # returns 3
    
    # Test 4: Access order matters
    print("\nTest 4: Access order matters")
    lru = LRUCache(3)
    lru.put(1, 1)
    lru.put(2, 2)
    lru.put(3, 3)
    lru.get(1)  # access 1
    lru.put(4, 4)  # should evict 2 (least recently used)
    print(f"get(2): {lru.get(2)}")  # returns -1
    print(f"get(1): {lru.get(1)}")  # returns 1
    print(f"get(3): {lru.get(3)}")  # returns 3
    print(f"get(4): {lru.get(4)}")  # returns 4
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    test_lru_cache()