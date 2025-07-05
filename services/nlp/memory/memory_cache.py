from collections import OrderedDict
from typing import Dict, List
from threading import Lock
from ..db.memory_db import get_short_term_memories

# 单条记忆数据结构示意（建议与 DB 查询字段保持一致）
MemoryEntry = Dict  # e.g., {'id': '...', 'content': '...', 'created_at': ..., 'important': ...}

class ShortTermMemoryCache:
    def __init__(self, max_per_session: int = 20):
        self.cache: Dict[str, OrderedDict[str, MemoryEntry]] = {}
        self.max_per_session = max_per_session
        self.lock = Lock()

    def put(self, session_id: str, memory: MemoryEntry):
        with self.lock:
            if session_id not in self.cache:
                self.cache[session_id] = OrderedDict()

            session_cache = self.cache[session_id]
            memory_id = memory["id"]

            # 如果已存在则删除（更新位置）
            if memory_id in session_cache:
                del session_cache[memory_id]

            # 插入最新条目
            session_cache[memory_id] = memory

            # 如果超出上限，移除最旧
            if len(session_cache) > self.max_per_session:
                session_cache.popitem(last=False)  # FIFO淘汰

    def add(self, session_id: str, memory: MemoryEntry):
        """兼容接口别名，等价于 put()"""
        self.put(session_id, memory)

    def get_all(self, session_id: str) -> List[MemoryEntry]:
        with self.lock:
            return list(self.cache.get(session_id, {}).values())

    def get(self, session_id: str) -> List[MemoryEntry]:
        """兼容别名接口"""
        return self.get_all(session_id)

    def get_recent(self, session_id: str, n: int = 5) -> List[MemoryEntry]:
        with self.lock:
            return list(self.cache.get(session_id, {}).values())[-n:]

    def clear_session(self, session_id: str):
        with self.lock:
            if session_id in self.cache:
                del self.cache[session_id]

    def clear_all(self):
        with self.lock:
            self.cache.clear()

    def get_or_reload(self, session_id: str, reload_if_empty: bool = True, limit: int = 10) -> List[MemoryEntry]:
            with self.lock:
                cached = self.cache.get(session_id)
                if cached and len(cached) > 0:
                    return list(cached.values())

            if reload_if_empty:
                # 从数据库中加载
                memories = get_short_term_memories(session_id)[-limit:]
                with self.lock:
                    if session_id not in self.cache:
                        self.cache[session_id] = OrderedDict()
                    for mem in memories:
                        self.cache[session_id][mem["id"]] = mem
                return memories
            else:
                return []