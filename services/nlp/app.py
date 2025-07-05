from fastapi import FastAPI,Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from datetime import datetime, timezone
from .db.chat_history_db import insert_chat_message

from .persona_manager import PersonaManager
from .memory.short_term import query_recent_memories
from .utils.memory_logger import log_memory_event

# ───────────── FastAPI 设置 ─────────────
from contextlib import asynccontextmanager
from .db.session_db import init_db, create_session_if_not_exists


from .db.chat_history_db import init_chat_history_db,get_chat_history,query_chat_history

init_chat_history_db()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ✅ 应用启动前执行的逻辑
    init_db()
    create_session_if_not_exists(
        session_id="session-gentle-1",
        persona_id="gentle",
        titlename="默认温柔AI",
        user_id="guest"
    )
    yield  # ⛔ 应用关闭逻辑可留空

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ───────────── 请求模型（非 session 模式） ─────────────
class ChatRequest(BaseModel):
    message: str
    persona: str = "gentle"  # 保留字段但不使用

# ───────────── 请求模型（session 模式） ─────────────
class SessionChatRequest(BaseModel):
    session_id: str
    user_input: str

class ChatMessagePayload(BaseModel):
    session_id: str
    sender: str  # "user" or "ai"
    content: str

# ───────────── 模型配置 ─────────────
OLLAMA_URL   = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "yi:9b-chat")

class HistoryRequest(BaseModel):
    session_id: str
    limit: int = 50


# ───────────── 简化版接口（不带 session）─────────────
@app.post("/api/nlp/chat")
async def chat_with_llama(req: ChatRequest):
    user_input = req.message.strip()
    system_prompt = "你是一个AI助手，请自然、友好地与用户互动。"

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        "stream": False
    }

    try:
        response = requests.post(f"{OLLAMA_URL}/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        return { "reply": data["message"]["content"] }
    except Exception as e:
        return { "reply": f"[错误] 无法连接到 Ollama 模型：{e}" }

# ───────────── 带 Session 模式的正式接口 ─────────────
@app.post("/api/nlp/chat_with_session")
def chat_with_session(req: SessionChatRequest):
    try:
        session_id = req.session_id
        user_input = req.user_input.strip()

        # 限制注入最近 5 条短期记忆
        recent_memories = query_recent_memories(session_id=session_id, limit=10, with_ids=True)


        manager = PersonaManager(session_id)
        reply, meta = manager.generate_response(
            session_id=session_id,
            user_input=user_input,
            memory_list=recent_memories  # 明确传入限定后的记忆
        )

        return { "reply": reply, "meta": meta }

    except Exception as e:
        return {
            "reply": f"[错误] 无法生成回复：{e}",
            "meta": {
                "persona": "unknown",
                "used_memory": False,
                "injection_memory_ids": [],
                "memory_summary": "（无记忆）",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }

@app.post("/api/nlp/chat/history")
def fetch_chat_history(req: HistoryRequest):
    try:
        history = get_chat_history(session_id=req.session_id, limit=req.limit)
        return { "history": history }
    except Exception as e:
        return {
            "history": [],
            "error": str(e)
        }

@app.post("/api/nlp/chat/save_message")
def save_chat_message(req: dict):
    try:
        session_id = req.get("session_id")
        sender = req.get("sender")
        content = req.get("content")
        if not session_id or not sender or not content:
            return { "status": "error", "reason": "missing fields" }
        insert_chat_message(session_id, sender, content)
        return { "status": "ok" }
    except Exception as e:
        return { "status": "error", "reason": str(e) }


# ───────────── 路由挂载 ─────────────
from .routes import session_routes
app.include_router(session_routes.router)




@app.get("/api/nlp/chat/history")
def get_chat_history(session_id: str = Query(...)):
    try:
        history = query_chat_history(session_id=session_id)
        return { "history": history }
    except Exception as e:
        return { "history": [], "error": str(e) }

@app.post("/api/nlp/chat/save_message")
async def save_message(payload: ChatMessagePayload):
    try:
        insert_chat_message(payload.session_id, payload.sender, payload.content)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}