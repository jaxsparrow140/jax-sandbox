#!/usr/bin/env python3

"""
Scrape top 10 Hacker News article titles.
Handles network errors, parsing failures, and empty responses gracefully.
"""

import requests
from bs4 import BeautifulSoup
import sys

def scrape_hn_top_titles():
    url = "https://news.ycombinator.com"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Hacker News: {e}", file=sys.stderr)
        return []

    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Hacker News uses a different structure for top stories
        # Titles are in <a class="storylink"> tags within <tr class="athing"> elements
        title_links = soup.select('tr.athing .title .storylink')
        if not title_links:
            print("No article titles found on page.", file=sys.stderr)
            return []
        
        # Extract top 10 titles
        top_titles = [link.text.strip() for link in title_links[:10]]
        return top_titles
    except Exception as e:
        print(f"Error parsing HTML: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    titles = scrape_hn_top_titles()
    if titles:
        for i, title in enumerate(titles, 1):
            print(f"{i}. {title}")
    else:
        print("No titles to display.")
        sys.exit(1)