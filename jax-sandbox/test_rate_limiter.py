"""Tests for the sliding-window-log RateLimiter.

Requirement-focused simulation
------------------------------
Simulate 100 requests over 10 seconds with a limit of 10 requests per 5 seconds.
Also includes an explicit burst test to ensure correctness under bursts.
"""

import time

from rate_limiter import RateLimiter


def _assert_raises(exc_type, fn):
    try:
        fn()
    except exc_type:
        return
    assert False, f"Expected {exc_type.__name__} to be raised"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def simulate_requests_evenly(limiter: RateLimiter, total: int, duration_s: float):
    """Fire `total` requests evenly spaced over `duration_s` seconds."""
    interval = duration_s / total
    timestamps = [i * interval for i in range(total)]
    results = [limiter.allow_request(now=t) for t in timestamps]
    return timestamps, results


# ---------------------------------------------------------------------------
# Core correctness tests
# ---------------------------------------------------------------------------

def test_basic_allow():
    rl = RateLimiter(max_requests=3, window_seconds=1.0)
    assert rl.allow_request(now=0.0) is True
    assert rl.allow_request(now=0.1) is True
    assert rl.allow_request(now=0.2) is True


def test_basic_deny():
    rl = RateLimiter(max_requests=3, window_seconds=1.0)
    rl.allow_request(now=0.0)
    rl.allow_request(now=0.1)
    rl.allow_request(now=0.2)
    assert rl.allow_request(now=0.3) is False


def test_window_slide_allows_new_request():
    rl = RateLimiter(max_requests=3, window_seconds=1.0)
    rl.allow_request(now=0.0)
    rl.allow_request(now=0.1)
    rl.allow_request(now=0.2)
    assert rl.allow_request(now=0.3) is False
    # At now=1.1, t=0.0 is out of window and pruned → one slot opens.
    assert rl.allow_request(now=1.1) is True


def test_exact_boundary_evicted():
    rl = RateLimiter(max_requests=1, window_seconds=1.0)
    rl.allow_request(now=0.0)
    # At now=1.0, cutoff==0.0, and timestamps <= cutoff are pruned.
    assert rl.allow_request(now=1.0) is True


def test_reset():
    rl = RateLimiter(max_requests=2, window_seconds=1.0)
    rl.allow_request(now=0.0)
    rl.allow_request(now=0.1)
    assert rl.allow_request(now=0.2) is False
    rl.reset()
    assert rl.allow_request(now=0.2) is True


def test_current_count_prunes():
    rl = RateLimiter(max_requests=5, window_seconds=1.0)
    rl.allow_request(now=0.0)
    rl.allow_request(now=0.5)
    assert rl.current_count(now=0.8) == 2
    assert rl.current_count(now=1.1) == 1


def test_invalid_params():
    _assert_raises(ValueError, lambda: RateLimiter(max_requests=0, window_seconds=1.0))
    _assert_raises(ValueError, lambda: RateLimiter(max_requests=5, window_seconds=0))


# ---------------------------------------------------------------------------
# Requirement: 100 requests over 10 seconds, limit 10 per 5 seconds
# ---------------------------------------------------------------------------

def test_simulate_100_requests_over_10_seconds_limit_10_per_5_seconds():
    MAX_REQ = 10
    WINDOW_S = 5.0
    TOTAL_REQUESTS = 100
    DURATION_S = 10.0

    rl = RateLimiter(max_requests=MAX_REQ, window_seconds=WINDOW_S)
    timestamps, results = simulate_requests_evenly(rl, TOTAL_REQUESTS, DURATION_S)

    allowed_times = [t for t, ok in zip(timestamps, results) if ok]
    allowed_count = results.count(True)
    denied_count = results.count(False)

    # With evenly-spaced requests at 0.1s intervals, the limiter should accept
    # 10 in the first ~1s, then another 10 once the first batch ages out.
    assert allowed_count == 20
    assert denied_count == 80

    # Sliding window invariant: no 5-second window contains > 10 allowed.
    for t_start in allowed_times:
        window_count = sum(1 for t in allowed_times if t_start <= t < t_start + WINDOW_S)
        assert window_count <= MAX_REQ


def test_handles_bursts():
    """Many requests at the same timestamp should still be limited correctly."""
    rl = RateLimiter(max_requests=10, window_seconds=5.0)

    burst1 = [rl.allow_request(now=0.0) for _ in range(50)]
    assert burst1.count(True) == 10

    burst2 = [rl.allow_request(now=5.0) for _ in range(50)]
    assert burst2.count(True) == 10


# ---------------------------------------------------------------------------
# Real-time smoke test (uses actual wall clock; kept short)
# ---------------------------------------------------------------------------

def test_realtime_smoke():
    rl = RateLimiter(max_requests=3, window_seconds=0.5)

    results = [rl.allow_request() for _ in range(5)]
    assert results[:3] == [True, True, True]
    assert results[3:] == [False, False]

    time.sleep(0.6)

    fresh = [rl.allow_request() for _ in range(3)]
    assert fresh == [True, True, True]
