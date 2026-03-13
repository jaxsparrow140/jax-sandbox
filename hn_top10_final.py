#!/usr/bin/env python3
"""
Hacker News Top 10 Scraper
Uses the official HN Firebase API: https://hacker-news.firebaseio.com/v0/
"""

import sys
import requests

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
TOP_STORIES_URL = f"{HN_API_BASE}/topstories.json"
ITEM_URL = f"{HN_API_BASE}/item/{{item_id}}.json"
TIMEOUT = 10  # seconds


def fetch_top_story_ids(n: int = 10) -> list[int]:
    """Fetch the list of top story IDs from HN."""
    try:
        resp = requests.get(TOP_STORIES_URL, timeout=TIMEOUT)
        resp.raise_for_status()
        story_ids = resp.json()
        if not isinstance(story_ids, list) or not story_ids:
            raise ValueError("Unexpected response format from HN API")
        return story_ids[:n]
    except requests.exceptions.ConnectionError:
        raise SystemExit("Error: Could not connect to Hacker News API. Check your internet connection.")
    except requests.exceptions.Timeout:
        raise SystemExit(f"Error: Request timed out after {TIMEOUT}s.")
    except requests.exceptions.HTTPError as e:
        raise SystemExit(f"Error: HTTP {e.response.status_code} from HN API.")
    except ValueError as e:
        raise SystemExit(f"Error: {e}")


def fetch_story_title(item_id: int) -> str:
    """Fetch the title for a single story by ID. Returns a fallback string on failure."""
    try:
        resp = requests.get(ITEM_URL.format(item_id=item_id), timeout=TIMEOUT)
        resp.raise_for_status()
        item = resp.json()
        if not isinstance(item, dict):
            return f"[Item {item_id}: unexpected format]"
        return item.get("title") or f"[Item {item_id}: no title]"
    except requests.exceptions.RequestException as e:
        return f"[Item {item_id}: fetch failed — {e}]"


def main():
    print("Fetching top 10 Hacker News stories...\n")

    story_ids = fetch_top_story_ids(n=10)

    print("Top 10 Hacker News Articles")
    print("=" * 50)

    for rank, story_id in enumerate(story_ids, start=1):
        title = fetch_story_title(story_id)
        print(f"{rank:>2}. {title}")

    print()


if __name__ == "__main__":
    main()
