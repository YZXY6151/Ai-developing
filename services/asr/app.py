# services/asr/app.py

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from asr_service import recognize_audio  # 假设这是 async def recognize_audio(file: UploadFile)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/asr/recognize")
async def recognize(file: UploadFile = File(...)):
    try:
        # 直接把 UploadFile 传给 recognize_audio
        text, language = await recognize_audio(file)
        return {"transcription": text, "language": language}

    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
