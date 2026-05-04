from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.database import init_db
from app.api.routes.api import router as api_router
from app.api.routes.chat import router as chat_router
from app.api.routes.voice import router as voice_router

app = FastAPI(title="NexusAI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
app.include_router(chat_router)
app.include_router(voice_router, prefix="/api")

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/")
async def root():
    return {"status": "NexusAI running", "docs": "/docs"}
