"""对话接口。"""
import json
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import StreamingResponse
from app.core.deps import get_db, get_current_user
from app.core.security import generate_sse_ticket
from app.services.chat_service import ChatService

router = APIRouter()


class ChatRequest(BaseModel):
    customer_id: str
    source: str = "web"
    query: str = ""


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    role: str
    content: str
    msg_type: str
    created_at: str


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: str
    source: str
    status: int
    last_msg_at: str | None


@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    req: ChatRequest,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    svc = ChatService(session)
    sess = await svc.create_session(req.customer_id, req.source)
    return SessionResponse.model_validate(sess)


@router.get("/sessions/{session_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    session_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    svc = ChatService(session)
    msgs = await svc.get_session_messages(session_id, skip, limit)
    return [MessageResponse.model_validate(m) for m in msgs]


@router.post("/stream-ticket")
async def create_stream_ticket(
    session_id: int,
    user=Depends(get_current_user),
):
    import redis.asyncio as aioredis
    from app.core.config import settings
    ticket = generate_sse_ticket()
    r = aioredis.from_url(settings.redis.url)
    await r.setex(
        f"sse:ticket:{ticket}",
        settings.security.sse_ticket_ttl_seconds,
        json.dumps({"user_id": user.id, "session_id": session_id}),
    )
    await r.close()
    return {"ticket": ticket}


@router.post("/sessions/{session_id}/transfer")
async def transfer_to_human(
    session_id: int,
    reason: str = Query("用户请求转人工"),
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    svc = ChatService(session)
    await svc.transfer_to_human(session_id, reason)
    return {"message": "已转接人工客服"}