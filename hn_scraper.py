#!/usr/bin/env python3
"""Scrape the top 10 article titles from Hacker News."""

import sys
import requests

API_URL = "https://hacker-news.firebaseio.com/v0"
TOP_STORIES = f"{API_URL}/topstories.json"
ITEM_URL = f"{API_URL}/item/{{}}.json"
TIMEOUT = 10  # seconds


def fetch_top_titles(n: int = 10) -> list[str]:
    """Return the top *n* article titles from HN."""
    resp = requests.get(TOP_STORIES, timeout=TIMEOUT)
    resp.raise_for_status()
    story_ids = resp.json()[:n]

    titles: list[str] = []
    for sid in story_ids:
        item_resp = requests.get(ITEM_URL.format(sid), timeout=TIMEOUT)
        item_resp.raise_for_status()
        data = item_resp.json()
        titles.append(data.get("title", "(no title)"))
    return titles


def main() -> None:
    try:
        titles = fetch_top_titles()
    except requests.ConnectionError:
        print("Error: couldn't connect to Hacker News API.", file=sys.stderr)
        sys.exit(1)
    except requests.Timeout:
        print("Error: request timed out.", file=sys.stderr)
        sys.exit(1)
    except requests.HTTPError as exc:
        print(f"Error: HTTP {exc.response.status_code}", file=sys.stderr)
        sys.exit(1)
    except (ValueError, KeyError) as exc:
        print(f"Error: unexpected response format — {exc}", file=sys.stderr)
        sys.exit(1)

    for i, title in enumerate(titles, 1):
        print(f"{i:>2}. {title}")


if __name__ == "__main__":
    main()
