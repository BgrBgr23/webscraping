import sqlite3
import os
from datetime import datetime, timezone, timedelta
from config import Config

# Türkiye saat dilimi (UTC+3)
TR_TZ = timezone(timedelta(hours=3))

def local_now():
    """Türkiye saatine göre şu anki zamanı döndürür."""
    return datetime.now(TR_TZ).strftime('%Y-%m-%d %H:%M:%S')


def get_db():
    """Veritabanı bağlantısı al."""
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Tüm tabloları oluştur."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            result_count INTEGER DEFAULT 0,
            searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            author TEXT,
            source TEXT NOT NULL,
            price REAL NOT NULL,
            url TEXT,
            image_url TEXT,
            searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            author TEXT,
            min_price REAL,
            source TEXT,
            url TEXT,
            image_url TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            author TEXT,
            target_price REAL NOT NULL,
            current_price REAL,
            source TEXT,
            url TEXT,
            image_url TEXT,
            is_active INTEGER DEFAULT 1,
            is_triggered INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            triggered_at TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


# ── Arama Geçmişi ──────────────────────────────────────────────

def save_search(query, result_count):
    conn = get_db()
    conn.execute('INSERT INTO search_history (query, result_count, searched_at) VALUES (?, ?, ?)',
                 (query, result_count, local_now()))
    conn.commit()
    conn.close()


def get_search_history(limit=50):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM search_history ORDER BY searched_at DESC LIMIT ?', (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def clear_search_history():
    conn = get_db()
    conn.execute('DELETE FROM search_history')
    conn.commit()
    conn.close()


# ── Favoriler ───────────────────────────────────────────────────

def add_favorite(product_name, author, min_price, source, url, image_url):
    conn = get_db()
    existing = conn.execute(
        'SELECT id FROM favorites WHERE product_name = ?', (product_name,)
    ).fetchone()
    if existing:
        conn.close()
        return False
    conn.execute(
        '''INSERT INTO favorites (product_name, author, min_price, source, url, image_url)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (product_name, author, min_price, source, url, image_url)
    )
    conn.commit()
    conn.close()
    return True


def get_favorites():
    conn = get_db()
    rows = conn.execute('SELECT * FROM favorites ORDER BY added_at DESC').fetchall()
    conn.close()
    return [dict(row) for row in rows]


def remove_favorite(fav_id):
    conn = get_db()
    conn.execute('DELETE FROM favorites WHERE id = ?', (fav_id,))
    conn.commit()
    conn.close()


# ── Fiyat Alarmları ─────────────────────────────────────────────

def add_price_alert(product_name, author, target_price, current_price, source, url, image_url=""):
    conn = get_db()
    conn.execute(
        '''INSERT INTO price_alerts
           (product_name, author, target_price, current_price, source, url, image_url, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (product_name, author, target_price, current_price, source, url, image_url, local_now())
    )
    conn.commit()
    conn.close()


def get_price_alerts():
    conn = get_db()
    rows = conn.execute('SELECT * FROM price_alerts ORDER BY created_at DESC').fetchall()
    conn.close()
    return [dict(row) for row in rows]


def remove_price_alert(alert_id):
    conn = get_db()
    conn.execute('DELETE FROM price_alerts WHERE id = ?', (alert_id,))
    conn.commit()
    conn.close()


def update_alert_price(alert_id, current_price):
    conn = get_db()
    alert = conn.execute('SELECT * FROM price_alerts WHERE id = ?', (alert_id,)).fetchone()
    if alert:
        conn.execute('UPDATE price_alerts SET current_price = ? WHERE id = ?',
                     (current_price, alert_id))
        if current_price <= alert['target_price']:
            conn.execute(
                'UPDATE price_alerts SET is_triggered = 1, triggered_at = ? WHERE id = ?',
                (local_now(), alert_id)
            )
    conn.commit()
    conn.close()
