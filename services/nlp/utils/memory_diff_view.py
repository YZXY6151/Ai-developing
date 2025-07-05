from typing import List, Dict, Tuple
from collections import defaultdict
import hashlib

# 生成唯一标识（用于匹配两边数据）
def _generate_hash(mem: Dict) -> str:
    key_fields = [
        mem.get("content", ""),
        mem.get("created_at", ""),
        mem.get("expires_at", ""),
        str(mem.get("important", False)),
        str(mem.get("user_request_persist", False)),
    ]
    return hashlib.sha256("||".join(key_fields).encode("utf-8")).hexdigest()
def compare_memories(a: List[Dict], b: List[Dict]):
    def memory_to_key(mem):
        return mem.get("id")

    def memory_summary(mem):
        return f"{mem.get('content', '')} | 创建: {mem.get('created_at')}"

    a_dict = {memory_to_key(m): m for m in a}
    b_dict = {memory_to_key(m): m for m in b}

    keys = set(a_dict.keys()).union(b_dict.keys())

    for key in sorted(keys):
        mem_a = a_dict.get(key)
        mem_b = b_dict.get(key)

        if mem_a and not mem_b:
            print(f"❌ 记忆已删除：{memory_summary(mem_a)}")
        elif not mem_a and mem_b:
            print(f"➕ 新增记忆：{memory_summary(mem_b)}")
        elif mem_a and mem_b:
            diffs = []
            for field in ["content", "created_at", "expires_at", "important", "user_request_persist"]:
                if mem_a.get(field) != mem_b.get(field):
                    diffs.append(f"{field}: '{mem_a.get(field)}' → '{mem_b.get(field)}'")
            if diffs:
                print(f"✏️ 修改记忆 {key}：")
                for d in diffs:
                    print(f"    - {d}")
