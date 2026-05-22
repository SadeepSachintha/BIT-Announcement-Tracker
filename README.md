# BIT Announcement Tracker

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Click%20Here-success?style=for-the-badge)](https://SadeepSachintha.github.io/BIT-Announcement-Tracker/)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue?style=for-the-badge&logo=telegram)](https://t.me/BITAnnouncementTracker_bot)

A comprehensive tracking system designed to monitor announcements from the Bachelor of Information Technology (BIT) at the University of Colombo School of Computing (UCSC). It tracks multiple sources, stores them in a local SQLite database, alerts subscribed users via a Telegram bot, and provides a modern web dashboard to monitor the system.

## 🌟 Features

- **Multi-Source Tracking:**
  - Main BIT Website RSS Feed
  - VLE Site Announcements
  - Project VLE Site Announcements
- **Telegram Bot Integration:**
  - Instant notifications for new announcements.
  - Interactive commands (`/start`, `/stop`, `/latest`, `/recent`, `/status`, `/help`).
- **WhatsApp Channel Integration:**
  - Push announcements directly to a WhatsApp Channel, Group, or Chat.
  - Automated formatting conversion (Telegram Markdown to clean WhatsApp-compliant layout).
  - Out-of-the-box support for popular gateways (WAHA, Whapi.cloud, Wassenger, or custom).
- **Premium Web Dashboard:**
  - Real-time status of the background scraper.
  - Live status tracking of both Telegram subscribers and WhatsApp channel broadcast integration.
  - Chronological list of announcements with color-coded source badges.
- **Smart Data Management:**
  - Automatic duplicate detection.
  - Built-in migration logic to recover data from legacy deployments.

## 🛠️ Tech Stack

- **Backend:** Python 3.x (Flask, `python-telegram-bot`)
- **Scraping:** `feedparser`, `beautifulsoup4`
- **Database:** SQLite3
- **Frontend:** Vanilla HTML5, CSS3 (Outfit Font), JavaScript

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SadeepSachintha/BIT-Announcement-Tracker.git
   cd BIT-Announcement-Tracker
   ```

2. **Setup Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure API Keys:**
   Create a `.env` file and set the Telegram bot token and optional WhatsApp variables:
   ```env
   TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
   
   # Optional WhatsApp Channel configuration
   WHATSAPP_ENABLED=true
   WHATSAPP_PROVIDER=waha                  # Options: waha, whapi, wassenger, generic
   WHATSAPP_API_URL=http://localhost:3000/api/sendText
   WHATSAPP_API_KEY=your_optional_api_key
   WHATSAPP_CHANNEL_ID=120363000000000000@newsletter
   ```

## 🎮 Usage

To start the system (Flask server, Telegram bot, and scraper):
```bash
python main.py
```

- **Dashboard:** `http://localhost:5000`
- **Bot Commands:** `/start`, `/latest`, `/status`, etc.

## ☁️ Deployment (Railway)

To host the bot 24/7 using [Railway](https://railway.app/):

1. **Environment Variables:** In Railway, add:
   - `TELEGRAM_BOT_TOKEN`: Your bot token.
   - `DATABASE_PATH`: `/app/data/bit_tracker.db`
2. **Persistent Storage (Volumes):**
   - **IMPORTANT:** Create a Volume and mount it to `/app/data`.
   - This ensures your subscribers are not lost when the bot redeploys.
3. **Database Persistence:**
   - > [!WARNING]
   - > **Do NOT commit your `bit_tracker.db` file to Git.** It should be ignored via `.gitignore`. The bot will automatically create a fresh one in the volume or migrate existing data if configured.

## 🌐 Live Demo (GitHub Pages)

A static version of the dashboard is available in the `docs/` folder. To enable it, set your GitHub Pages source to the `/docs` folder on the `main` branch.

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).
