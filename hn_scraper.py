"""
Scrape the top 10 article titles from Hacker News
"""

import requests
from bs4 import BeautifulSoup
import time

def scrape_hacker_news():
    """Scrape top 10 article titles from Hacker News"""
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
        
        # Find all story links (titles)
        # Hacker News story titles have class 'titleline'
        story_links = soup.find_all('span', class_='titleline')
        
        # Extract top 10 titles
        top_titles = []
        for i, link in enumerate(story_links[:10]):
            title_tag = link.find('a')
            if title_tag:
                title = title_tag.get_text()
                top_titles.append(title)
        
        return top_titles
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Hacker News: {e}")
        return []
    except Exception as e:
        print(f"Error parsing Hacker News: {e}")
        return []

def main():
    """Main function to run the scraper"""
    print("Scraping top 10 articles from Hacker News...")
    titles = scrape_hacker_news()
    
    if titles:
        print("\nTop 10 Hacker News Articles:")
        print("-" * 40)
        for i, title in enumerate(titles, 1):
            print(f"{i}. {title}")
    else:
        print("Failed to retrieve Hacker News articles.")

if __name__ == "__main__":
    main()