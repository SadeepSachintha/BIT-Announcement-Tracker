import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

# Load configuration at the very beginning before importing local modules
load_dotenv()

# Ensure the workspace directory is in the import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database
import whatsapp

# Configure Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    # Initialize the database
    database.init_db()
    
    # Fetch the latest 6 announcements
    limit = 6
    logger.info(f"Fetching latest {limit} announcements from database...")
    announcements = database.get_latest_announcements(limit=limit)
    
    if not announcements:
        logger.warning("No announcements found in the database.")
        print("Error: No announcements found in the database.")
        return
        
    # Reverse list so they are sent chronologically (oldest of the 6 first)
    # This keeps the final timeline on WhatsApp in the correct chronological order.
    announcements = list(reversed(announcements))
    
    print(f"\n==================================================")
    print(f"Found {len(announcements)} announcements to push.")
    print(f"==================================================\n")
    
    success_count = 0
    for idx, ann in enumerate(announcements, 1):
        source = ann.get('source', 'Main Site')
        title = ann.get('title')
        pub_date = ann.get('pub_date')
        link = ann.get('link')
        
        # Format identical to the scraper's standard output
        message = f"🚨 **New Announcement [{source}]** 🚨\n\n**{title}**\n\n📅 Published: {pub_date}\n🔗 Link: {link}"
        
        print(f"[{idx}/{len(announcements)}] Broadcasting: \"{title}\"")
        success = await whatsapp.broadcast_message(message)
        if success:
            print(f"  [-] Success")
            success_count += 1
        else:
            print(f"  [-] Failed")
            
        # Standard polite delay between requests to avoid rate limits
        await asyncio.sleep(1.5)
        
    print(f"\n==================================================")
    print(f"Push Finished: {success_count}/{len(announcements)} successfully sent.")
    print(f"==================================================\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
