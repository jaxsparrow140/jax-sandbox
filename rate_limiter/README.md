# Sliding Window Rate Limiter

## Overview

This implementation provides a sliding window rate limiter using the log-based algorithm. It allows N requests per M seconds and handles burst traffic correctly.

## Features

- Implements sliding window algorithm with timestamp logging
- Accurately handles burst requests
- Provides methods to check current request count
- Thread-safe for single-threaded use cases

## Usage

```python
from rate_limiter import SlidingWindowRateLimiter

# Create limiter: 10 requests per 5 seconds
limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=5)

# Check if request is allowed
if limiter.allow_request():
    # Process request
    pass
else:
    # Rate limit exceeded
    print("Rate limit exceeded")
```

## Testing

Run tests with:

```bash
python3 test_rate_limiter.py
```

The test simulates 100 requests over 10 seconds with a limit of 10 requests per 5 seconds.
Expected result: Approximately 20 requests allowed (10 per 5-second window).

## Algorithm

The sliding window algorithm works by:

1. Maintaining a list of request timestamps
2. For each new request:
   - Remove all timestamps older than (current_time - window_seconds)
   - If the number of remaining timestamps < max_requests, allow the request and add the current timestamp
   - Otherwise, deny the request

This approach provides accurate rate limiting even with bursty traffic patterns.