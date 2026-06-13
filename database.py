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

DATABASE_URL = os.getenv('DATABASE_URL')
IS_POSTGRES = DATABASE_URL is not None and (DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://"))

if IS_POSTGRES:
    import psycopg2
    import psycopg2.extras
    # Supabase / Heroku environment fix
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    logger.info("Database setup: Using PostgreSQL (Supabase)")
else:
    DB_PATH = os.getenv('DATABASE_PATH', 'data/bit_tracker.db')
    DB_DIR = os.path.dirname(DB_PATH) if DB_PATH else None
    logger.info(f"Database setup: Using SQLite path {os.path.abspath(DB_PATH) if DB_PATH else 'None'}")

def get_db():
    if IS_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        if DB_DIR and not os.path.exists(DB_DIR):
            os.makedirs(DB_DIR, exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def get_cursor(conn):
    if IS_POSTGRES:
        return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        return conn.cursor()

def get_placeholder():
    return "%s" if IS_POSTGRES else "?"

def init_db():
    conn = get_db()
    c = get_cursor(conn)
    if IS_POSTGRES:
        # PostgreSQL syntax
        c.execute('''
            CREATE TABLE IF NOT EXISTS announcements (
                id TEXT PRIMARY KEY,
                title TEXT,
                link TEXT,
                pub_date TEXT,
                discovered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                source TEXT DEFAULT 'Main'
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS scraper_status (
                key TEXT PRIMARY KEY,
                last_run TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                status TEXT
            )
        ''')
    else:
        # SQLite syntax
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
        c.execute('''
            CREATE TABLE IF NOT EXISTS scraper_status (
                key TEXT PRIMARY KEY,
                last_run TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT
            )
        ''')
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully.")

def add_announcement(id, title, link, pub_date, source='Main'):
    conn = get_db()
    c = get_cursor(conn)
    p = get_placeholder()
    try:
        c.execute(f'INSERT INTO announcements (id, title, link, pub_date, source) VALUES ({p}, {p}, {p}, {p}, {p})',
                  (id, title, link, pub_date, source))
        conn.commit()
        return True
    except Exception as e:
        err_msg = str(e).lower()
        if "duplicate" in err_msg or "unique" in err_msg or "integrity" in err_msg:
            return False
        logger.error(f"Error adding announcement: {e}")
        return False
    finally:
        conn.close()

def get_latest_announcements(limit=10):
    conn = get_db()
    c = get_cursor(conn)
    p = get_placeholder()
    try:
        query = f'SELECT * FROM announcements ORDER BY discovered_at DESC LIMIT {p}'
        c.execute(query, (limit,))
        rows = c.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to get latest announcements: {e}")
        return []
    finally:
        conn.close()

def get_latest_announcement():
    conn = get_db()
    c = get_cursor(conn)
    try:
        c.execute('SELECT * FROM announcements ORDER BY discovered_at DESC LIMIT 1')
        row = c.fetchone()
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"Failed to get latest announcement: {e}")
        return None
    finally:
        conn.close()

def update_scraper_status(status="Success"):
    conn = get_db()
    c = get_cursor(conn)
    p = get_placeholder()
    now = datetime.now()
    try:
        if IS_POSTGRES:
            c.execute('''
                INSERT INTO scraper_status (key, last_run, status)
                VALUES ('scraper', %s, %s)
                ON CONFLICT (key) DO UPDATE SET last_run = EXCLUDED.last_run, status = EXCLUDED.status
            ''', (now, status))
        else:
            c.execute('''
                INSERT OR REPLACE INTO scraper_status (key, last_run, status)
                VALUES ('scraper', ?, ?)
            ''', (now, status))
        conn.commit()
        logger.info(f"Updated scraper status to: {status}")
    except Exception as e:
        logger.error(f"Failed to update scraper status: {e}")
    finally:
        conn.close()

def get_scraper_status():
    conn = get_db()
    c = get_cursor(conn)
    try:
        c.execute("SELECT last_run, status FROM scraper_status WHERE key = 'scraper'")
        row = c.fetchone()
        if row:
            return dict(row)
        return None
    except Exception as e:
        logger.error(f"Failed to get scraper status: {e}")
        return None
    finally:
        conn.close()
