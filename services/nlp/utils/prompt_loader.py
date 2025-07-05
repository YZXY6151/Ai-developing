# services/nlp/utils/prompt_loader.py

import os
import re

def load_prompt_block_from_file(persona_id: str, prompt_path: str = None) -> str:
    """
    从 prompt.txt 中加载指定 persona_id 的 prompt 块
    """
    prompt_path = prompt_path or os.getenv("PROMPT_TEMPLATE_PATH", "prompt.txt")

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read()
        pattern = rf"###\s*==\s*persona:\s*{re.escape(persona_id)}\s*==\n(.*?)(?=\n###\s*==|$)"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else f"[找不到 persona: {persona_id} 的 prompt]"
    except Exception as e:
        return f"[读取 prompt.txt 失败: {e}]"
