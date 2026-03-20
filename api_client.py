import requests
import time
from typing import Optional


class APIClient:
    """Simple REST API client with rate limit handling."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers['Authorization'] = f'Bearer {api_key}'
        self._rate_limit_remaining: Optional[int] = None
        self._rate_limit_reset: Optional[float] = None

    def _update_rate_limit(self, response: requests.Response) -> None:
        """Parse and store rate limit headers from a response."""
        remaining = response.headers.get('X-RateLimit-Remaining')
        reset = response.headers.get('X-RateLimit-Reset')
        if remaining is not None:
            self._rate_limit_remaining = int(remaining)
        if reset is not None:
            self._rate_limit_reset = float(reset)

    def _wait_for_reset(self) -> None:
        """Sleep until the rate limit window resets."""
        if self._rate_limit_reset is not None:
            wait = self._rate_limit_reset - time.time()
            if wait > 0:
                time.sleep(wait)

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Execute an HTTP request with rate limit awareness and retry logic."""
        url = f'{self.base_url}/{endpoint.lstrip("/")}'
        max_retries = 3

        # If we already know the window is exhausted, wait before sending.
        if self._rate_limit_remaining is not None and self._rate_limit_remaining <= 0:
            self._wait_for_reset()

        for attempt in range(max_retries):
            resp = self.session.request(method, url, **kwargs)
            self._update_rate_limit(resp)

            if resp.status_code == 429:
                # Rate limited — wait for reset then retry (if attempts remain).
                self._wait_for_reset()
                if attempt < max_retries - 1:
                    continue
                # Exhausted retries; surface the error.
                resp.raise_for_status()

            resp.raise_for_status()
            return resp.json()

        # Should be unreachable, but satisfy the type checker.
        raise RuntimeError("Exceeded maximum retry attempts")

    def get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make a GET request and return JSON response."""
        return self._request('GET', endpoint, params=params)

    def post(self, endpoint: str, data: dict) -> dict:
        """Make a POST request and return JSON response."""
        return self._request('POST', endpoint, json=data)
