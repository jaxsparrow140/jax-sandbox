#!/usr/bin/env python3
"""
Scrape the top 10 article titles from Hacker News
"""

import requests
from bs4 import BeautifulSoup
import sys

def scrape_hn_top_articles():
    """Scrape top 10 article titles from Hacker News"""
    try:
        # Fetch the Hacker News homepage
        url = "https://news.ycombinator.com/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all story links (class 'titleline')
        story_links = soup.find_all('span', class_='titleline')
        
        # Extract top 10 titles
        top_titles = []
        for link in story_links[:10]:
            title_tag = link.find('a')
            if title_tag:
                top_titles.append(title_tag.get_text())
        
        # Print the titles
        print("Top 10 Hacker News Articles:")
        print("=" * 40)
        for i, title in enumerate(top_titles, 1):
            print(f"{i}. {title}")
        
        return top_titles
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Hacker News: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error parsing Hacker News: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    titles = scrape_hn_top_articles()
    if not titles:
        sys.exit(1)
    
    # Exit with success code
    sys.exit(0)