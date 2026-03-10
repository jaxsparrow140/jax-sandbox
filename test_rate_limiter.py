"""
Tests for the sliding-window-log RateLimiter.

Burst simulation
----------------
100 requests are sent over a 10-second span with a limit of
10 requests per 5-second window.

Expected behaviour:
  - At most 10 requests are allowed in any rolling 5-second window.
  - Total allowed requests ≤ 20 across the full 10 s
    (two non-overlapping 5-second windows).
  - Because the window is *sliding*, up to ~20 can be allowed in practice
    (first 10 early in the span, next 10 once the first 10 age out).
"""

import time
from rate_limiter import RateLimiter


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def simulate_requests(
    limiter: RateLimiter,
    total: int,
    duration_s: float,
) -> tuple[list[float], list[bool]]:
    """
    Fire `total` requests evenly spaced over `duration_s` seconds.

    Returns
    -------
    timestamps : list[float]
        Simulated timestamp of each request (does NOT use real sleep).
    results    : list[bool]
        allow_request() result for each request.
    """
    interval = duration_s / total
    timestamps = [i * interval for i in range(total)]
    results = [limiter.allow_request(now=t) for t in timestamps]
    return timestamps, results


# ---------------------------------------------------------------------------
# Core correctness tests
# ---------------------------------------------------------------------------

def test_basic_allow():
    """First N requests in an empty window must all be allowed."""
    rl = RateLimiter(max_requests=3, window_seconds=1.0)
    assert rl.allow_request(now=0.0) is True
    assert rl.allow_request(now=0.1) is True
    assert rl.allow_request(now=0.2) is True


def test_basic_deny():
    """Request N+1 within the window must be rejected."""
    rl = RateLimiter(max_requests=3, window_seconds=1.0)
    rl.allow_request(now=0.0)
    rl.allow_request(now=0.1)
    rl.allow_request(now=0.2)
    assert rl.allow_request(now=0.3) is False


def test_window_slide_allows_new_request():
    """
    After a full window has elapsed the oldest requests age out
    and fresh capacity opens up.
    """
    rl = RateLimiter(max_requests=3, window_seconds=1.0)
    rl.allow_request(now=0.0)
    rl.allow_request(now=0.1)
    rl.allow_request(now=0.2)
    # 0.3 s is still inside the window → rejected
    assert rl.allow_request(now=0.3) is False
    # 1.1 s: the entry at t=0.0 has aged out (cutoff = 1.1 - 1.0 = 0.1,
    # strictly, entries ≤ cutoff are pruned, so t=0.0 is evicted but t=0.1
    # is NOT yet evicted).  Count = 2 → allowed.
    assert rl.allow_request(now=1.1) is True


def test_exact_boundary():
    """
    An entry exactly at the cutoff boundary (timestamp == now - window)
    should be evicted (closed-open interval: [cutoff, now]).
    """
    rl = RateLimiter(max_requests=1, window_seconds=1.0)
    rl.allow_request(now=0.0)
    # At now=1.0 the entry at t=0.0 sits exactly at the boundary and is
    # evicted, so the request at now=1.0 should be allowed.
    assert rl.allow_request(now=1.0) is True


def test_reset():
    """reset() clears the log and restores full capacity."""
    rl = RateLimiter(max_requests=2, window_seconds=1.0)
    rl.allow_request(now=0.0)
    rl.allow_request(now=0.1)
    assert rl.allow_request(now=0.2) is False
    rl.reset()
    assert rl.allow_request(now=0.2) is True


def test_current_count():
    rl = RateLimiter(max_requests=5, window_seconds=1.0)
    rl.allow_request(now=0.0)
    rl.allow_request(now=0.5)
    # At now=0.8: both entries are in-window
    assert rl.current_count(now=0.8) == 2
    # At now=1.1: entry at 0.0 is evicted (cutoff=0.1 > 0.0)
    assert rl.current_count(now=1.1) == 1


def test_invalid_params():
    import pytest
    with pytest.raises(ValueError):
        RateLimiter(max_requests=0, window_seconds=1.0)
    with pytest.raises(ValueError):
        RateLimiter(max_requests=5, window_seconds=0)


# ---------------------------------------------------------------------------
# Burst simulation — 100 requests over 10 s, limit 10 per 5 s
# ---------------------------------------------------------------------------

def test_burst_simulation():
    """
    Simulate 100 requests evenly spread over 10 seconds.
    Rate limit: 10 requests per 5-second sliding window.

    Invariants checked:
    1. No 5-second window contains more than 10 allowed requests.
    2. Total allowed requests is reasonable (≤ 20 for a 10 s span).
    3. Some requests are rejected (the burst hits the ceiling).
    """
    MAX_REQ = 10
    WINDOW_S = 5.0
    TOTAL_REQUESTS = 100
    DURATION_S = 10.0

    rl = RateLimiter(max_requests=MAX_REQ, window_seconds=WINDOW_S)
    timestamps, results = simulate_requests(rl, TOTAL_REQUESTS, DURATION_S)

    allowed_times = [t for t, ok in zip(timestamps, results) if ok]
    denied_count  = results.count(False)
    allowed_count = results.count(True)

    print(f"\n{'='*60}")
    print(f"Burst simulation: {TOTAL_REQUESTS} requests over {DURATION_S}s")
    print(f"Limit: {MAX_REQ} requests per {WINDOW_S}s window")
    print(f"{'='*60}")
    print(f"  Allowed : {allowed_count}")
    print(f"  Denied  : {denied_count}")
    print(f"  Allowed timestamps (s): {[round(t, 3) for t in allowed_times]}")
    print(f"{'='*60}\n")

    # ── Invariant 1: sliding-window constraint ──────────────────────────
    # For every pair of allowed timestamps tA and tB where tB - tA < WINDOW_S,
    # count how many allowed timestamps fall in [tA, tB).  Must be ≤ MAX_REQ.
    for i, t_start in enumerate(allowed_times):
        window_count = sum(
            1 for t in allowed_times
            if t_start <= t < t_start + WINDOW_S
        )
        assert window_count <= MAX_REQ, (
            f"Window starting at {t_start:.3f}s has {window_count} allowed "
            f"requests (limit {MAX_REQ})"
        )

    # ── Invariant 2: sanity on totals ───────────────────────────────────
    # Over 10 s with a 5 s window the theoretical max is 20.
    # (First 10 immediately, next 10 after the first batch ages out.)
    assert allowed_count <= 20, (
        f"Too many requests allowed: {allowed_count} (expected ≤ 20)"
    )
    assert allowed_count > 0, "No requests were allowed — something's wrong"

    # ── Invariant 3: limiter actually rejected requests ──────────────────
    assert denied_count > 0, "All requests were allowed — limiter did nothing"

    print("✅ All burst-simulation invariants passed.")


# ---------------------------------------------------------------------------
# Real-time smoke test (uses actual wall clock; kept short)
# ---------------------------------------------------------------------------

def test_realtime_smoke():
    """
    Quick real-time test: 5 rapid requests with limit=3/0.5s.
    The first 3 should be allowed, the next 2 denied.
    After sleeping past the window the next 3 should be allowed again.
    """
    rl = RateLimiter(max_requests=3, window_seconds=0.5)

    results = [rl.allow_request() for _ in range(5)]
    assert results[:3] == [True, True, True], "First 3 should be allowed"
    assert results[3:] == [False, False],      "Requests 4-5 should be denied"

    time.sleep(0.6)  # let the window expire

    fresh = [rl.allow_request() for _ in range(3)]
    assert fresh == [True, True, True], "After window reset, 3 should be allowed"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import pytest, sys
    sys.exit(pytest.main([__file__, "-v"]))
