import asyncio
import threading
import os
from dotenv import load_dotenv
import database
import bot
import scraper
from app import app
import logging
from werkzeug.serving import make_server

# Load environment variables
load_dotenv()

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

    # Bot Token from .env
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in .env file.")
        return

    # Start Flask app in a separate thread so it doesn't block asyncio loop
    server_thread = ServerThread(app)
    server_thread.start()

    # Initialize Bot
    application = bot.init_bot(BOT_TOKEN)

    # Initialize Bot components
    await application.initialize()
    await application.start()
    
    # Set bot commands menu
    from telegram import BotCommand
    commands = [
        BotCommand("start", "Subscribe to notifications"),
        BotCommand("stop", "Unsubscribe from notifications"),
        BotCommand("latest", "Get the latest announcement"),
        BotCommand("recent", "Get the 5 most recent announcements"),
        BotCommand("status", "Check bot and scraper status"),
        BotCommand("help", "Show available commands")
    ]
    try:
        await application.bot.set_my_commands(commands)
    except Exception as e:
        logger.error(f"Failed to set bot commands: {e}")

    await application.updater.start_polling()

    # Start scraper task
    scraper_task = asyncio.create_task(scraper.run_scraper(bot.broadcast_message, interval=300))

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
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        server_thread.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
