import os
import logging
import requests
import asyncio

logger = logging.getLogger(__name__)

# Load configurations from environment variables
ENABLED = os.getenv("WHATSAPP_ENABLED", "false").lower() == "true"
PROVIDER = os.getenv("WHATSAPP_PROVIDER", "generic").lower()
API_URL = os.getenv("WHATSAPP_API_URL", "")
API_KEY = os.getenv("WHATSAPP_API_KEY", "")
CHANNEL_ID = os.getenv("WHATSAPP_CHANNEL_ID", "")

def format_message_for_whatsapp(message: str) -> str:
    """
    Converts Telegram Markdown to WhatsApp formatting.
    Specifically:
    - Replaces Telegram bold '**' with WhatsApp bold '*'
    """
    if not message:
        return ""
    
    # Replace Telegram **bold** with WhatsApp *bold*
    formatted = message.replace("**", "*")
    return formatted

def send_http_request(url: str, json_data: dict, headers: dict, timeout: int = 45) -> requests.Response:
    """
    Synchronous HTTP helper for running inside a thread with configurable timeout.
    """
    return requests.post(url, json=json_data, headers=headers, timeout=timeout)

async def broadcast_message(message: str) -> bool:
    """
    Broadcasts the given announcement message to the configured WhatsApp Channel/Chat.
    Includes a retry mechanism to handle transient WAHA server lag or timeouts.
    """
    if not ENABLED:
        logger.info("WhatsApp broadcasting is disabled.")
        return False
    
    if not API_URL:
        logger.error("WhatsApp broadcast failed: WHATSAPP_API_URL is not set.")
        return False
        
    if not CHANNEL_ID:
        logger.error("WhatsApp broadcast failed: WHATSAPP_CHANNEL_ID is not set.")
        return False

    whatsapp_msg = format_message_for_whatsapp(message)
    
    # Set headers
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
        headers["X-Api-Key"] = API_KEY
    
    # Formulate payload depending on chosen provider
    payload = {}
    if PROVIDER == "waha":
        # WAHA (WhatsApp HTTP API) standard sendText schema
        headers["Content-Type"] = "application/json"
        payload = {
            "chatId": CHANNEL_ID,
            "text": whatsapp_msg,
            "session": os.getenv("WHATSAPP_SESSION", "default")
        }
    elif PROVIDER == "whapi":
        # Whapi.Cloud send text message schema
        headers["Content-Type"] = "application/json"
        payload = {
            "to": CHANNEL_ID,
            "body": whatsapp_msg
        }
    elif PROVIDER == "wassenger":
        # Wassenger send message schema
        headers["Content-Type"] = "application/json"
        payload = {
            "phone": CHANNEL_ID,
            "message": whatsapp_msg
        }
    else:
        # Generic Custom Webhook structure
        headers["Content-Type"] = "application/json"
        payload = {
            "to": CHANNEL_ID,
            "body": whatsapp_msg,
            "text": whatsapp_msg,
            "message": whatsapp_msg
        }
        
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(1, max_retries + 1):
        logger.info(f"Dispatching announcement to WhatsApp Channel/Chat via '{PROVIDER}' (Attempt {attempt}/{max_retries})...")
        try:
            # Execute the HTTP request in a thread pool to avoid blocking the main event loop
            response = await asyncio.to_thread(send_http_request, API_URL, payload, headers, 45)
            
            if response.status_code in [200, 201, 202]:
                logger.info("Announcement successfully broadcasted to WhatsApp!")
                return True
            else:
                logger.error(f"WhatsApp API returned error code {response.status_code} on attempt {attempt}: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to broadcast message on attempt {attempt} due to exception: {e}")
            
        if attempt < max_retries:
            logger.info(f"Waiting {retry_delay} seconds before retrying...")
            await asyncio.sleep(retry_delay)
            
    logger.error("WhatsApp broadcast failed after all retries.")
    return False
