import json
import csv
import os
from typing import List, Dict
from datetime import datetime


# 模拟数据库调用（替换为实际 get_short_term_memories）
def get_short_term_memories(session_id: str) -> List[Dict]:
    return [
        {"content": "今天吃了拉面", "created_at": datetime.utcnow().isoformat(), "important": True},
        {"content": "天气不错", "created_at": datetime.utcnow().isoformat(), "important": False},
        {"content": "", "created_at": datetime.utcnow().isoformat(), "important": True},
        {"content": "准备学习 AI 开发", "created_at": datetime.utcnow().isoformat(), "important": True},
        {"content": "GPT 是大语言模型", "created_at": datetime.utcnow().isoformat(), "important": False},
    ]


def export_training_samples_to_file(
    session_id: str,
    format: str = "jsonl",
    path: str = "training_data.jsonl",
    only_important: bool = False,
    exclude_empty: bool = True
):
    memories = get_short_term_memories(session_id)

    # 过滤
    filtered = []
    for mem in memories:
        content = mem["content"].strip()
        if exclude_empty and not content:
            continue
        if only_important and not mem.get("important", False):
            continue
        filtered.append({
            "input": content,
            "response": "",
            "timestamp": mem["created_at"]
        })

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    if format == "jsonl":
        with open(path, "w", encoding="utf-8") as f:
            for item in filtered:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    elif format == "csv":
        with open(path, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["input", "response", "timestamp"])
            writer.writeheader()
            writer.writerows(filtered)

    elif format == "txt":
        with open(path, "w", encoding="utf-8") as f:
            for item in filtered:
                f.write(f"### 用户：\n{item['input']}\n\n### AI：\n{item['response']}\n\n")

    else:
        raise ValueError("不支持的格式类型: " + format)

    return path
