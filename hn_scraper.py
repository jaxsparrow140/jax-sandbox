#!/usr/bin/env python3
"""
Scrape the top 10 article titles from Hacker News
"""

import requests
from bs4 import BeautifulSoup
import sys

def scrape_hacker_news():
    """Fetch and parse Hacker News top stories"""
    try:
        # Send request to Hacker News
        url = "https://news.ycombinator.com/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all story titles (class 'titleline')
        titles = soup.select('span.titleline a')
        
        # Extract top 10 titles
        top_titles = []
        for i, title in enumerate(titles[:10]):
            top_titles.append(title.get_text())
        
        return top_titles
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Hacker News: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error parsing Hacker News: {e}", file=sys.stderr)
        return []

def main():
    """Main function"""
    print("Fetching top 10 Hacker News stories...")
    titles = scrape_hacker_news()
    
    if not titles:
        print("Failed to retrieve any titles.")
        sys.exit(1)
    
    print("\nTop 10 Hacker News Stories:")
    print("=" * 40)
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")

if __name__ == "__main__":
    main()