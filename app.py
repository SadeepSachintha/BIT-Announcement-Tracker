from flask import Flask, jsonify, render_template
import database
import scraper

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
    status_info = {
        'scraper_running': scraper.is_running(),
        'total_subscribers': database.get_total_subscribers()
    }
    return jsonify(status_info)

# Expose app for running via Gunicorn/Waitress if needed
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
