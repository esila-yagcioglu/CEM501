import sqlite3
import os
import time
from dotenv import load_dotenv

load_dotenv(override=True)

DB_PATH = os.path.join(os.path.dirname(__file__), "memory.db")


def init_db():
    """Create database tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            role TEXT,
            company TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS message_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_email TEXT,
            direction TEXT CHECK(direction IN ('sent', 'received')),
            subject TEXT,
            body TEXT,
            category TEXT,
            channel TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS scheduled_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            due_at TIMESTAMP NOT NULL,
            contact_email TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized.")


def log_message(contact_email, direction, subject, body, category, channel="email"):
    """Log a sent or received message."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        INSERT INTO message_history (contact_email, direction, subject, body, category, channel)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (contact_email, direction, subject, body, category, channel))

    conn.commit()
    conn.close()


def get_history(contact_email, limit=5):
    """Get recent message history for a contact."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        SELECT direction, subject, category, sent_at
        FROM message_history
        WHERE contact_email = ?
        ORDER BY sent_at DESC
        LIMIT ?
    ''', (contact_email, limit))

    rows = c.fetchall()
    conn.close()
    return rows


def get_all_history(limit=20):
    """Get all recent messages."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        SELECT contact_email, direction, subject, category, channel, sent_at
        FROM message_history
        ORDER BY sent_at DESC
        LIMIT ?
    ''', (limit,))

    rows = c.fetchall()
    conn.close()
    return rows


def print_history():
    """Print all message history."""
    rows = get_all_history()

    if not rows:
        print("No message history found.")
        return

    print("\n" + "=" * 80)
    print("MESSAGE HISTORY")
    print("=" * 80)

    for row in rows:
        email, direction, subject, category, channel, sent_at = row
        arrow = "→" if direction == "sent" else "←"
        print(f"{sent_at} | {arrow} | [{category}] | {channel} | {email}")
        print(f"  Subject: {subject}")
        print("-" * 80)


if __name__ == "__main__":
    init_db()
    print_history()