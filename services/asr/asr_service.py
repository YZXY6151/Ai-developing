# # 执行方式：
# #
# # cd "C:\Users\yzxy6\OneDrive\デスクトップ\graduate design\AI-vtuber"
# #
# # python -m pip install --upgrade pip
# # python -m pip install -r requirements.txt
# # source venv/bin/activate
# #
# # uvicorn asr_service:app --host 0.0.0.0 --port 8181 --reload   音频转化成文本服务
# # 该服务使用 OpenAI Whisper 模型进行音频转写

# from fastapi import FastAPI, File, UploadFile, HTTPException
# import whisper
# import os
# import tempfile
# import uuid
# from pydantic import BaseModel

# app = FastAPI(
#     title="ASR Service",
#     description="使用 OpenAI Whisper 模型的语音识别服务",
#     version="1.0.0"
# )

# # 加载 Whisper 模型（可选：small/base/large，根据准确度与速度平衡选择）
# MODEL_NAME = os.getenv("WHISPER_MODEL", "base")
# MODEL = whisper.load_model(MODEL_NAME)

# class RecognizeResponse(BaseModel):
#     transcription: str
#     language: str

# @app.post("/api/asr/recognize", response_model=RecognizeResponse)
# async def recognize_audio(file: UploadFile = File(...)):
#     # 生成唯一的临时文件路径
#     suffix = os.path.splitext(file.filename)[1] or ".webm"
#     temp_dir = tempfile.gettempdir()
#     temp_name = f"{uuid.uuid4().hex}{suffix}"
#     temp_path = os.path.join(temp_dir, temp_name)

#     # 保存上传的音频到临时文件（分块写入）
#     try:
#         with open(temp_path, "wb") as f:
#             while True:
#                 chunk = await file.read(1024 * 64)
#                 if not chunk:
#                     break
#                 f.write(chunk)

#         # 调用 Whisper 模型进行转写
#         try:
#             result = MODEL.transcribe(temp_path)
            
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"ASR 转写失败：{e}")

#         text = result.get("text", "").strip()
#         language = result.get("language", "") or "unknown"

#         return RecognizeResponse(transcription=text, language=language)

#     finally:
#         # 清理临时文件并记录日志
#         try:
#             os.remove(temp_path)
#         except OSError:
#             app.logger.warning(f"无法删除临时文件: {temp_path}")

# services/asr/asr_service.py
# services/asr/asr_service.py
import whisper
import os
import tempfile
import uuid
import subprocess
from fastapi import UploadFile
from typing import Tuple

# ── 1. 只加载一次 Whisper 模型 ──────────────────────────────
MODEL_NAME = os.getenv("WHISPER_MODEL", "base")   # 可用环境变量切换模型
model = whisper.load_model(MODEL_NAME)

# ── 2. 语音识别核心函数 ─────────────────────────────────────
async def recognize_audio(file: UploadFile) -> Tuple[str, str]:
    """
    1) 将上传的 WebM/Opus 保存到临时文件
    2) 用 ffmpeg 转码为 16-kHz mono WAV
    3) 调用 Whisper 识别
    4) 返回 (转写文本, 语言)
    """
    # 保存上传文件到临时路径
    suffix = ".webm"
    webm_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}{suffix}")
    with open(webm_path, "wb") as f:
        while chunk := await file.read(64 * 1024):
            f.write(chunk)

    # 转码到 WAV（16 kHz / mono）
    wav_path = webm_path.replace(".webm", ".wav")
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", webm_path, "-ar", "16000", "-ac", "1", wav_path],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg 转码失败: {e}")

    try:
        # Whisper 识别
        result = model.transcribe(wav_path)
        text = result.get("text", "").strip()
        language = result.get("language", "") or "unknown"
        return text, language
    except Exception as e:
        raise RuntimeError(f"ASR 识别失败: {e}")
    finally:
        # 清理临时文件
        for p in (webm_path, wav_path):
            try:
                os.remove(p)
            except FileNotFoundError:
                pass
