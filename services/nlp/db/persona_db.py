# services/nlp/db/persona_db.py

import sqlite3
import os
from datetime import datetime

DB_PATH = os.getenv("SESSION_DB_PATH", os.path.join(os.path.dirname(__file__), "../databases/sessions.db"))




def get_persona_by_id(persona_id: str):
    """
    根据 persona_id 从 persona 表中获取完整人物设定字典。
    """


    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM persona WHERE id = ?", (persona_id,))
    row = cursor.fetchone()
    columns = [desc[0] for desc in cursor.description] if row else []
    conn.close()
    return dict(zip(columns, row)) if row else None

def load_persona_from_db(persona_id: str) -> dict:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, title_display, system_prompt, intro, default_tags,
               core_knowledge_refs, trained_model, editable_fields,
               owner_id, created_at
        FROM persona
        WHERE id = ?
    """, (persona_id,))
    
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise ValueError(f"[加载失败] Persona ID: {persona_id} 不存在于数据库中")

    return {
        "id": row[0],
        "name": row[1],
        "title_display": row[2],
        "system_prompt": row[3],
        "intro": row[4],
        "default_tags": row[5],
        "core_knowledge_refs": row[6],
        "trained_model": row[7],
        "editable_fields": row[8],
        "owner_id": row[9],
        "created_at": row[10],
    }


def init_persona_table_full():
    """
    创建完整的 persona 表（包含所有字段），用于替代旧的 persona_profiles。
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS persona (
            id TEXT PRIMARY KEY,
            name TEXT,
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
    conn.commit()
    conn.close()


def insert_full_default_personas():
    now = datetime.utcnow().isoformat()

    default_personas = [
        {
            "id": "gentle",
            "name": "gentle",
            "title_display": "温柔亲切",
            "system_prompt": "你是一个温柔亲切的AI虚拟主播，用简洁自然的中文与用户互动。",
            "intro": "温柔有礼、贴心亲切的虚拟主播。",
            "default_tags": "温柔,亲切,简洁",
            "core_knowledge_refs": "",
            "trained_model": "yi:9b-chat",
            "editable_fields": "title_display,system_prompt",
            "owner_id": "",
            "created_at": now
        },
        {
            "id": "cool",
            "name": "cool",
            "title_display": "冷静理智",
            "system_prompt": "你是一位冷静沉着的虚拟主播，语气简洁、理性、逻辑清晰。",
            "intro": "冷静理性的虚拟主播，语言简练精准。",
            "default_tags": "冷静,逻辑,简洁",
            "core_knowledge_refs": "",
            "trained_model": "yi:9b-chat",
            "editable_fields": "title_display,system_prompt",
            "owner_id": "",
            "created_at": now
        },
        {
            "id": "energetic",
            "name": "energetic",
            "title_display": "活力满满",
            "system_prompt": "你是一位活力四射的虚拟主播，语气欢快、有趣，喜欢用拟声词。",
            "intro": "充满活力、情绪丰富的主播。",
            "default_tags": "活泼,热情,拟声词",
            "core_knowledge_refs": "",
            "trained_model": "yi:9b-chat",
            "editable_fields": "title_display,system_prompt",
            "owner_id": "",
            "created_at": now
        },
        {
            "id": "tsundere",
            "name": "tsundere",
            "title_display": "傲娇毒舌",
            "system_prompt": "你是一位傲娇毒舌的虚拟主播，讲话嘴硬心软，语气略微挑衅但很在意用户。",
            "intro": "表面毒舌、内心温柔的主播。",
            "default_tags": "傲娇,毒舌,挑衅",
            "core_knowledge_refs": "",
            "trained_model": "yi:9b-chat",
            "editable_fields": "title_display,system_prompt",
            "owner_id": "",
            "created_at": now
        }
    ]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for p in default_personas:
        cursor.execute("""
            INSERT OR IGNORE INTO persona (
                id, name, title_display, system_prompt, intro, default_tags,
                core_knowledge_refs, trained_model, editable_fields,
                owner_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p["id"], p["name"], p["title_display"], p["system_prompt"],
            p["intro"], p["default_tags"], p["core_knowledge_refs"],
            p["trained_model"], p["editable_fields"], p["owner_id"],
            p["created_at"]
        ))
    conn.commit()
    conn.close()