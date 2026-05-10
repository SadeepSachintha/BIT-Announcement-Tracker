# BIT Announcement Tracker

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Click%20Here-success?style=for-the-badge)](https://SadeepSachintha.github.io/BIT-Announcement-Tracker/)

A comprehensive tracking system designed to monitor announcements from the Bachelor of Information Technology (BIT) at the University of Colombo School of Computing (UCSC). It tracks multiple sources, stores them in a local SQLite database, alerts subscribed users via a Telegram bot, and provides a modern web dashboard to monitor the system.

## 🌟 Features

- **Multi-Source Tracking:**
  - Main BIT Website RSS Feed (`https://www.bit.lk/index.php/feed/`)
  - VLE Site Announcements (`https://vle.bit.lk/`)
  - Project VLE Site Announcements (`https://project.vle.bit.lk/`)
- **Telegram Bot Integration (`@BITAnnouncementTracker_bot`):**
  - Instant notifications for new announcements.
  - Interactive commands (`/start`, `/stop`, `/latest`, `/recent`, `/status`, `/help`).
- **Premium Web Dashboard:**
  - Real-time status of the background scraper.
  - Live count of active Telegram subscribers.
  - Chronological list of announcements with color-coded source badges.
- **Smart Database:**
  - Uses SQLite to track previously seen announcements to prevent duplicate notifications.

## 🛠️ Tech Stack

- **Backend Logic:** Python 3.x
- **Web Server:** Flask
- **Database:** SQLite3
- **Bot API:** `python-telegram-bot`
- **Web Scraping:** `feedparser`, `beautifulsoup4`, `requests`
- **Frontend Dashboard:** HTML5, CSS3 (Vanilla), JavaScript (Vanilla)

## 📋 Prerequisites

Before running the application, ensure you have the following installed:
- Python 3.8+
- Git

You will also need a **Telegram Bot Token**. You can get one by talking to [@BotFather](https://t.me/botfather) on Telegram and creating a new bot.

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SadeepSachintha/BIT-Announcement-Tracker.git
   cd BIT-Announcement-Tracker
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - **Windows:**
     ```powershell
     .\venv\Scripts\activate
     ```
   - **Mac/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Environment Configuration:**
   Rename `.env.example` to `.env` and add your Telegram bot token:
   ```env
   TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
   ```

## 🎮 Usage

To start the system (which initializes the web server, the telegram bot, and the background scraper concurrently):

```bash
python main.py
```

### Dashboard Access
Once the application is running, open your web browser and navigate to:
[http://localhost:5000](http://localhost:5000)

### Bot Commands
Interact with your bot on Telegram using the following commands:
- `/start` - Subscribe to instant notifications.
- `/stop` - Unsubscribe from notifications.
- `/latest` - Fetch the most recent announcement from the database.
- `/recent` - Get the 5 most recent announcements.
- `/status` - Check the bot's status and total subscriber count.
- `/help` - Show available commands.

## ☁️ Deployment (Railway)

To host the bot 24/7 for free using [Railway](https://railway.app/):

1. **Connect GitHub:** Create a new project on Railway and link it to your GitHub repository.
2. **Environment Variables:** In the **Variables** tab, add:
   - `TELEGRAM_BOT_TOKEN`: Your bot token from @BotFather.
   - `DATABASE_PATH`: `/app/data/bit_tracker.db`
3. **Persistent Storage (Volumes):**
   - Go to **Settings** -> **Volumes** (or search for **Volume** in the **+ New** menu).
   - Mount the volume to the path: `/app/data`. This ensures your subscribers and history are saved even when the bot restarts or redeploys.
4. **Deploy:** Railway will automatically detect the `Procfile` and start the system. You can monitor the progress in the **Logs** tab.

## 🌐 Live Demo (GitHub Pages)

Since GitHub Pages only hosts static files, a static mock version of the dashboard is provided in the `docs/` folder for demonstration purposes. 

**To enable the live demo on your repository:**
1. Go to your repository settings on GitHub.
2. Navigate to **Pages** on the left sidebar.
3. Under **Build and deployment**, set the **Source** to `Deploy from a branch`.
4. Select the `main` branch and choose the `/docs` folder.
5. Click **Save**. Your static demo will be live at `https://SadeepSachintha.github.io/BIT-Announcement-Tracker/` shortly!

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).
