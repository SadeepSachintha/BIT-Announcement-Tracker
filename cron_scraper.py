import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

# Load config
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("cron_scraper")

# Ensure the root directory is in the import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database
import scraper
import whatsapp

async def main():
    logger.info("Starting cron scraper execution...")
    
    # Initialize DB
    database.init_db()
    
    # Define broadcast helper to send announcements to WhatsApp
    async def broadcast_announcement(message):
        if os.getenv("PAUSE_NOTIFICATIONS", "false").lower() == "true":
            logger.info("Broadcasting is currently PAUSED via PAUSE_NOTIFICATIONS.")
            return
        await whatsapp.broadcast_message(message)

    try:
        # Fetch and process announcements from all sources (Main site, VLE, Project VLE)
        await scraper.fetch_all_sources(broadcast_announcement)
        
        # Log successful run to database
        database.update_scraper_status("Success")
        logger.info("Cron scraper execution completed successfully.")
    except Exception as e:
        logger.error(f"Cron scraper failed: {e}")
        try:
            database.update_scraper_status(f"Failed: {e}")
        except Exception as db_err:
            logger.error(f"Failed to write failure status to DB: {db_err}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
