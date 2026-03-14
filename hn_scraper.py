#!/usr/bin/env python3
"""
Scrape the top 10 article titles from Hacker News
"""

import requests
from bs4 import BeautifulSoup
import sys

def scrape_hn_top_articles():
    """Fetch and parse top 10 Hacker News articles"""
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
        
        # Find all story links
        # Based on web_fetch output, article titles are the <a> tags with href starting with "item?id="
        # that have text that is not "comments", "vote", "ago", or numbers
        story_links = []
        
        # Find all links with href starting with "item?id="
        for link in soup.find_all('a', href=True):
            if link['href'].startswith('item?id='):
                text = link.get_text().strip()
                
                # Filter out non-title links
                # Exclude links that are just numbers, "comments", "vote", "ago", "points"
                if text and len(text) > 3 and not text.isdigit() and \
                   'comments' not in text and 'vote' not in text and \
                   'ago' not in text and 'points' not in text and \
                   'discuss' not in text and 'new' not in text and \
                   '1 comment' not in text and '2 comments' not in text and \
                   '3 comments' not in text and '4 comments' not in text and \
                   '5 comments' not in text and '6 comments' not in text and \
                   '7 comments' not in text and '8 comments' not in text and \
                   '9 comments' not in text and '10 comments' not in text:
                    story_links.append(link)
                    
                    # Stop when we have 10 titles
                    if len(story_links) >= 10:
                        break
        
        # Get the top 10 articles
        top_articles = story_links[:10]
        
        # Print titles
        print("Top 10 Hacker News Articles:")
        print("=" * 40)
        for i, link in enumerate(top_articles, 1):
            title = link.get_text().strip()
            url = "https://news.ycombinator.com/" + link['href']
            print(f"{i}. {title}")
            print(f"   {url}")
            print()
        
        return len(top_articles)
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Hacker News: {e}", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"Error parsing Hacker News: {e}", file=sys.stderr)
        return 0

if __name__ == "__main__":
    count = scrape_hn_top_articles()
    if count == 0:
        sys.exit(1)
    else:
        print(f"Successfully scraped {count} articles.")
        sys.exit(0)