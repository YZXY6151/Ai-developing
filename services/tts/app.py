import os
import io
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gtts import gTTS
from fastapi.responses import StreamingResponse, JSONResponse

app = FastAPI()

# -----------------------------------------------------------------------------
# CORS 配置：开发阶段放宽为所有来源，生产请指定精确域名
# -----------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # 开发阶段快速调试，可改回具体地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# 根路由，用于健康检查
# -----------------------------------------------------------------------------
@app.get("/health")
async def health_check():
    return JSONResponse({"status": "ok"})

# -----------------------------------------------------------------------------
# 请求模型
# -----------------------------------------------------------------------------
class TTSRequest(BaseModel):
    text: str
    lang: str = "zh-cn"
    slow: bool = False

# -----------------------------------------------------------------------------
# 异步合成到内存 Buffer
# -----------------------------------------------------------------------------
async def synthesize_to_buffer(text: str, lang: str, slow: bool) -> io.BytesIO:
    loop = asyncio.get_event_loop()
    buf = io.BytesIO()

    def _generate():
        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf

    return await loop.run_in_executor(None, _generate)

# -----------------------------------------------------------------------------
# TTS 合成接口
# -----------------------------------------------------------------------------
@app.post("/api/tts/synthesize")
async def synthesize(req: TTSRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="文本不能为空")
    # 限制最大长度，防止生成过大文件
    if len(text) > 500:
        text = text[:500]

    try:
        buf = await synthesize_to_buffer(text, req.lang, req.slow)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音合成失败：{e}")

    # 流式返回
    def iterfile():
        while True:
            chunk = buf.read(8 * 1024)
            if not chunk:
                break
            yield chunk

    return StreamingResponse(iterfile(), media_type="audio/mpeg")
