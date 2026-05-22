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

# The exact GUIDs (URLs) corresponding to the 6 announcements listed in your last screenshot
# Ordered from oldest to newest:
WEBSITE_GUIDS = [
    "https://www.bit.lk/?p=4233",  # IMPORTANT NOTICE - EXTENDED (May 08)
    "https://www.bit.lk/?p=4238",  # BIT External Degree Certificate Collection - 2024 (May 12)
    "https://www.bit.lk/?p=4246",  # HDIT Certificate Collection - 2024 (May 20)
    "https://www.bit.lk/?p=4249",  # Results Released (May 21)
    "https://www.bit.lk/?p=4251",  # APPLICABLE TO STUDENTS WHOSE EXAMINATION RESULTS HAVE BEEN WITHHELD (May 22)
    "https://www.bit.lk/?p=4255"   # IMPORTANT NOTICE - FURTHER EXTENDED (May 22)
]

async def main():
    # Initialize database
    database.init_db()
    
    print("\n==================================================")
    print("Fetching website announcements from database...")
    print("==================================================\n")
    
    # Query database and find the matching rows
    conn = database.get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM announcements")
    all_rows = [dict(row) for row in c.fetchall()]
    conn.close()
    
    # Order them according to WEBSITE_GUIDS (chronological order)
    matched_announcements = []
    for guid in WEBSITE_GUIDS:
        for row in all_rows:
            if row['id'] == guid:
                matched_announcements.append(row)
                break
                
    if len(matched_announcements) < len(WEBSITE_GUIDS):
        print(f"Warning: Only found {len(matched_announcements)} out of {len(WEBSITE_GUIDS)} targeted announcements in the database.")
        
    if not matched_announcements:
        print("Error: No matching announcements found.")
        return
        
    print(f"Found {len(matched_announcements)} announcements to push.")
    print("--------------------------------------------------\n")
    
    success_count = 0
    for idx, ann in enumerate(matched_announcements, 1):
        source = ann.get('source', 'Main Site')
        title = ann.get('title')
        pub_date = ann.get('pub_date')
        link = ann.get('link')
        
        # Standard format
        message = f"🚨 **New Announcement [{source}]** 🚨\n\n**{title}**\n\n📅 Published: {pub_date}\n🔗 Link: {link}"
        
        print(f"[{idx}/{len(matched_announcements)}] Broadcasting: \"{title}\"")
        success = await whatsapp.broadcast_message(message)
        if success:
            print("  [-] Success")
            success_count += 1
        else:
            print("  [-] Failed")
            
        # Standard delay to respect rate limits
        await asyncio.sleep(1.5)
        
    print(f"\n==================================================")
    print(f"Push Finished: {success_count}/{len(matched_announcements)} successfully sent.")
    print(f"==================================================\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
