import os
import sqlite3
from datetime import datetime

# Path for the database file - support Railway Volumes
DB_PATH = os.getenv('DATABASE_PATH', 'data/bit_tracker.db')
DB_DIR = os.path.dirname(DB_PATH)

def get_db():
    if DB_DIR and not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    # Announcements table
    c.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id TEXT PRIMARY KEY,
            title TEXT,
            link TEXT,
            pub_date TEXT,
            discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source TEXT DEFAULT 'Main'
        )
    ''')
    
    # Check if 'source' column exists (for backward compatibility with existing DB)
    c.execute("PRAGMA table_info(announcements)")
    columns = [column['name'] for column in c.fetchall()]
    if 'source' not in columns:
        c.execute("ALTER TABLE announcements ADD COLUMN source TEXT DEFAULT 'Main'")
        
    # Subscribers table
    c.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            chat_id TEXT PRIMARY KEY,
            is_active INTEGER DEFAULT 1,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_announcement(id, title, link, pub_date, source='Main'):
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO announcements (id, title, link, pub_date, source) VALUES (?, ?, ?, ?, ?)',
                  (id, title, link, pub_date, source))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_latest_announcements(limit=10):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM announcements ORDER BY discovered_at DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_latest_announcement():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM announcements ORDER BY discovered_at DESC LIMIT 1')
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def add_subscriber(chat_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO subscribers (chat_id, is_active) VALUES (?, 1)', (str(chat_id),))
    conn.commit()
    conn.close()

def remove_subscriber(chat_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE subscribers SET is_active = 0 WHERE chat_id = ?', (str(chat_id),))
    conn.commit()
    conn.close()

def get_active_subscribers():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT chat_id FROM subscribers WHERE is_active = 1')
    rows = c.fetchall()
    conn.close()
    return [row['chat_id'] for row in rows]

def get_total_subscribers():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) as count FROM subscribers WHERE is_active = 1')
    row = c.fetchone()
    conn.close()
    return row['count']
