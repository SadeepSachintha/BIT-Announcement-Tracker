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
        scraper_status = scraper.is_running()
        sub_count = database.get_total_subscribers()
        
        status_info = {
            'scraper_running': scraper_status,
            'total_subscribers': sub_count,
            'whatsapp_enabled': whatsapp.ENABLED,
            'whatsapp_provider': whatsapp.PROVIDER if whatsapp.ENABLED else None,
            'whatsapp_configured': bool(whatsapp.CHANNEL_ID and whatsapp.API_URL)
        }
        
        # Log the status for debugging
        app.logger.info(f"Status API called: Scraper={scraper_status}, Subscribers={sub_count}")
        
        return jsonify(status_info)
    except Exception as e:
        app.logger.error(f"Error in status API: {e}")
        return jsonify({'error': str(e)}), 500

# Expose app for running via Gunicorn/Waitress if needed
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
