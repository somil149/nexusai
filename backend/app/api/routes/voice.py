"""Voice TTS endpoint using edge-tts (free, no API key)."""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import edge_tts, io

router = APIRouter()

VOICES = {
    "en-female": "en-US-JennyNeural",
    "en-male": "en-US-GuyNeural",
    "en-female-2": "en-US-AriaNeural",
}

class TTSRequest(BaseModel):
    text: str
    voice: str = "en-female"

@router.post("/tts")
async def text_to_speech(req: TTSRequest):
    voice = VOICES.get(req.voice, VOICES["en-female"])
    communicate = edge_tts.Communicate(req.text, voice)
    buf = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buf.write(chunk["data"])
    buf.seek(0)
    return StreamingResponse(buf, media_type="audio/mpeg")

@router.get("/tts/voices")
async def list_voices():
    return list(VOICES.keys())
