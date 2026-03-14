import requests
from bs4 import BeautifulSoup
import time
import json

def scrape_hacker_news():
    '''Scrape the top 10 article titles from Hacker News'''
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
        
        # Find all story links (titles) - using the structure from the fetched content
        titles = []
        
        # Find all elements with class 'titleline' which contains the story links
        for item in soup.select('span.titleline'):
            link = item.find('a')
            if link:
                titles.append(link.get_text())
            if len(titles) >= 10:
                break
        
        # If we didn't find enough titles with the above method, try the old method as fallback
        if len(titles) < 10:
            for item in soup.select('a.storylink')[:10-len(titles)]:
                titles.append(item.get_text())
        
        # Print titles
        print("Top 10 Hacker News Articles:")
        print("=" * 40)
        for i, title in enumerate(titles, 1):
            print(f"{i}. {title}")
        
        # Save to file as well
        with open('hacker_news_titles.json', 'w') as f:
            json.dump(titles, f, indent=2)
        
        return titles
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Hacker News: {e}")
        return []
    except Exception as e:
        print(f"Error parsing Hacker News: {e}")
        return []

if __name__ == "__main__":
    scrape_hacker_news()