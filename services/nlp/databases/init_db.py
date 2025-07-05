import os
import sqlite3
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent

import os
import sqlite3
from pathlib import Path
from datetime import datetime
import re

BASE_DIR = Path(__file__).resolve().parent
prompt_file = BASE_DIR / "prompt.txt"

def init_persona_db():
    db_path = BASE_DIR / "sessions.db"
    if db_path.exists():
        print(f"✅ 数据库已存在，跳过初始化：{db_path.name}")
        return
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 创建表
    c.execute("""
        CREATE TABLE IF NOT EXISTS persona (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            title_display TEXT,
            system_prompt TEXT,
            intro TEXT,
            default_tags TEXT,
            core_knowledge_refs TEXT,
            trained_model TEXT,
            editable_fields TEXT,
            owner_id TEXT,
            created_at TEXT
        )
    """)
    
    # 检查已存在的 persona
    c.execute("SELECT id FROM persona")
    existing = {row[0] for row in c.fetchall()}

    # 加载 prompt.txt 中的系统 prompt 段
    prompt_map = {}
    if prompt_file.exists():
        content = prompt_file.read_text(encoding="utf-8")

        # 使用正则提取四个 persona 段落
        pattern = r"=== persona:\s*(\w+)[^=]*===\n(.*?)(?=\n### === persona:|\Z)"
        matches = re.findall(pattern, content, re.DOTALL)

        for persona_id, prompt_text in matches:
            prompt_map[persona_id.strip()] = prompt_text.strip()

    # 默认字段模板（除 system_prompt 外）
    now = datetime.now().isoformat(timespec="seconds")
    persona_rows = [
        ("gentle", "gentle", "温柔主播", prompt_map.get("gentle", "你是一个温柔亲切的AI虚拟主播..."),
         "温柔型AI", "友好,体贴", "", "llama3", "none", None, now),
        ("tsundere", "tsundere", "傲娇主播", prompt_map.get("tsundere", "你是一位傲娇毒舌的虚拟主播..."),
         "傲娇型AI", "傲娇,挑衅", "", "llama3", "none", None, now),
        ("cool", "cool", "冷静主播", prompt_map.get("cool", "你是一位冷静沉着的主播..."),
         "冷静型AI", "理性,沉稳", "", "llama3", "none", None, now),
        ("energetic", "energetic", "活力主播", prompt_map.get("energetic", "你是一位活力满满的虚拟主播..."),
         "活泼型AI", "有趣,兴奋", "", "llama3", "none", None, now)
    ]

    # 插入缺失的 persona
    for row in persona_rows:
        if row[0] not in existing:
            c.execute("INSERT INTO persona VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", row)

    conn.commit()
    conn.close()



def init_session_db():
    db_path = BASE_DIR / "session.db"
    if db_path.exists():
        print(f"✅ 数据库已存在，跳过初始化：{db_path.name}")
        return
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS session (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            persona_id TEXT,
            titlename TEXT,
            created_at TEXT,
            last_active_at TEXT,
            status TEXT,
            summary TEXT
        )
    """)
    conn.commit()
    conn.close()

def init_short_term_memory_db():
    db_path = BASE_DIR / "short_term_memory.db"
    if db_path.exists():
        print(f"✅ 数据库已存在，跳过初始化：{db_path.name}")
        return
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS short_term_memory (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            content TEXT,
            created_at TEXT,
            expires_at TEXT,
            important INTEGER,
            user_request_persist INTEGER
        )
    """)
    conn.commit()
    conn.close()

def init_memory_log_db():
    db_path = BASE_DIR / "memory_log.db"
    if db_path.exists():
        print(f"✅ 数据库已存在，跳过初始化：{db_path.name}")
        return
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS memory_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_type TEXT,
            session_id TEXT,
            detail TEXT
        )
    """)
    conn.commit()
    conn.close()

def init_long_term_memory_db():
    db_path = BASE_DIR / "long_term_memory.db"
    if db_path.exists():
        print(f"✅ 数据库已存在，跳过初始化：{db_path.name}")
        return
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS long_term_memory (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            content TEXT,
            created_at TEXT,
            importance INTEGER,
            label TEXT,
            source TEXT
        )
    """)
    conn.commit()
    conn.close()

def run_all():
    print("🛠 初始化所有数据库中...")
    init_persona_db()
    init_session_db()
    init_short_term_memory_db()
    init_memory_log_db()
    init_long_term_memory_db()
    print("✅ 所有数据库初始化完成！")

if __name__ == "__main__":
    run_all()
