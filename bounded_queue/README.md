# Bounded Blocking Queue Implementation

## Overview

This is a thread-safe bounded blocking queue implementation in Python using only threading primitives (no queue.Queue allowed). It supports:

- `put(item)`: Blocks if the queue is full
- `get()`: Blocks if the queue is empty
- `put_nowait(item)`: Raises Full exception if queue is full
- `get_nowait()`: Raises Empty exception if queue is empty

## Implementation Details

The implementation uses:
- A list to store items
- A mutex (Lock) for thread-safe access
- Two Condition variables:
  - `not_empty`: Signaled when an item is added
  - `not_full`: Signaled when an item is removed

## Usage

1. Import the class:
```python
from bounded_queue import BoundedBlockingQueue
```

2. Create a queue with a maximum size:
```python
queue = BoundedBlockingQueue(maxsize=5)
```

3. Use the queue in producer-consumer scenarios:
```python
queue.put(item)  # Blocks if full
queue.get()      # Blocks if empty
queue.put_nowait(item)  # Raises Full if full
queue.get_nowait()      # Raises Empty if empty
```

## Running the Test

To run the producer-consumer test:

```bash
cd ~/jax-sandbox/bounded_queue
python test_bounded_queue.py
```

The test creates 3 producers and 2 consumers with a queue capacity of 5. Each producer adds 5 items, and consumers remove items as they become available.

## License

MIT License
