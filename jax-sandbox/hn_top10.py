#!/usr/bin/env python3
"""Scrape the top 10 article titles from Hacker News."""

import sys
import requests
from bs4 import BeautifulSoup

URL = "https://news.ycombinator.com/"
TIMEOUT = 10


def fetch_top_titles(n: int = 10) -> list[str]:
    """Return the first *n* story titles from the HN front page."""
    resp = requests.get(URL, timeout=TIMEOUT)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    title_links = soup.select(".titleline > a")

    if not title_links:
        raise RuntimeError("No titles found — HN page structure may have changed.")

    return [link.get_text(strip=True) for link in title_links[:n]]


def main() -> None:
    try:
        titles = fetch_top_titles()
    except requests.ConnectionError:
        print("Error: Could not connect to Hacker News. Check your network.", file=sys.stderr)
        sys.exit(1)
    except requests.Timeout:
        print("Error: Request to Hacker News timed out.", file=sys.stderr)
        sys.exit(1)
    except requests.HTTPError as exc:
        print(f"Error: HTTP {exc.response.status_code} from Hacker News.", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Top 10 Hacker News articles:\n")
    for i, title in enumerate(titles, 1):
        print(f"  {i:>2}. {title}")


if __name__ == "__main__":
    main()
