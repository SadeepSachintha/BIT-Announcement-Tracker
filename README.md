# BIT Announcement Tracker 🚀

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Click%20Here-success?style=for-the-badge)](https://SadeepSachintha.github.io/BIT-Announcement-Tracker/)

A premium, comprehensive tracking and notification system designed to monitor announcements from the **Bachelor of Information Technology (BIT)** program at the **University of Colombo School of Computing (UCSC)**. It aggregates updates from multiple portals, stores them securely in a local SQLite database, broadcasts updates to a WhatsApp Channel, and renders all system activities on a real-time web dashboard.

---

## 🌟 Key Features

*   **Multi-Source Aggregation:**
    *   **Main BIT Website:** Monitors the primary RSS feed.
    *   **VLE Portal:** Scrapes the main Virtual Learning Environment site announcements.
    *   **Project VLE Portal:** Tracks project-specific Virtual Learning Environment site announcements.
*   **WhatsApp Broadcasting:**
    *   **WhatsApp Channel Broadcasting:** Integrates with leading WhatsApp API gateways. Automatic layout standardizer to format Markdown into clean, native WhatsApp formatting.
*   **Modern Web Dashboard:**
    *   Responsive UI featuring a tailored HSL dark-mode theme and professional Outfit typography.
    *   Real-time status indicators monitoring the scraper lifecycle, Telegram subscriber metrics, WhatsApp connection, and system-wide broadcast state.
    *   Chronological announcement feed complete with source badges, direct access links, and auto-refreshing capability.
*   **Robust Core Mechanics:**
    *   **Silent Initial Sync:** On startup, the scraper executes a silent run to catalog pre-existing announcements in the SQLite database, preventing a deluge of notification spam on application reboot.
    *   **Async Network Isolation:** Scraping operations and third-party API dispatches run in isolated thread-pools, ensuring Flask and Telegram event loops remain fully responsive.
    *   **Global Notification Pause:** A centralized switch to immediately freeze or resume outgoing notifications without having to shutdown services.
    *   **Data Integrity:** Auto-migration logic and strict duplicate prevention using unique GUID hashing.

---

## 📊 Dashboard Indicators

The interactive dashboard displays live indicators for instantaneous health checks:

| Indicator | Status States | Description |
| :--- | :--- | :--- |
| **Scraper Status** | `Online` \| `Offline` | Tracks if the background periodic parsing thread is actively running. |
| **WhatsApp Channel** | `Online (<PROVIDER>)` \| `Config Error` \| `Disabled` | Details the status and selected gateway API profile for WhatsApp integration. |
| **Broadcast Mode** | `Active 🟢` \| `Paused ⏸️` | Shows whether the global notification switch is allowing pushes or temporarily holding them. |

---


## ⚙️ Environment Configuration

Create a `.env` file in the root directory to define system variables. All options are documented below:

```env
# ==============================================================================
# BIT ANNOUNCEMENT TRACKER CONFIGURATION
# ==============================================================================

# --- Core Configurations ---
DATABASE_PATH=data/bit_tracker.db         # SQLite file path (Optional, defaults to 'data/bit_tracker.db')
PORT=5000                                 # Flask web port (Optional, defaults to 5000)

# --- Global Control Switch ---
# If set to true, blocks outgoing notifications to both Telegram and WhatsApp channels
PAUSE_NOTIFICATIONS=false                 # Options: true, false (Optional, defaults to false)

# --- WhatsApp Broadcast Configuration (Optional) ---
WHATSAPP_ENABLED=true                     # Options: true, false (Optional, defaults to false)
WHATSAPP_PROVIDER=waha                    # Gateway profiles: waha, whapi, wassenger, generic (Defaults to generic)
WHATSAPP_API_URL=http://localhost:3000/api/sendText # Endpoint to dispatch POST requests to
WHATSAPP_API_KEY=your_optional_api_key    # API key or authorization token (Optional)
WHATSAPP_CHANNEL_ID=120363000000000000@newsletter # Target Channel, Chat, Group, or Phone ID
WHATSAPP_SESSION=default                  # Session name parameter (Optional, WAHA-specific, defaults to 'default')
```

---

## 🛠️ Tech Stack

*   **Backend Core:** Python 3.x, Flask
*   **Web Scraping & Parsing:** `feedparser`, `beautifulsoup4`, `requests`
*   **Database:** SQLite3
*   **Frontend UI:** HTML5, CSS3 (Outfit Typography, customized grid alignment, dynamic status badges), Vanilla JavaScript (ES6 Fetch APIs)

---

## 🚀 Installation & Setup

### 1. Repository Setup
```bash
git clone https://github.com/SadeepSachintha/BIT-Announcement-Tracker.git
cd BIT-Announcement-Tracker
```

### 2. Environment Virtualization
```bash
python -m venv venv
# On macOS/Linux:
source venv/bin/activate  
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
```

### 3. Dependencies Installation
```bash
pip install -r requirements.txt
```

### 4. Running the System
To start the unified system (Flask server and background scraper loop):
```bash
python main.py
```
*   **Dashboard URL:** `http://localhost:5000`
*   **Log Feed:** Check console standard output for periodic status summaries.

---

## ☁️ Deployment (Railway)

The tracker is configured for 24/7 hosting on [Railway](https://railway.app/).

1.  **Environment Setup:** In the Railway dashboard under your service settings, add:
    *   `DATABASE_PATH`: `/app/data/bit_tracker.db`
    *   Add any optional WhatsApp configurations as desired.
2.  **Persistent Volumes (CRITICAL):**
    *   Create a Railway Persistent Volume and mount it to `/app/data`.
    *   This ensures that your subscription database persists through service rebuilds and redeployments.
3.  **Database Safety:**
    *   > [!WARNING]
    *   > **Never commit your `bit_tracker.db` file to Git.** It is ignored via `.gitignore` to prevent repository contamination. The application will initialize a fresh database inside the volume upon startup.

---

## 🌐 Live Static Dashboard

A static version of the dashboard is available in the `docs/` folder. To host your own visual tracker, enable GitHub Pages pointing to the `/docs` folder on your main branch.

---

## 📝 License

This project is licensed under the terms of the [MIT License](LICENSE).
