import os
from datetime import datetime
from typing import Optional

LOG_FILE = os.getenv("MEMORY_LOG_FILE", "memory_debug.log")
ENABLE_LOG = True  # 可通过环境变量或配置文件关闭日志

def _log_prefix():
    return datetime.now().isoformat(timespec='seconds')

def log_memory_event(event: str, detail: str = "", session_id: Optional[str] = None):
    if not ENABLE_LOG:
        return

    prefix = _log_prefix()
    session_info = f"[Session: {session_id}]" if session_id else ""
    message = f"{prefix} | {event} {session_info} {detail}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message)

    # 可选：同时打印
    print(f"🪵 {message.strip()}")
