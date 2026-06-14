import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

# Load config
load_dotenv()

# Ensure current dir is in import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import whatsapp

# Configure Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    print("\n==================================================")
    print("      WhatsApp Integration Test Run")
    print("==================================================\n")
    
    # Check variables
    print(f"Provider:      {os.getenv('WHATSAPP_PROVIDER', 'generic')}")
    print(f"API URL:       {os.getenv('WHATSAPP_API_URL', 'Not Set')}")
    print(f"Channel ID:    {os.getenv('WHATSAPP_CHANNEL_ID', 'Not Set')}")
    print("--------------------------------------------------\n")
    
    test_message = (
        "🚨 *Test Announcement [System Test]* 🚨\n\n"
        "*Hello! This is a test run of the BIT Announcement Tracker.* "
        "If you are reading this in your channel, your WhatsApp integration is successfully working!\n\n"
        "📅 Date: 2026-06-14\n"
        "🔗 Link: https://github.com/SadeepSachintha/BIT-Announcement-Tracker"
    )
    
    print("Sending test message...")
    success = await whatsapp.broadcast_message(test_message)
    
    print("\n==================================================")
    if success:
        print("RESULT: SUCCESS! The test message was sent.")
    else:
        print("RESULT: FAILED! Check the error logs above for details.")
    print("==================================================\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest run interrupted by user.")
