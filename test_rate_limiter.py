import time
import threading
from rate_limiter import SlidingWindowRateLimiter


def test_basic_limiting():
    limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=1.0)
    assert limiter.is_allowed('client_a') == True
    assert limiter.is_allowed('client_a') == True
    assert limiter.is_allowed('client_a') == True
    assert limiter.is_allowed('client_a') == False  # 4th request blocked


def test_window_expiry():
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=0.5)
    assert limiter.is_allowed('client_b') == True
    assert limiter.is_allowed('client_b') == True
    assert limiter.is_allowed('client_b') == False
    time.sleep(0.6)
    assert limiter.is_allowed('client_b') == True  # Window expired


def test_concurrent_clients():
    limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=5.0)
    results = {'allowed': 0, 'denied': 0}
    results_lock = threading.Lock()

    def make_requests(client_id, count):
        for _ in range(count):
            if limiter.is_allowed(client_id):
                with results_lock:
                    results['allowed'] += 1
            else:
                with results_lock:
                    results['denied'] += 1

    threads = []
    for i in range(5):
        t = threading.Thread(target=make_requests, args=(f'client_{i}', 15))
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Each client should have at most 10 allowed
    # 5 clients × 15 requests = 75 total, 5 × 10 = 50 max allowed
    assert results['allowed'] <= 50, f"Too many allowed: {results['allowed']}"
    assert results['allowed'] + results['denied'] == 75
