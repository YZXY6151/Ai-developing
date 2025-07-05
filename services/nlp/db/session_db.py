# services/nlp/db/session_db.py

import sqlite3
import uuid
import os
from datetime import datetime,timezone

# 默认数据库路径
DB_PATH = os.getenv("SESSION_DB_PATH", os.path.join(os.path.dirname(__file__), "../databases/sessions.db"))

# ───────────── 初始化数据库 ─────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            persona_id TEXT NOT NULL,
            titlename TEXT,
            created_at TEXT,
            last_active_at TEXT,
            status TEXT DEFAULT 'active'
        )
    """)
    conn.commit()
    conn.close()

# ───────────── 新建 Session ─────────────
def create_session(user_id: str, persona_id: str, titlename: str = None) -> str:
    print("🔍 写入 session 的数据库路径:", DB_PATH)

    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO sessions (id, user_id, persona_id, titlename, created_at, last_active_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (session_id, user_id, persona_id, titlename, now, now))
    conn.commit()
    conn.close()
    return session_id

# ───────────── 查询 persona_id ─────────────
def get_session_persona(session_id: str) -> str:
    """
    根据 session_id 获取对应的 persona_id（如 gentle, cool 等）。
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT persona_id FROM sessions WHERE id = ?", (session_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

# ───────────── 可选：查询会话是否存在 ─────────────
def session_exists(session_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM sessions WHERE id = ?", (session_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

def get_session_by_id(session_id: str):
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    columns = [desc[0] for desc in cursor.description] if row else []
    conn.close()

    if row:
        return dict(zip(columns, row))
    else:
        return None

def create_session_if_not_exists(session_id: str, persona_id: str, titlename: str = "默认会话", user_id: str = "guest"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM sessions WHERE id = ?", (session_id,))
    if cursor.fetchone():
        conn.close()
        return  # 已存在则直接返回

    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO sessions (id, user_id, persona_id, titlename, created_at, last_active_at, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session_id, user_id, persona_id, titlename, now, now, "active"))

    conn.commit()
    conn.close()