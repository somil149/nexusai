"""WebSocket endpoint for streaming chat with tools and RAG."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db, Session, Message
from app.providers.client import stream_chat
from app.tools.executor import execute_tool, TOOLS_SCHEMA
from app.rag.pipeline import search_documents, build_rag_context
from app.agents.engine import run_crew
import json, uuid
from datetime import datetime

router = APIRouter()

@router.websocket("/ws/chat/{session_id}")
async def chat_ws(session_id: str, websocket: WebSocket):
    await websocket.accept()
    from app.models.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        try:
            while True:
                data = await websocket.receive_json()
                provider = data.get("provider", "openai")
                model = data.get("model", "gpt-4o-mini")
                user_msg = data.get("message", "")
                use_tools = data.get("use_tools", True)
                use_rag = data.get("use_rag", False)
                rag_session = data.get("rag_session", "")

                # Save user message
                msg = Message(id=str(uuid.uuid4()), session_id=session_id,
                              role="user", content=user_msg, model=model, provider=provider)
                db.add(msg)

                # Update session
                sess = await db.get(Session, session_id)
                if sess:
                    if sess.title == "New Chat" and user_msg:
                        sess.title = user_msg[:50]
                    sess.model = model
                    sess.provider = provider
                    sess.updated_at = datetime.utcnow()
                await db.commit()

                # Build messages history
                from sqlalchemy import select
                result = await db.execute(
                    select(Message).where(Message.session_id == session_id,
                                          Message.role.in_(["user", "assistant"]))
                    .order_by(Message.created_at).limit(20)
                )
                history = result.scalars().all()
                messages = [{"role": m.role, "content": m.content} for m in history]

                # RAG context injection
                if use_rag and user_msg:
                    rag_results = await search_documents(user_msg, rag_session)
                    if rag_results:
                        ctx = build_rag_context(rag_results)
                        messages[-1]["content"] = ctx + messages[-1]["content"]

                # Stream response
                full_response = ""
                tools = TOOLS_SCHEMA if use_tools else None

                async for chunk in stream_chat(provider, model, messages, tools):
                    full_response += chunk
                    await websocket.send_json({"type": "chunk", "content": chunk})

                # Save assistant message
                asst_msg = Message(id=str(uuid.uuid4()), session_id=session_id,
                                   role="assistant", content=full_response,
                                   model=model, provider=provider)
                db.add(asst_msg)
                await db.commit()

                await websocket.send_json({"type": "done", "session_id": session_id})

        except WebSocketDisconnect:
            pass
        except Exception as e:
            await websocket.send_json({"type": "error", "content": str(e)})

@router.websocket("/ws/crew/{session_id}")
async def crew_ws(session_id: str, websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        agents = data.get("agents", [])
        task = data.get("task", "")
        async for chunk in run_crew(agents, task):
            await websocket.send_json({"type": "chunk", "content": chunk})
        await websocket.send_json({"type": "done"})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"type": "error", "content": str(e)})
