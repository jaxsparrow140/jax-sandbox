#!/usr/bin/env python3
"""Fetch and print the top N Hacker News story titles.

Scrapes the Hacker News homepage HTML and extracts story titles.
Uses only the Python standard library.

Usage:
  python3 hn_top10.py            # prints top 10 titles
  python3 hn_top10.py --count 5

Exit codes:
  0: success
  1: network/http error
  2: parse error / no titles found
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser


HN_URL_DEFAULT = "https://news.ycombinator.com/"


class HNTopParser(HTMLParser):
    """HTML parser that extracts story titles from HN.

    As of HN's current markup, titles are within:
      <span class="titleline"><a ...>Title</a></span>
    """

    def __init__(self, limit: int):
        super().__init__(convert_charrefs=True)
        self.limit = limit
        self.titles: list[str] = []
        self._in_titleline_span = False
        self._capture_a_text = False
        self._title_taken_in_span = False
        self._current_title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if len(self.titles) >= self.limit:
            return

        attrs_dict = dict(attrs)

        if tag == "span" and attrs_dict.get("class") == "titleline":
            self._in_titleline_span = True
            self._title_taken_in_span = False
            return

        # HN sometimes includes additional anchors (e.g., domain links) inside the
        # titleline span; we only want the first <a> (the actual story title).
        if self._in_titleline_span and tag == "a" and not self._title_taken_in_span:
            self._capture_a_text = True
            self._current_title_parts = []

    def handle_endtag(self, tag: str):
        if tag == "span" and self._in_titleline_span:
            self._in_titleline_span = False
            self._capture_a_text = False
            self._title_taken_in_span = False
            self._current_title_parts = []
            return

        if tag == "a" and self._capture_a_text:
            self._capture_a_text = False
            self._title_taken_in_span = True
            title = "".join(self._current_title_parts).strip()
            self._current_title_parts = []
            if title:
                self.titles.append(title)

    def handle_data(self, data: str):
        if len(self.titles) >= self.limit:
            return
        if self._capture_a_text:
            self._current_title_parts.append(data)


def fetch(url: str, timeout_s: float) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "hn-top10/1.0 (+https://news.ycombinator.com/)",
            "Accept": "text/html",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            body = resp.read()
            return body.decode(charset, errors="replace")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP error {e.code}: {e.reason}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e.reason}") from e


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Print top Hacker News story titles.")
    p.add_argument("--count", type=int, default=10, help="Number of titles to print (default: 10)")
    p.add_argument("--url", default=HN_URL_DEFAULT, help=f"HN URL to scrape (default: {HN_URL_DEFAULT})")
    p.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout in seconds (default: 10)")
    args = p.parse_args(argv)

    if args.count <= 0:
        print("--count must be a positive integer", file=sys.stderr)
        return 2

    try:
        html = fetch(args.url, timeout_s=args.timeout)
    except Exception as e:
        print(f"Error fetching {args.url}: {e}", file=sys.stderr)
        return 1

    parser = HNTopParser(limit=args.count)
    try:
        parser.feed(html)
        parser.close()
    except Exception as e:
        print(f"Error parsing HTML: {e}", file=sys.stderr)
        return 2

    if not parser.titles:
        print("No titles found — HN markup may have changed.", file=sys.stderr)
        return 2

    for i, title in enumerate(parser.titles[: args.count], start=1):
        print(f"{i:2d}. {title}")

    if len(parser.titles) < args.count:
        print(
            f"Warning: only found {len(parser.titles)} titles (requested {args.count}).",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
