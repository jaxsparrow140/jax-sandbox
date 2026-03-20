"""Tests for APIClient."""

import time
import pytest
import requests
import requests_mock as req_mock_module

from api_client import APIClient


BASE = "https://api.example.com"
KEY  = "test-key"


@pytest.fixture
def client():
    return APIClient(BASE, KEY)


# ── Helpers ────────────────────────────────────────────────────────────────

def _rl_headers(remaining: int, reset_offset: float = 60) -> dict:
    """Build rate-limit response headers."""
    return {
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset":     str(time.time() + reset_offset),
    }


# ── Basic GET / POST ───────────────────────────────────────────────────────

def test_get_returns_json(client, requests_mock):
    requests_mock.get(f"{BASE}/items", json={"items": [1, 2, 3]})
    assert client.get("/items") == {"items": [1, 2, 3]}


def test_get_sends_auth_header(client, requests_mock):
    requests_mock.get(f"{BASE}/me", json={})
    client.get("/me")
    assert requests_mock.last_request.headers["Authorization"] == f"Bearer {KEY}"


def test_get_passes_params(client, requests_mock):
    requests_mock.get(f"{BASE}/search", json={})
    client.get("/search", params={"q": "hello"})
    assert requests_mock.last_request.qs == {"q": ["hello"]}


def test_post_sends_json_body(client, requests_mock):
    requests_mock.post(f"{BASE}/create", json={"id": 42})
    result = client.post("/create", data={"name": "widget"})
    assert result == {"id": 42}
    assert requests_mock.last_request.json() == {"name": "widget"}


def test_raises_on_non_429_error(client, requests_mock):
    requests_mock.get(f"{BASE}/bad", status_code=404)
    with pytest.raises(requests.HTTPError):
        client.get("/bad")


# ── Rate-limit header parsing ──────────────────────────────────────────────

def test_rate_limit_remaining_tracked(client, requests_mock):
    requests_mock.get(
        f"{BASE}/items",
        json={},
        headers=_rl_headers(remaining=5),
    )
    client.get("/items")
    assert client._rate_limit_remaining == 5


def test_rate_limit_reset_tracked(client, requests_mock):
    reset_at = time.time() + 30
    requests_mock.get(
        f"{BASE}/items",
        json={},
        headers={
            "X-RateLimit-Remaining": "3",
            "X-RateLimit-Reset":     str(reset_at),
        },
    )
    client.get("/items")
    assert abs(client._rate_limit_reset - reset_at) < 0.1


# ── 429 retry logic ────────────────────────────────────────────────────────

def test_retries_on_429_then_succeeds(client, requests_mock):
    """First two calls return 429; third succeeds."""
    adapter = requests_mock.get(
        f"{BASE}/slow",
        [
            {"status_code": 429, "headers": _rl_headers(0, reset_offset=0.01)},
            {"status_code": 429, "headers": _rl_headers(0, reset_offset=0.01)},
            {"json": {"ok": True},  "headers": _rl_headers(10)},
        ],
    )
    result = client.get("/slow")
    assert result == {"ok": True}
    assert adapter.call_count == 3


def test_raises_after_three_429s(client, requests_mock):
    """Three consecutive 429s should propagate as HTTPError."""
    requests_mock.get(
        f"{BASE}/nope",
        [
            {"status_code": 429, "headers": _rl_headers(0, reset_offset=0.01)},
            {"status_code": 429, "headers": _rl_headers(0, reset_offset=0.01)},
            {"status_code": 429, "headers": _rl_headers(0, reset_offset=0.01)},
        ],
    )
    with pytest.raises(requests.HTTPError):
        client.get("/nope")


# ── Pre-emptive wait (remaining == 0 from prior response) ──────────────────

def test_preemptive_wait_when_budget_zero(client, requests_mock, monkeypatch):
    """When _rate_limit_remaining is already 0, _wait_for_reset is called before the request."""
    waited = []

    def fake_wait(self):
        waited.append(True)
        self._rate_limit_remaining = None   # simulate window reset

    monkeypatch.setattr(APIClient, "_wait_for_reset", fake_wait)
    requests_mock.get(f"{BASE}/ok", json={"ok": True})

    client._rate_limit_remaining = 0
    client._rate_limit_reset = time.time() + 0.01
    result = client.get("/ok")

    assert result == {"ok": True}
    assert waited, "_wait_for_reset should have been called pre-emptively"
