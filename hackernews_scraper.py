"""
Scrape the top 10 article titles from Hacker News
"""

import requests
from bs4 import BeautifulSoup
import time

def scrape_hackernews_top_titles():
    """
    Scrape the top 10 article titles from Hacker News
    Returns a list of titles or empty list if error occurs
    """
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            # Set headers to avoid being blocked - using a very simple user agent
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; HackerNewsScraper/1.0)'
            }
            
            print(f"Attempt {attempt + 1}: Fetching Hacker News...")
            
            # Fetch the Hacker News homepage
            response = requests.get('https://news.ycombinator.com/', headers=headers, timeout=10)
            
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all title links - these are anchor tags within td elements with class 'title'
            # The actual article titles are the text content of these anchors
            title_links = []
            for td in soup.find_all('td', class_='title'):
                # Find the first anchor tag in the td element
                link = td.find('a')
                if link and link.get_text().strip():
                    # This is likely the title link
                    title_links.append(link)
            
            # We should have exactly 30 title links (10 articles * 3 links each: title, domain, comments)
            # But we only want the first one from each article
            # Take only the first 10
            title_links = title_links[:10]
            
            print(f"Found {len(title_links)} title links")
            
            # Extract top 10 titles
            top_titles = []
            for i, link in enumerate(title_links):
                title_text = link.get_text().strip()
                if title_text:  # Only add non-empty titles
                    top_titles.append(title_text)
            
            return top_titles
            
        except requests.exceptions.RequestException as e:
            print(f"Request error (attempt {attempt + 1}): {type(e).__name__}: {e}")
            if attempt == max_retries - 1:  # Last attempt
                print(f"Error fetching Hacker News after {max_retries} attempts: {e}")
                return []
            else:
                print(f"Attempt {attempt + 1} failed, retrying in 2 seconds...")
                time.sleep(2)
        except Exception as e:
            print(f"Error parsing Hacker News: {type(e).__name__}: {e}")
            return []
    return []

def main():
    """Main function to run the scraper"""
    print("Scraping top 10 articles from Hacker News...")
    titles = scrape_hackernews_top_titles()
    
    if titles:
        print("\nTop 10 Hacker News Articles:")
        print("-" * 40)
        for i, title in enumerate(titles, 1):
            print(f"{i}. {title}")
    else:
        print("Failed to retrieve Hacker News titles.")

if __name__ == "__main__":
    main()