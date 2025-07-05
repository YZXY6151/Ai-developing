import sqlite3
import os
from datetime import datetime

# 使用环境变量控制数据库路径，默认 fallback 到当前目录下
CHAT_HISTORY_DB_PATH = os.getenv("CHAT_HISTORY_DB_PATH", "services/nlp/databases/chat_history.db")

def init_chat_history_db():
    conn = sqlite3.connect(CHAT_HISTORY_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            sender TEXT CHECK(sender IN ('user', 'ai')) NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def insert_chat_message(session_id: str, sender: str, content: str):
    conn = sqlite3.connect(CHAT_HISTORY_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_history (id, session_id, sender, content, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        f"{session_id}-{sender}-{datetime.utcnow().timestamp()}",
        session_id,
        sender,
        content,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()


def get_chat_history(session_id: str, limit: int = 50):
    conn = sqlite3.connect(CHAT_HISTORY_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender, content, created_at
        FROM chat_history
        WHERE session_id = ?
        ORDER BY created_at ASC
        LIMIT ?
    """, (session_id, limit))
    rows = cursor.fetchall()
    conn.close()

    # 格式化为列表字典形式，方便 API 返回
    history = []
    for sender, content, created_at in rows:
        history.append({
            "sender": sender,
            "content": content,
            "created_at": created_at
        })
    return history

def query_chat_history(session_id: str, limit: int = 50) -> list[dict]:
    conn = sqlite3.connect(CHAT_HISTORY_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender, content, created_at
        FROM chat_history
        WHERE session_id = ?
        ORDER BY created_at ASC
        LIMIT ?
    """, (session_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [
        { "sender": row[0], "content": row[1], "created_at": row[2] }
        for row in rows
    ]
