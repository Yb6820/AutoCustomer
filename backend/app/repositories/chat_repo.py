"""Chat repository."""
from __future__ import annotations
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import ChatSession, ChatMessage, ChatRetrievalLog, ChatFeedback, ChatQuickReply
from app.repositories.base import BaseRepository


class SessionRepository(BaseRepository[ChatSession]):
    model = ChatSession

    async def list_by_customer(self, customer_id: str, skip: int = 0, limit: int = 50) -> Sequence[ChatSession]:
        result = await self.session.execute(
            select(ChatSession)
            .where(ChatSession.customer_id == customer_id)
            .order_by(ChatSession.last_msg_at.desc())
            .offset(skip).limit(limit)
        )
        return result.scalars().all()


class MessageRepository(BaseRepository[ChatMessage]):
    model = ChatMessage

    async def list_by_session(self, session_id: int, skip: int = 0, limit: int = 100) -> Sequence[ChatMessage]:
        result = await self.session.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
            .offset(skip).limit(limit)
        )
        return result.scalars().all()


class RetrievalLogRepository(BaseRepository[ChatRetrievalLog]):
    model = ChatRetrievalLog


class FeedbackRepository(BaseRepository[ChatFeedback]):
    model = ChatFeedback


class QuickReplyRepository(BaseRepository[ChatQuickReply]):
    model = ChatQuickReply