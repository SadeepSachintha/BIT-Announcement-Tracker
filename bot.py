import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import database

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)
BOT_TOKEN = None
application = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    database.add_subscriber(chat_id)
    await context.bot.send_message(chat_id=chat_id, text="Welcome to the BIT Announcement Tracker! You are now subscribed to get the latest updates.")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    database.remove_subscriber(chat_id)
    await context.bot.send_message(chat_id=chat_id, text="You have been unsubscribed from notifications. Send /start to subscribe again.")

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    announcement = database.get_latest_announcement()
    if announcement:
        source = announcement.get('source', 'Main Site')
        message = f"🚨 **Latest Announcement [{source}]** 🚨\n\n**{announcement['title']}**\n\n📅 Published: {announcement['pub_date']}\n🔗 Link: {announcement['link']}"
        await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=chat_id, text="No announcements found yet.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    import scraper
    scraper_status = "Online 🟢" if scraper.is_running() else "Offline 🔴"
    subs_count = database.get_total_subscribers()
    await context.bot.send_message(chat_id=chat_id, text=f"🤖 Bot Status: Online 🟢\n🕸️ Scraper: {scraper_status}\n👥 Active Subscribers: {subs_count}")

def init_bot(token):
    global BOT_TOKEN, application
    BOT_TOKEN = token
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('stop', stop))
    application.add_handler(CommandHandler('latest', latest))
    application.add_handler(CommandHandler('status', status))
    
    return application

async def broadcast_message(message: str):
    if not application:
        logger.error("Bot application not initialized.")
        return
    
    subscribers = database.get_active_subscribers()
    for chat_id in subscribers:
        try:
            await application.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")

async def run_bot_polling(application):
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    # Keep the task running
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
