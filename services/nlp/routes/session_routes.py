# services/nlp/routes/session_routes.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..db.session_db import create_session

router = APIRouter()

# ───────────── 请求模型 ─────────────
class CreateSessionRequest(BaseModel):
    persona_id: str
    titlename: str = None  # 可选标题名
    user_id: str = "guest"  # 暂时默认使用 "guest"

# ───────────── 响应模型 ─────────────
class CreateSessionResponse(BaseModel):
    session_id: str

# ───────────── 创建 Session 接口 ─────────────
@router.post("/api/nlp/session/create", response_model=CreateSessionResponse)
def create_new_session(req: CreateSessionRequest):
    try:
        session_id = create_session(
            user_id=req.user_id,
            persona_id=req.persona_id,
            titlename=req.titlename
        )
        return {"session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建会话失败：{e}")


@router.post("/api/session/create")
def create_session_api(user_id: str = "demo-user", persona_id: str = "gentle", titlename: str = "临时会话"):
    session_id = create_session(user_id=user_id, persona_id=persona_id, titlename=titlename)
    return {"session_id": session_id}