"""对话应用服务。"""
from __future__ import annotations
from datetime import datetime
from typing import AsyncIterator, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import ChatSession, ChatMessage, ChatRetrievalLog
from app.repositories.chat_repo import SessionRepository, MessageRepository, RetrievalLogRepository


class ChatService:
    """对话会话/消息管理。"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.session_repo = SessionRepository(session)
        self.msg_repo = MessageRepository(session)
        self.retrieval_repo = RetrievalLogRepository(session)

    async def create_session(self, customer_id: str, source: str = "web") -> ChatSession:
        session = ChatSession(customer_id=customer_id, source=source, status=1)
        return await self.session_repo.add(session)

    async def send_message(self, session_id: int, role: str, content: str, msg_type: str = "text", **kwargs) -> ChatMessage:
        msg = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            msg_type=msg_type,
            **kwargs,
        )
        await self.msg_repo.add(msg)
        # 更新会话最后消息时间
        sess = await self.session_repo.get_by_id(session_id)
        if sess:
            sess.last_msg_at = datetime.utcnow()
            await self.session.flush()
        return msg

    async def log_retrieval(self, message_id: int, query: str, topk_scores: list[dict], threshold: float, hit_count: int, rerank_used: bool = False, latency_ms: int = 0) -> ChatRetrievalLog:
        import json
        log = ChatRetrievalLog(
            message_id=message_id,
            query=query,
            topk_scores=json.dumps(topk_scores),
            threshold=threshold,
            hit_count=hit_count,
            rerank_used=rerank_used,
            latency_ms=latency_ms,
        )
        return await self.retrieval_repo.add(log)

    async def transfer_to_human(self, session_id: int, reason: str) -> ChatSession:
        sess = await self.session_repo.get_by_id(session_id)
        if not sess:
            raise ValueError("会话不存在")
        sess.status = 2  # transferred
        sess.transferred_reason = reason
        await self.session.flush()
        return sess

    async def get_session_messages(self, session_id: int, skip: int = 0, limit: int = 100) -> Sequence[ChatMessage]:
        return await self.msg_repo.list_by_session(session_id, skip, limit)