import os
from dotenv import load_dotenv
# Load environment variables first
load_dotenv()

import asyncio
import threading
import database
import scraper
import whatsapp
from app import app
import logging
from werkzeug.serving import make_server

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ServerThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        port = int(os.getenv('PORT', 5000))
        self.server = make_server('0.0.0.0', port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        logger.info("Starting Flask Server on http://0.0.0.0:5000")
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

async def main():
    # Initialize DB
    database.init_db()

    # Start Flask app in a separate thread so it doesn't block asyncio loop
    server_thread = ServerThread(app)
    server_thread.start()

    # Broadcast callback to send announcements to WhatsApp
    async def broadcast_announcement(message):
        if os.getenv("PAUSE_NOTIFICATIONS", "false").lower() == "true":
            logger.info("Broadcasting is currently PAUSED via PAUSE_NOTIFICATIONS env variable.")
            return
        # Broadcast to WhatsApp channel (if enabled)
        await whatsapp.broadcast_message(message)

    # Start scraper task
    scraper_task = asyncio.create_task(scraper.run_scraper(broadcast_announcement, interval=300))

    logger.info("System is running. Press Ctrl+C to stop.")

    try:
        # Keep the main coroutine running
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received.")
    finally:
        logger.info("Shutting down...")
        scraper_task.cancel()
        server_thread.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
