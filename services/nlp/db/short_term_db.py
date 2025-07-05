# services/nlp/db/short_term_db.py
# pip install sqlalchemy

import sqlite3
import os
import uuid
from datetime import datetime, timedelta

DB_PATH = os.getenv("STM_DB_PATH", os.path.join(os.path.dirname(__file__), "../databases/short_term.db"))

def init_stm_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS short_term_memory (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT,
            expires_at TEXT,
            important BOOLEAN DEFAULT 0,
            user_request_persist BOOLEAN DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
