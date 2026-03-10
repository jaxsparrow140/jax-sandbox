#!/usr/bin/env python3
"""Scrape the top 10 article titles from Hacker News."""

import sys
import warnings

# Suppress urllib3 NotOpenSSLWarning on macOS system Python — must come before import
warnings.filterwarnings("ignore", message=".*OpenSSL.*")

import requests  # noqa: E402
from concurrent.futures import ThreadPoolExecutor, as_completed  # noqa: E402

HN_TOP_STORIES = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM = "https://hacker-news.firebaseio.com/v0/item/{}.json"
NUM_STORIES = 10
TIMEOUT = 10  # seconds


def fetch_item(sid: int) -> tuple[int, str]:
    """Fetch a single HN item and return (story_id, title)."""
    resp = requests.get(HN_ITEM.format(sid), timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    return sid, data.get("title", "(no title)")


def fetch_top_titles(n: int = NUM_STORIES) -> list[str]:
    """Return the titles of the top *n* HN stories, fetched concurrently."""
    resp = requests.get(HN_TOP_STORIES, timeout=TIMEOUT)
    resp.raise_for_status()
    story_ids = resp.json()[:n]

    # Fetch all items concurrently — much faster than serial requests
    results: dict[int, str] = {}
    with ThreadPoolExecutor(max_workers=n) as pool:
        futures = {pool.submit(fetch_item, sid): sid for sid in story_ids}
        for future in as_completed(futures):
            sid, title = future.result()  # propagates exceptions
            results[sid] = title

    # Preserve original ranking order
    return [results[sid] for sid in story_ids]


def main() -> None:
    try:
        titles = fetch_top_titles()
    except requests.ConnectionError:
        print("Error: could not connect to Hacker News API.", file=sys.stderr)
        sys.exit(1)
    except requests.Timeout:
        print("Error: request timed out.", file=sys.stderr)
        sys.exit(1)
    except requests.HTTPError as exc:
        print(f"Error: HTTP {exc.response.status_code}.", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Top 10 Hacker News articles:\n")
    for i, title in enumerate(titles, 1):
        print(f"  {i:>2}. {title}")


if __name__ == "__main__":
    main()
