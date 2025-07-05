from typing import List, Dict
from datetime import datetime
from .memory_logger import log_memory_event


def check_memory_consistency(memories: List[Dict], session_id: str = None) -> bool:
    """
    检查短期记忆是否时间顺序合理、内容无重复。
    若发现问题，将记录日志。
    """
    success = True

    # 时间顺序检查
    for i in range(1, len(memories)):
        t1 = datetime.fromisoformat(memories[i - 1]["created_at"])
        t2 = datetime.fromisoformat(memories[i]["created_at"])
        if t1 > t2:
            log_memory_event(
                event="CONSISTENCY_ERROR",
                session_id=session_id,
                detail=f"时间顺序错误：第{i}条记忆时间晚于前一条。"
            )
            success = False

    # 内容重复检查
    seen = set()
    for mem in memories:
        content = mem["content"]
        if content in seen:
            log_memory_event(
                event="CONSISTENCY_ERROR",
                session_id=session_id,
                detail=f"重复内容：'{content[:30]}'"
            )
            success = False
        seen.add(content)

    if success:
        log_memory_event(
            event="CONSISTENCY_OK",
            session_id=session_id,
            detail=f"共检查 {len(memories)} 条记忆，全部通过 ✅"
        )

    return success
