import os
from typing import Optional
from datetime import datetime
from services.nlp.db.memory_db import get_short_term_memories
from services.nlp.utils.memory_logger import log_memory_event

def simulate_session_replay(session_id: str, verbose: bool = True):
    """
    模拟重播某个 session 的记忆轨迹。
    可用于开发阶段调试记忆记录是否合理。
    """
    memories = get_short_term_memories(session_id)
    memories = sorted(memories, key=lambda m: m["created_at"])  # 时间升序排序

    print(f"\n📼 正在回放 Session: {session_id}\n")

    if not memories:
        print("⚠️ 无记忆可回放。")
        log_memory_event("PLAYBACK_EMPTY", session_id=session_id, detail="该 session 无记录")
        return

    for mem in memories:
        created = mem["created_at"]
        content = mem["content"]
        is_important = mem.get("important", False)

        tag = "📌" if is_important else "🧠"
        print(f"🕒 [{created}] {tag} {content}")

    print(f"\n✅ 共 {len(memories)} 条记忆已回放\n")
    log_memory_event("PLAYBACK_OK", session_id=session_id, detail=f"成功回放 {len(memories)} 条记忆")
