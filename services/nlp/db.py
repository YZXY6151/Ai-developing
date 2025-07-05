# services/nlp/db.py
import os
import sqlite3

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "database", "main.db")) # 🔁 修改为你实际数据库路径

def get_session_persona(session_id: str) -> str:
    """
    根据 session_id 查询绑定的 persona_id
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT persona_id FROM sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return row[0]
    else:
        raise ValueError(f"No persona found for session_id: {session_id}")

# def get_persona_prompt(persona_id: str) -> str:
#     """
#     根据 persona_id 查询 system_prompt
#     """
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("SELECT system_prompt FROM persona WHERE id = ?", (persona_id,))
#     row = cursor.fetchone()
#     conn.close()

#     if row:
#         return row[0]
#     else:
#         raise ValueError(f"No system_prompt found for persona_id: {persona_id}")
