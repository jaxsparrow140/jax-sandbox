#!/usr/env python3
"""
Hacker News Top 10 Article Scraper

Scrapes the top 10 article titles from Hacker News using their official JSON API.
Handles errors gracefully with proper exception handling.
"""

import requests
import sys
from typing import List, Optional


HACKER_NEWS_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/topstories.json"
HACKER_NEWS_ITEM_URL = "https://hacker-news.firebaseio.com/item/{}.json"
TOP_N = 10


def fetch_top_story_ids() -> Optional[List[int]]:
    """Fetch the list of top story IDs from Hacker News."""
    try:
        response = requests.get(HACKER_NEWS_TOP_STORIES_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching top stories: {e}")
        return None
    except ValueError as e:
        print(f"Error parsing top stories JSON: {e}")
        return None


def fetch_story_details(story_id: int) -> Optional[dict]:
    """Fetch details for a specific story by ID."""
    try:
        url = f"{HACKER_NEWS_ITEM_URL}"
        response = requests.get(url.format(story_id), timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching story {story_id}: {e}")
        return None
    except ValueError as e:
        print(f"Error parsing story {story_id} JSON: {e}")
        return None


def scrape_hacker_news_top_titles(n: int = TOP_N) -> List[str]:
    """
    Scrapes the top N article titles from Hacker News.
    
    Args:
        n: Number of top articles to fetch (default: 10)
    
    Returns:
        List of article titles
    """
    titles = []
    
    # Fetch top story IDs
    story_ids = fetch_top_story_ids()
    if not story_ids:
        return titles
    
    # Limit to top N
    story_ids = story_ids[:n]
    
    # Fetch each story's title
    for story_id in story_ids:
        story = fetch_story_details(story_id)
        if story and 'title' in story:
            titles.append(story['title'])
        elif story:
            # Story exists but no title (might be deleted or malformed)
            titles.append(f"[No title for story {story_id}]")
    
    return titles


def main():
    """Main function to scrape and print Hacker News top titles."""
    print("📰 Fetching top 10 articles from Hacker News...\n")
    
    titles = scrape_hacker_news_top_titles(TOP_N)
    
    if not titles:
        print("❌ Failed to fetch any articles from Hacker News.")
        sys.exit(1)
    
    print(f"✅ Successfully fetched {len(titles)} articles:\n")
    
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")
    
    print(f"\n🎉 Done! Retrieved {len(titles)} titles.")


if __name__ == "__main__":
    main()
