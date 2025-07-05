from typing import List, Optional, Dict
from datetime import datetime,timezone
from ..db.memory_db import get_short_term_memories


def inspect_memories(session_id: str, include_expired: bool = False, only_important: bool = False) -> List[Dict]:
    """
    查询并返回某个 session 的短期记忆，用于调试分析。

    :param session_id: Session ID
    :param include_expired: 是否包含已过期的记忆
    :param only_important: 是否仅筛选重要记忆
    :return: 记忆内容列表
    """
    all_memories = get_short_term_memories(session_id)
    result = []

    for mem in all_memories:
        expired = mem["expires_at"] and datetime.fromisoformat(mem["expires_at"]) < datetime.now(timezone.utc)
        if not include_expired and expired:
            continue
        if only_important and not mem["important"]:
            continue
        result.append(mem)

    return result


def format_memory_entry(mem: Dict) -> str:
    """
    格式化单条记忆用于终端打印。
    """
    return (
        f"🧠 内容: {mem['content']}\n"
        f"   ➤ 创建时间: {mem['created_at']}\n"
        f"   ➤ 到期时间: {mem['expires_at'] or 'N/A'}\n"
        f"   ➤ 重要标记: {'✅' if mem['important'] else '❌'}\n"
        f"   ➤ ID: {mem['id']}"
    )


def print_memories(session_id: str, include_expired: bool = False, only_important: bool = False):
    """
    打印某个 session 的记忆信息到终端，用于开发者调试。
    """
    memories = inspect_memories(session_id, include_expired, only_important)
    if not memories:
        print("⚠️ 无匹配的短期记忆。")
        return
    print(f"🔍 共找到 {len(memories)} 条记忆：\n")
    for mem in memories:
        print(format_memory_entry(mem))
        print("-" * 40)
