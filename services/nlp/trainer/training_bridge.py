# services/nlp/trainer/training_bridge.py

import json
from typing import List, Dict, Optional
from services.nlp.db.memory_db import get_short_term_memories
from services.nlp.utils.memory_logger import log_memory_event

def extract_training_samples(
    session_id: str,
    only_important: bool = False,
    exclude_empty: bool = True,
    as_json: bool = False
) -> List[Dict] | str:
    """
    提取某个 session 的短期记忆数据，生成可用于训练的样本。
    """

    raw_memories = get_short_term_memories(session_id)

    samples = []
    for mem in raw_memories:
        content = mem.get("content", "").strip()
        important = mem.get("important", False)

        if exclude_empty and not content:
            continue
        if only_important and not important:
            continue

        samples.append({
            "input": content,
            "response": "",  # 暂无记录 AI 回复，可后续接入响应记录系统
            "timestamp": mem.get("created_at", "")
        })

    log_memory_event(
        event="EXPORT_TRAINING_SAMPLES",
        session_id=session_id,
        detail=f"导出训练样本 {len(samples)} 条（重要: {only_important}，排除空: {exclude_empty}）"
    )

    if as_json:
        return json.dumps(samples, ensure_ascii=False, indent=2)
    else:
        return samples
