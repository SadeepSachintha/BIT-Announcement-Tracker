import feedparser
import time
import logging
import database
import asyncio

logger = logging.getLogger(__name__)

FEED_URL = "https://www.bit.lk/index.php/feed/"

scraper_running = False

async def fetch_and_notify(broadcast_func):
    logger.info("Fetching RSS feed...")
    try:
        feed = feedparser.parse(FEED_URL)
        if feed.bozo:
            logger.error("Error parsing feed.")
            return

        # Feed entries are usually ordered newest first.
        # We iterate in reverse so the oldest new items are processed first,
        # ensuring chronological notifications if multiple items are new.
        for entry in reversed(feed.entries):
            guid = entry.get('id', entry.get('link'))
            title = entry.get('title')
            link = entry.get('link')
            pub_date = entry.get('published')

            # Try adding to database
            if database.add_announcement(guid, title, link, pub_date):
                logger.info(f"New announcement found: {title}")
                message = f"🚨 **New Announcement** 🚨\n\n**{title}**\n\n📅 Published: {pub_date}\n🔗 Link: {link}"
                await broadcast_func(message)
    except Exception as e:
        logger.error(f"Failed to fetch feed: {e}")

async def run_scraper(broadcast_func, interval=300):
    global scraper_running
    scraper_running = True
    logger.info(f"Scraper started, running every {interval} seconds.")
    try:
        while True:
            await fetch_and_notify(broadcast_func)
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        scraper_running = False
        logger.info("Scraper stopped.")
        pass

def is_running():
    return scraper_running
