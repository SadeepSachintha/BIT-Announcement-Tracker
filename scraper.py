import feedparser
import time
import logging
import database
import asyncio
import requests
from bs4 import BeautifulSoup
from datetime import datetime

logger = logging.getLogger(__name__)

FEED_URL = "https://www.bit.lk/index.php/feed/"
VLE_URL = "https://vle.bit.lk/"
PROJECT_VLE_URL = "https://project.vle.bit.lk/"

scraper_running = False

def fetch_rss_feed():
    try:
        feed = feedparser.parse(FEED_URL)
        if feed.bozo:
            logger.error("Error parsing feed.")
            return []
        
        results = []
        for entry in feed.entries:
            results.append({
                'guid': entry.get('id', entry.get('link')),
                'title': entry.get('title'),
                'link': entry.get('link'),
                'pub_date': entry.get('published', datetime.now().strftime("%Y-%m-%d")),
                'source': 'Main Site'
            })
        return list(reversed(results))
    except Exception as e:
        logger.error(f"Failed to fetch RSS feed: {e}")
        return []

def fetch_vle_page(url, source_name):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Moodle site news usually has h3 headers with the discussion links
        # Looking at the scraped HTML, we see <h3> followed by the title
        announcements = []
        h3_tags = soup.find_all('h3')
        
        for h3 in h3_tags:
            title = h3.get_text(strip=True)
            # Find the permalink
            # Usually it's in a link nearby, or the h3 itself might contain an anchor
            # Let's search for the first link after the h3 that has 'discuss.php'
            next_link = h3.find_next('a', href=True)
            while next_link and 'forum/discuss.php' not in next_link['href']:
                next_link = next_link.find_next('a', href=True)
                
            link = next_link['href'] if next_link else url
            guid = link # Use link as unique ID
            pub_date = datetime.now().strftime("%Y-%m-%d") # Hard to parse exact date from front page easily
            
            announcements.append({
                'guid': guid,
                'title': title,
                'link': link,
                'pub_date': pub_date,
                'source': source_name
            })
        return list(reversed(announcements))
    except Exception as e:
        logger.error(f"Failed to fetch {source_name}: {e}")
        return []

async def fetch_all_sources(broadcast_func):
    logger.info("Fetching from all sources...")
    
    # Run synchronous HTTP requests in threads to not block asyncio loop
    all_announcements = []
    
    rss_items = await asyncio.to_thread(fetch_rss_feed)
    all_announcements.extend(rss_items)
    
    vle_items = await asyncio.to_thread(fetch_vle_page, VLE_URL, 'VLE')
    all_announcements.extend(vle_items)
    
    project_vle_items = await asyncio.to_thread(fetch_vle_page, PROJECT_VLE_URL, 'Project VLE')
    all_announcements.extend(project_vle_items)
    
    for item in all_announcements:
        if database.add_announcement(item['guid'], item['title'], item['link'], item['pub_date'], item['source']):
            logger.info(f"New announcement found from {item['source']}: {item['title']}")
            message = f"🚨 **New Announcement [{item['source']}]** 🚨\n\n**{item['title']}**\n\n📅 Published: {item['pub_date']}\n🔗 Link: {item['link']}"
            await broadcast_func(message)

async def run_scraper(broadcast_func, interval=300):
    global scraper_running
    scraper_running = True
    logger.info(f"Scraper started, running every {interval} seconds.")
    try:
        while True:
            await fetch_all_sources(broadcast_func)
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        scraper_running = False
        logger.info("Scraper stopped.")
        pass

def is_running():
    return scraper_running
