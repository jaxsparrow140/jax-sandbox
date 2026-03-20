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

    def _update_rate_limit(self, response: requests.Response) -> None:
        """Parse and cache rate limit headers from a response."""
        remaining = response.headers.get('X-RateLimit-Remaining')
        reset = response.headers.get('X-RateLimit-Reset')
        if remaining is not None:
            self._rate_limit_remaining = int(remaining)
        if reset is not None:
            self._rate_limit_reset = float(reset)

    def _wait_for_reset(self) -> None:
        """Sleep until the rate limit window resets."""
        if self._rate_limit_reset is not None:
            delay = self._rate_limit_reset - time.time()
            if delay > 0:
                time.sleep(delay)

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """
        Execute an HTTP request with automatic rate-limit handling.

        - Proactively waits before sending if remaining quota is already 0.
        - On HTTP 429, waits until the reset timestamp and retries.
        - Raises after exceeding MAX_RETRIES attempts.
        """
        MAX_RETRIES = 3
        url = f'{self.base_url}/{endpoint.lstrip("/")}'

        for attempt in range(MAX_RETRIES):
            # Proactive hold: quota exhausted from a previous response
            if self._rate_limit_remaining == 0:
                self._wait_for_reset()

            resp = self.session.request(method, url, **kwargs)
            self._update_rate_limit(resp)

            if resp.status_code == 429:
                if attempt < MAX_RETRIES - 1:
                    self._wait_for_reset()
                    continue
                # Final attempt still 429 — surface the error
                resp.raise_for_status()

            resp.raise_for_status()
            return resp.json()

        # Unreachable, but satisfies type checkers
        raise RuntimeError("Request failed after maximum retries")  # pragma: no cover

    def get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make a GET request and return JSON response."""
        return self._request('GET', endpoint, params=params)

    def post(self, endpoint: str, data: dict) -> dict:
        """Make a POST request and return JSON response."""
        return self._request('POST', endpoint, json=data)
