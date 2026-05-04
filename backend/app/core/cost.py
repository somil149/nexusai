"""Cost tracker - token usage and cost per provider/session."""
from sqlalchemy import select, func
from app.models.database import Message, AsyncSessionLocal
from app.providers.registry import get_cost

async def record_usage(session_id: str, model: str, provider: str,
                        input_tokens: int, output_tokens: int, db):
    cost = get_cost(provider, model, input_tokens, output_tokens)
    # Update last assistant message with token counts
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id, Message.role == "assistant")
        .order_by(Message.created_at.desc())
        .limit(1)
    )
    msg = result.scalar_one_or_none()
    if msg:
        msg.input_tokens = input_tokens
        msg.output_tokens = output_tokens
        msg.cost_usd = cost
        await db.commit()
    return cost

async def get_session_cost(session_id: str, db) -> dict:
    result = await db.execute(
        select(
            func.sum(Message.input_tokens),
            func.sum(Message.output_tokens),
            func.sum(Message.cost_usd),
        ).where(Message.session_id == session_id)
    )
    row = result.one()
    return {"input_tokens": row[0] or 0, "output_tokens": row[1] or 0, "cost_usd": round(row[2] or 0, 6)}

async def get_total_cost(db) -> dict:
    result = await db.execute(
        select(
            Message.provider,
            func.sum(Message.input_tokens),
            func.sum(Message.output_tokens),
            func.sum(Message.cost_usd),
        ).group_by(Message.provider)
    )
    rows = result.all()
    return [{"provider": r[0], "input_tokens": r[1] or 0, "output_tokens": r[2] or 0, "cost_usd": round(r[3] or 0, 6)}
            for r in rows if r[0]]
