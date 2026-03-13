#!/usr/bin/env python3
"""Scrape the top 10 article titles from Hacker News."""

import sys
import requests

HN_TOP_STORIES = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM = "https://hacker-news.firebaseio.com/v0/item/{}.json"
NUM_STORIES = 10
TIMEOUT = 10  # seconds


def fetch_top_titles(n: int = NUM_STORIES) -> list[str]:
    """Return the titles of the top *n* Hacker News stories."""
    resp = requests.get(HN_TOP_STORIES, timeout=TIMEOUT)
    resp.raise_for_status()
    story_ids = resp.json()[:n]

    titles: list[str] = []
    for sid in story_ids:
        item_resp = requests.get(HN_ITEM.format(sid), timeout=TIMEOUT)
        item_resp.raise_for_status()
        data = item_resp.json()
        titles.append(data.get("title", "(no title)"))
    return titles


def main() -> None:
    try:
        titles = fetch_top_titles()
    except requests.ConnectionError:
        print("Error: Could not connect to Hacker News API.", file=sys.stderr)
        sys.exit(1)
    except requests.Timeout:
        print("Error: Request timed out.", file=sys.stderr)
        sys.exit(1)
    except requests.HTTPError as exc:
        print(f"Error: HTTP {exc.response.status_code} from API.", file=sys.stderr)
        sys.exit(1)
    except (requests.RequestException, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Top 10 Hacker News Articles")
    print("=" * 40)
    for i, title in enumerate(titles, 1):
        print(f"{i:>2}. {title}")


if __name__ == "__main__":
    main()
