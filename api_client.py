import requests
import time
from typing import Optional


class APIClient:
    """Simple REST API client."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers['Authorization'] = f'Bearer {api_key}'
        self._rate_limit_remaining: Optional[int] = None
        self._rate_limit_reset: Optional[float] = None

    def _update_rate_limit(self, resp: requests.Response) -> None:
        """Parse and store rate limit headers from a response."""
        remaining = resp.headers.get('X-RateLimit-Remaining')
        reset = resp.headers.get('X-RateLimit-Reset')
        if remaining is not None:
            self._rate_limit_remaining = int(remaining)
        if reset is not None:
            self._rate_limit_reset = float(reset)

    def _wait_for_reset(self) -> None:
        """Sleep until the rate limit window resets, then clear the exhausted state."""
        if self._rate_limit_reset is not None:
            wait = self._rate_limit_reset - time.time()
            if wait > 0:
                time.sleep(wait)
        # After waiting, the window has reset — clear so we don't loop-wait again.
        self._rate_limit_remaining = None

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Execute an HTTP request with rate-limit awareness and retry logic."""
        url = f'{self.base_url}/{endpoint.lstrip("/")}'
        max_attempts = 3
        last_resp: Optional[requests.Response] = None

        for attempt in range(max_attempts):
            # Proactively wait if we already know the quota is exhausted.
            if self._rate_limit_remaining == 0:
                self._wait_for_reset()

            last_resp = self.session.request(method, url, **kwargs)
            self._update_rate_limit(last_resp)

            if last_resp.status_code == 429:
                if attempt < max_attempts - 1:
                    # Wait for the window to reset, then retry.
                    self._wait_for_reset()
                    continue
                # Final attempt still rate-limited — let raise_for_status surface it.

            last_resp.raise_for_status()
            return last_resp.json()

        # Safety fallback (unreachable in practice — loop always raises or returns).
        last_resp.raise_for_status()  # type: ignore[union-attr]
        return last_resp.json()  # type: ignore[union-attr]

    def get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make a GET request and return JSON response."""
        return self._request('GET', endpoint, params=params)

    def post(self, endpoint: str, data: dict) -> dict:
        """Make a POST request and return JSON response."""
        return self._request('POST', endpoint, json=data)
