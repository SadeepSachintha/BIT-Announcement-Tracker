import logging
import asyncio
from telegram import Update, BotCommand, LinkPreviewOptions
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

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    help_text = (
        "🤖 **Available Commands:**\n\n"
        "/start - Subscribe to announcements\n"
        "/stop - Unsubscribe from announcements\n"
        "/latest - Get the latest announcement\n"
        "/recent - Get the 5 most recent announcements\n"
        "/status - Check bot and scraper status\n"
        "/help - Show this help message"
    )
    await context.bot.send_message(chat_id=chat_id, text=help_text, parse_mode='Markdown')

async def recent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    announcements = database.get_latest_announcements(limit=5)
    if announcements:
        message = "🚨 **Recent Announcements** 🚨\n\n"
        for idx, ann in enumerate(announcements, 1):
            source = ann.get('source', 'Main Site')
            message += f"{idx}. **[{source}]** {ann['title']}\n🔗 [Link]({ann['link']})\n\n"
        await context.bot.send_message(
            chat_id=chat_id, 
            text=message, 
            parse_mode='Markdown', 
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )
    else:
        await context.bot.send_message(chat_id=chat_id, text="No announcements found yet.")

def init_bot(token):
    global BOT_TOKEN, application
    BOT_TOKEN = token
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('stop', stop))
    application.add_handler(CommandHandler('latest', latest))
    application.add_handler(CommandHandler('recent', recent))
    application.add_handler(CommandHandler('status', status))
    application.add_handler(CommandHandler('help', help_cmd))
    
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
    
    # Set bot commands menu
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
