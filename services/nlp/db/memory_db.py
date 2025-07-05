import sqlite3
import uuid
from datetime import datetime, timedelta,timezone
import os

# 数据库路径（可通过环境变量覆盖）
DB_PATH = os.getenv("STM_DB_PATH", os.path.join(os.path.dirname(__file__), "../databases/short_term_memory.db"))

# ───────────── 初始化数据库 ─────────────
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


# ───────────── 写入短期记忆 ─────────────
def add_short_term_memory(session_id: str, content: str, expires_minutes: int = 60):
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=expires_minutes)
    memory_id = str(uuid.uuid4())

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO short_term_memory (id, session_id, content, created_at, expires_at)
        VALUES (?, ?, ?, ?, ?)
    """, (memory_id, session_id, content, now.isoformat(), expires_at.isoformat()))
    conn.commit()
    conn.close()


# ───────────── 查询某 Session 的所有记忆（默认只取未过期）─────────────
def get_recent_memory(session_id: str) -> list:
    now = datetime.now(timezone.utc).isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT content FROM short_term_memory
        WHERE session_id = ? AND expires_at > ?
        ORDER BY created_at ASC
    """, (session_id, now))
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]


def delete_expired_memory(session_id: str = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    now = datetime.now(timezone.utc).isoformat()
    
    if session_id:
        c.execute("""
            DELETE FROM short_term_memory
            WHERE session_id = ? AND expires_at IS NOT NULL AND expires_at <= ?
        """, (session_id, now))
    else:
        c.execute("""
            DELETE FROM short_term_memory
            WHERE expires_at IS NOT NULL AND expires_at <= ?
        """, (now,))

    deleted_count = c.rowcount
    conn.commit()
    conn.close()
    return deleted_count


def store_short_term_memory(session_id: str, content: str, expires_at: str = None, important: bool = False, user_request_persist: bool = False):
    from ..utils.memory_logger import log_memory_event

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    memory_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    c.execute("""
        INSERT INTO short_term_memory (id, session_id, content, created_at, expires_at, important, user_request_persist)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (memory_id, session_id, content, created_at, expires_at, important, user_request_persist))
    conn.commit()
    conn.close()

    # 日志记录
    log_memory_event(
        "WRITE_MEMORY",
        f"写入内容: {content}",
        session_id=session_id
    )

    return memory_id


def get_short_term_memories(session_id: str) -> list:
    from ..utils.memory_logger import log_memory_event

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, content, created_at, expires_at, important
        FROM short_term_memory
        WHERE session_id = ?
        ORDER BY created_at DESC
    """, (session_id,))
    rows = c.fetchall()
    conn.close()

    results = [
        {
            "id": row[0],
            "content": row[1],
            "created_at": row[2],
            "expires_at": row[3],
            "important": bool(row[4])
        } for row in rows
    ]

    # 日志记录
    log_memory_event(
        "QUERY_MEMORY",
        f"共查询到 {len(results)} 条记忆",
        session_id=session_id
    )

    return results

def delete_all_memory(session_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM short_term_memory WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()
