import sqlite3
from datetime import datetime

def get_db():
    conn = sqlite3.connect('ticketbrain.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_no TEXT,
            subject TEXT,
            type TEXT,
            priority TEXT,
            status TEXT,
            module TEXT,
            description TEXT,
            ai_summary TEXT,
            created_at TEXT,
            is_requirement BOOLEAN DEFAULT 0,
            approved BOOLEAN DEFAULT NULL
        )
    ''')
    conn.commit()
    conn.close()