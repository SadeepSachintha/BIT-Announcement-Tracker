import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, render_template
import database
import scraper
import whatsapp

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/announcements')
def get_announcements():
    announcements = database.get_latest_announcements(limit=20)
    return jsonify(announcements)

@app.route('/api/status')
def get_status():
    try:
        from datetime import datetime, timedelta
        
        # Check database for last scraper execution status
        last_status = database.get_scraper_status()
        scraper_status = False
        last_run_str = "Never"
        
        if last_status:
            last_run = last_status['last_run']
            if isinstance(last_run, str):
                # Handle SQLite string representation of datetime
                try:
                    dt = datetime.strptime(last_run.split('.')[0], "%Y-%m-%d %H:%M:%S")
                except Exception:
                    dt = datetime.now()
            else:
                dt = last_run
            
            # If cron executed within the last 45 minutes, consider it online
            diff = datetime.now() - dt.replace(tzinfo=None)
            if diff < timedelta(minutes=45):
                scraper_status = True
                
            last_run_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            # Fallback to in-memory check (if running locally via python main.py)
            scraper_status = scraper.is_running()
        
        status_info = {
            'scraper_running': scraper_status,
            'last_run': last_run_str,
            'whatsapp_enabled': whatsapp.ENABLED,
            'whatsapp_provider': whatsapp.PROVIDER if whatsapp.ENABLED else None,
            'whatsapp_configured': bool(whatsapp.CHANNEL_ID and whatsapp.API_URL),
            'notifications_paused': os.getenv("PAUSE_NOTIFICATIONS", "false").lower() == "true"
        }
        
        # Log the status for debugging
        app.logger.info(f"Status API called: Scraper={scraper_status}, LastRun={last_run_str}")
        
        return jsonify(status_info)
    except Exception as e:
        app.logger.error(f"Error in status API: {e}")
        return jsonify({'error': str(e)}), 500

# Expose app for running via Gunicorn/Waitress if needed
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
