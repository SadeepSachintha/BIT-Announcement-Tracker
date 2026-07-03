import os
import sys
import asyncio
import logging
import requests
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
    logger.info("Initializing heartbeat check...")
    
    # Check session status
    api_url = os.getenv("WHATSAPP_API_URL", "")
    api_key = os.getenv("WHATSAPP_API_KEY", "")
    target = os.getenv("WHATSAPP_HEARTBEAT_TARGET", "")
    
    if not api_url or not target:
        logger.error("Heartbeat failed: WHATSAPP_API_URL or WHATSAPP_HEARTBEAT_TARGET not configured.")
        return
        
    base_url = api_url.rsplit("/api/", 1)[0]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-Api-Key": api_key
    }
    
    status = "UNKNOWN"
    try:
        r = requests.get(f"{base_url}/api/sessions/default", headers=headers, timeout=15)
        if r.status_code == 200:
            status = r.json().get("status", "UNKNOWN")
        else:
            logger.error(f"Failed to fetch session status. HTTP {r.status_code}: {r.text}")
    except Exception as e:
        logger.error(f"Error connecting to WAHA server: {e}")
        
    if status == "WORKING":
        logger.info("WhatsApp session is WORKING. Sending heartbeat message...")
        msg = "🟢 *BIT Tracker Heartbeat* 🟢\n\n*WhatsApp connection is healthy and active.*\n\n🤖 *Host:* Oracle VM"
        success = await whatsapp.send_message(target, msg)
        if success:
            logger.info("Heartbeat message successfully sent.")
        else:
            logger.error("Failed to send heartbeat message.")
    else:
        logger.error(f"Heartbeat check failed: WhatsApp session status is '{status}' (Expected 'WORKING').")

if __name__ == "__main__":
    asyncio.run(main())
