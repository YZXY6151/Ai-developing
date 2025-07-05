import re
from typing import Optional, Dict
from services.nlp.db.session_db import get_session_by_id
from services.nlp.db.persona_db import get_persona_by_id
from services.nlp.utils.memory_logger import log_memory_event
from services.nlp.memory.short_term import query_recent_memories
from services.nlp.db.memory_db import store_short_term_memory
import requests
import os
from datetime import datetime, timezone
from services.nlp.utils.prompt_loader import load_prompt_block_from_file

OLLAMA_URL   = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "yi:9b-chat")


class PersonaManager:
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id
        self.persona: Optional[Dict] = None

        if session_id:
            self.persona = self.get_persona_for_session(session_id)

    def get_persona_for_session(self, session_id: str) -> Optional[Dict]:
        session = get_session_by_id(session_id)
        if not session:
            log_memory_event("PERSONA_ERROR", f"未找到 session: {session_id}")
            return None
        persona_id = session.get("persona_id")
        if not persona_id:
            log_memory_event("PERSONA_ERROR", f"session 未绑定 persona: {session_id}")
            return None
        persona = get_persona_by_id(persona_id)
        if not persona:
            log_memory_event("PERSONA_ERROR", f"未找到 persona: {persona_id}")
            return None
        log_memory_event("LOAD_PERSONA", f"成功加载 persona: {persona.get('name', persona_id)}", session_id)
        log_memory_event("PERSONA_INFO", f"标题: {persona.get('title_display')} | Prompt: {persona.get('system_prompt')}", session_id)
        return persona

    def build_system_prompt(self, persona: Optional[Dict] = None, memory_list: Optional[list] = None) -> str:
        source = persona if persona else self.persona
        if not source:
            return "你是一个AI助手，请用自然、友好的语气与用户交流。"

        persona_id = source.get("id", "")
        system_prompt_text = load_prompt_block_from_file(persona_id)

        memory_snippets = []
        if memory_list:
            for m in memory_list:
                memory_snippets.append(f"- {m['content']}")
        elif self.session_id:
            memories = query_recent_memories(self.session_id, limit=10)
            for m in memories:
                memory_snippets.append(f"- {m['content']}")

        memory_text = "\n".join(memory_snippets)

        final_prompt = f"""{system_prompt_text}

[记忆内容]
{memory_text}

[当前时间]
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        return final_prompt

    def generate_response(self, session_id: str, user_input: str, memory_list=None):
        self.session_id = session_id
        self.persona = self.get_persona_for_session(session_id)
        if not self.persona:
            return "⚠️ 无法加载人格设定", {
                "persona": "unknown",
                "used_memory": False,
                "injection_memory_ids": [],
                "memory_summary": "（无记忆）",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        


        if memory_list is not None:
            recent_list = memory_list
            memory_ids = [m["id"] for m in recent_list if "id" in m]
            recent_text = "\n".join([f"- {m['content']}" for m in recent_list if "content" in m])
        else:
            recent_list = query_recent_memories(session_id, limit=5, with_ids=True)
            memory_ids = [m["id"] for m in recent_list]
            recent_text = "\n".join([f"- {m['content']}" for m in recent_list])


        # ✅ 修改：将 recent_list 传入
        system_prompt = self.build_system_prompt(self.persona, recent_list)

        payload = {
            "model": OLLAMA_MODEL,  # 建议用 "yi:9b-chat"
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt  # 打印调试确保完整
                },
                {
                    "role": "user",
                    "content": f"请用你的主播身份自然回答这个问题：{user_input}"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 300,
            "stream": False
        }


        try:
            response = requests.post(f"{OLLAMA_URL}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            reply = data["message"]["content"]

            store_short_term_memory(session_id, user_input)
            store_short_term_memory(session_id, reply)
            log_memory_event("AUTO_WRITE_MEMORY", "保存用户输入 + AI 回复，重要: True", session_id)

            meta = {
                "persona": self.persona.get("name", "unknown"),
                "used_memory": len(memory_ids) > 0,
                "injection_memory_ids": memory_ids,
                "memory_summary": recent_text or "（无记忆）",
                "timestamp": datetime.utcnow().isoformat()
            }

            return reply, meta

        except Exception as e:
            return f"[错误] 无法连接到 Ollama 模型：{e}", {
                "persona": "unknown",
                "used_memory": False,
                "injection_memory_ids": [],
                "memory_summary": "（无记忆）",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
