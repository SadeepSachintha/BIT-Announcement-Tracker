import os
import sqlite3
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Path for the database file - support Railway Volumes
DB_PATH = os.getenv('DATABASE_PATH', 'data/bit_tracker.db')
DB_DIR = os.path.dirname(DB_PATH)
logger.info(f"Database setup: Using path {os.path.abspath(DB_PATH)}")

def get_db():
    if DB_DIR and not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def migrate_legacy_data():
    """
    Safely merges data from the root bit_tracker.db (legacy/repo-tracked) 
    into the active DB_PATH (volume).
    """
    legacy_path = 'bit_tracker.db'
    
    # Check if legacy file exists and is different from current DB
    if os.path.exists(legacy_path) and os.path.abspath(legacy_path) != os.path.abspath(DB_PATH):
        logger.info(f"Migration: Found legacy database at {legacy_path}. Checking for new data to merge...")
        try:
            legacy_conn = sqlite3.connect(legacy_path)
            legacy_conn.row_factory = sqlite3.Row
            current_conn = get_db()
            
            # Migrate subscribers
            c_legacy = legacy_conn.cursor()
            c_legacy.execute("SELECT chat_id, is_active, joined_at FROM subscribers")
            subs = [dict(row) for row in c_legacy.fetchall()]
            
            c_current = current_conn.cursor()
            merged_subs = 0
            for sub in subs:
                c_current.execute(
                    "INSERT OR IGNORE INTO subscribers (chat_id, is_active, joined_at) VALUES (?, ?, ?)",
                    (sub['chat_id'], sub['is_active'], sub['joined_at'])
                )
                if c_current.rowcount > 0:
                    merged_subs += 1
            
            # Migrate announcements
            c_legacy.execute("SELECT id, title, link, pub_date, discovered_at, source FROM announcements")
            anns = [dict(row) for row in c_legacy.fetchall()]
            merged_anns = 0
            for ann in anns:
                c_current.execute(
                    "INSERT OR IGNORE INTO announcements (id, title, link, pub_date, discovered_at, source) VALUES (?, ?, ?, ?, ?, ?)",
                    (ann['id'], ann['title'], ann['link'], ann['pub_date'], ann['discovered_at'], ann['source'])
                )
                if c_current.rowcount > 0:
                    merged_anns += 1
                
            current_conn.commit()
            legacy_conn.close()
            current_conn.close()
            
            if merged_subs > 0 or merged_anns > 0:
                logger.info(f"Migration successful: Merged {merged_subs} subscribers and {merged_anns} announcements.")
            else:
                logger.info("Migration: No new data to merge.")
                
        except Exception as e:
            logger.error(f"Migration failed: {e}")

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
    
    # Run migration if necessary
    migrate_legacy_data()

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
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM subscribers WHERE is_active = 1')
        row = c.fetchone()
        count = row[0] if row else 0
        conn.close()
        logger.info(f"Subscriber count requested: Found {count} active subscribers.")
        return count
    except Exception as e:
        logger.error(f"Error getting subscriber count: {e}")
        return 0
