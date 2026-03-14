#!/usr/bin/env python3
"""
Fetch the top 10 article titles from Hacker News using the official API
"""

import requests
import sys

def fetch_hacker_news_top_stories():
    """
    Fetch the top 10 article titles from Hacker News using the official API
    Returns a list of titles or empty list if error occurs
    """
    try:
        # Get top story IDs using the official API
        top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        response = requests.get(top_stories_url, timeout=10)
        response.raise_for_status()
        
        # Get the top 10 story IDs
        top_story_ids = response.json()[:10]
        
        # Fetch details for each story
        top_titles = []
        for story_id in top_story_ids:
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            story_response = requests.get(story_url, timeout=10)
            story_response.raise_for_status()
            story_data = story_response.json()
            
            # Extract title if available
            if story_data and 'title' in story_data:
                top_titles.append(story_data['title'])
        
        return top_titles
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Hacker News data: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error processing Hacker News data: {e}", file=sys.stderr)
        return []

def main():
    """
    Main function to fetch and print top 10 Hacker News titles
    """
    print("Fetching top 10 Hacker News articles...")
    titles = fetch_hacker_news_top_stories()
    
    if not titles:
        print("Could not retrieve any titles.")
        return 1
    
    print(f"\nTop 10 Hacker News Articles:")
    print("=" * 40)
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
