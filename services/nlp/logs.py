# services/nlp/logs.py

def log_persona_loaded(session_id: str, persona: dict):
    title = persona.get("title_display") or persona.get("name") or "未知"
    print(f"🪵 Persona 加载成功 [Session: {session_id}] => Persona: {title}")
