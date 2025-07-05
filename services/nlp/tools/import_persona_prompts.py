# services/nlp/tools/import_persona_prompts.py
#   未引用

import sqlite3
import re
import os

DB_PATH = os.getenv("SESSION_DB_PATH", os.path.join(os.path.dirname(__file__), "../databases/sessions.db"))
PROMPT_FILE = "prompt.txt"

def parse_personas_from_prompt_file():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    persona_blocks = re.split(r"^###\s*==\s*persona:\s*(\w+)\s*==\s*$", content, flags=re.MULTILINE)

    parsed = []

    for i in range(1, len(persona_blocks), 2):
        persona_id = persona_blocks[i].strip()
        block = persona_blocks[i + 1]
        title_match = re.search(r"title_display:\\s*(.+)", block)
        prompt_match = re.search(r"system_prompt:\\s*\\|\\s*(.+)", block, re.DOTALL)
        title = title_match.group(1).strip() if title_match else "未知"
        prompt = prompt_match.group(1).strip() if prompt_match else ""

        parsed.append({
            "id": persona_id,
            "title_display": title,
            "system_prompt": prompt
        })

    return parsed

def import_personas_to_db(personas):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS persona_profiles (
            id TEXT PRIMARY KEY,
            title_display TEXT,
            system_prompt TEXT
        )
    """)

    for p in personas:
        cursor.execute("""
            INSERT OR REPLACE INTO persona_profiles (id, title_display, system_prompt)
            VALUES (?, ?, ?)
        """, (p["id"], p["title_display"], p["system_prompt"]))

    conn.commit()
    conn.close()
    print(f"✅ 成功导入 {len(personas)} 个 persona 到数据库。")

if __name__ == "__main__":
    personas = parse_personas_from_prompt_file()
    import_personas_to_db(personas)
