from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.database import get_db, Session, Message, Document, AgentConfig
from app.providers.registry import discover_providers
from pydantic import BaseModel
import uuid, shutil
from pathlib import Path
from app.core.config import settings

router = APIRouter()

# ── Models ──────────────────────────────────────────────────────────────────
@router.get("/models")
async def list_models():
    return await discover_providers()

# ── Sessions ─────────────────────────────────────────────────────────────────
@router.get("/sessions")
async def list_sessions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Session).order_by(desc(Session.updated_at)).limit(50))
    return result.scalars().all()

@router.post("/sessions")
async def create_session(db: AsyncSession = Depends(get_db)):
    s = Session(id=str(uuid.uuid4()))
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return s

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    s = await db.get(Session, session_id)
    if not s:
        raise HTTPException(404)
    await db.delete(s)
    await db.commit()
    return {"ok": True}

@router.get("/sessions/{session_id}/messages")
async def get_messages(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Message).where(Message.session_id == session_id).order_by(Message.created_at))
    return result.scalars().all()

# ── Documents ─────────────────────────────────────────────────────────────────
@router.post("/documents/upload")
async def upload_document(session_id: str = "", file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    from app.rag.pipeline import ingest_document
    dest = Path(settings.upload_dir) / file.filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    chunks = await ingest_document(str(dest), session_id)
    doc = Document(filename=file.filename, session_id=session_id, chunk_count=chunks)
    db.add(doc)
    await db.commit()
    return {"filename": file.filename, "chunks": chunks}

# ── Agent configs ─────────────────────────────────────────────────────────────
@router.get("/agent-configs")
async def list_agent_configs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgentConfig).order_by(desc(AgentConfig.created_at)))
    return result.scalars().all()

class AgentConfigCreate(BaseModel):
    name: str
    description: str = ""
    agents: list[dict]

@router.post("/agent-configs")
async def create_agent_config(body: AgentConfigCreate, db: AsyncSession = Depends(get_db)):
    cfg = AgentConfig(name=body.name, description=body.description, agents=body.agents)
    db.add(cfg)
    await db.commit()
    await db.refresh(cfg)
    return cfg

# ── Cost ──────────────────────────────────────────────────────────────────────
@router.get("/cost")
async def total_cost(db: AsyncSession = Depends(get_db)):
    from app.core.cost import get_total_cost
    return await get_total_cost(db)

@router.get("/cost/{session_id}")
async def session_cost(session_id: str, db: AsyncSession = Depends(get_db)):
    from app.core.cost import get_session_cost
    return await get_session_cost(session_id, db)
