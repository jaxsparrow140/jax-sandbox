# Sliding Window Rate Limiter

## Overview

This implementation provides a rate limiter using the sliding window log algorithm. Unlike fixed window algorithms, the sliding window approach accurately handles bursty traffic by tracking individual request timestamps and allowing requests based on a moving time window.

## Implementation Details

- **Algorithm**: Sliding window log
- **Key feature**: Tracks exact request timestamps to handle bursts correctly
- **Limit**: N requests per M seconds
- **Memory usage**: Stores timestamps for each request (memory grows linearly with requests)

## Usage

```python
from rate_limiter import SlidingWindowRateLimiter

# Create limiter: 10 requests per 5 seconds
limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=5)

# Check if request is allowed
if limiter.allow_request():
    # Process request
    print("Request allowed")
else:
    # Reject request
    print("Request denied - rate limit exceeded")
```

## Testing

The test suite simulates 100 requests over 10 seconds with a limit of 10 requests per 5 seconds. The sliding window algorithm should allow approximately 20 requests in total (10 in each 5-second window), with some variation due to the bursty pattern and exact timing.

Run tests with:
```bash
python test_rate_limiter.py
```

## Advantages over Fixed Window

- Accurately handles bursty traffic
- No "cliff edge" at window boundaries
- More fair distribution of requests

## Limitations

- Memory usage grows with the number of requests (stores timestamps)
- For very high throughput, consider using a token bucket or fixed window with interpolation

## License

MIT
