"""Tests for SlidingWindowRateLimiter."""

import time
import threading
import pytest

from rate_limiter import SlidingWindowRateLimiter


# ── Construction ──────────────────────────────────────────────────────────────

def test_invalid_max_requests():
    with pytest.raises(ValueError):
        SlidingWindowRateLimiter(max_requests=0, window_seconds=10)


def test_invalid_window_seconds():
    with pytest.raises(ValueError):
        SlidingWindowRateLimiter(max_requests=5, window_seconds=0)


# ── Basic allow / deny ────────────────────────────────────────────────────────

def test_allows_up_to_max_requests():
    limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=60)
    assert limiter.is_allowed("alice") is True
    assert limiter.is_allowed("alice") is True
    assert limiter.is_allowed("alice") is True


def test_denies_when_over_quota():
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60)
    limiter.is_allowed("bob")
    limiter.is_allowed("bob")
    assert limiter.is_allowed("bob") is False


def test_clients_are_isolated():
    limiter = SlidingWindowRateLimiter(max_requests=1, window_seconds=60)
    assert limiter.is_allowed("client-a") is True
    assert limiter.is_allowed("client-b") is True  # separate quota


# ── get_remaining ─────────────────────────────────────────────────────────────

def test_remaining_starts_at_max():
    limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=60)
    assert limiter.get_remaining("new-client") == 5


def test_remaining_decreases_on_allowed_request():
    limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=60)
    limiter.is_allowed("carol")
    assert limiter.get_remaining("carol") == 4


def test_remaining_zero_when_quota_exhausted():
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60)
    limiter.is_allowed("dave")
    limiter.is_allowed("dave")
    limiter.is_allowed("dave")  # denied, should NOT decrement further
    assert limiter.get_remaining("dave") == 0


# ── reset ─────────────────────────────────────────────────────────────────────

def test_reset_restores_full_quota():
    limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=60)
    limiter.is_allowed("eve")
    limiter.is_allowed("eve")
    limiter.reset("eve")
    assert limiter.get_remaining("eve") == 3


def test_reset_does_not_affect_other_clients():
    limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=60)
    limiter.is_allowed("frank")
    limiter.is_allowed("grace")
    limiter.reset("frank")
    assert limiter.get_remaining("grace") == 2


# ── Sliding window expiry ─────────────────────────────────────────────────────

def test_old_requests_expire_from_window():
    """Requests older than window_seconds should slide out, freeing quota."""
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=0.2)
    assert limiter.is_allowed("henry") is True
    assert limiter.is_allowed("henry") is True
    assert limiter.is_allowed("henry") is False  # quota full

    time.sleep(0.25)  # let the window expire

    # Old timestamps gone — full quota again
    assert limiter.is_allowed("henry") is True


# ── Thread safety ─────────────────────────────────────────────────────────────

def test_concurrent_requests_respect_quota():
    """Under concurrent load, the number of allowed requests must not exceed max_requests."""
    max_req = 50
    limiter = SlidingWindowRateLimiter(max_requests=max_req, window_seconds=60)
    allowed = []
    lock = threading.Lock()

    def attempt():
        result = limiter.is_allowed("shared")
        with lock:
            allowed.append(result)

    threads = [threading.Thread(target=attempt) for _ in range(max_req * 3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert sum(allowed) == max_req
