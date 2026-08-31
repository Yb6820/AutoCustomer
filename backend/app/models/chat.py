from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Float, Index, Integer, JSON, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ChatSession(Base, TimestampMixin):
    __tablename__ = "chat_session"
    __table_args__ = (
        Index("ix_chat_session_customer_status_last", "customer_id", "status", "last_msg_at"),
        Index("ix_chat_session_status_created", "status", "created_at"),
    )

    customer_id: Mapped[str] = mapped_column(String(64), nullable=False)
    source: Mapped[str] = mapped_column(String(16), nullable=False, comment="web/h5/mini/wechat")
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="1=active 2=transferred 3=closed"
    )
    rating: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    model_config_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    transferred_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_msg_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class ChatMessage(Base, TimestampMixin):
    __tablename__ = "chat_message"
    __table_args__ = (
        Index("ix_chat_message_session_created", "session_id", "created_at"),
        Index("ix_chat_message_created", "created_at"),
    )

    session_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False, comment="user/assistant/system/agent")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    msg_type: Mapped[str] = mapped_column(String(16), nullable=False, comment="text/card/transfer/rating")
    tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    retrieval_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


class ChatRetrievalLog(Base, TimestampMixin):
    __tablename__ = "chat_retrieval_log"
    __table_args__ = (
        Index("ix_chat_retrieval_log_message_id", "message_id"),
        Index("ix_chat_retrieval_log_created", "created_at"),
    )

    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    topk_scores: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    threshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    hit_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rerank_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


class ChatFeedback(Base, TimestampMixin):
    __tablename__ = "chat_feedback"
    __table_args__ = (
        Index("ix_chat_feedback_message_id", "message_id"),
    )

    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    session_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    feedback_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="1=点赞 2=点踩"
    )
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class ChatQuickReply(Base, TimestampMixin):
    __tablename__ = "chat_quick_reply"

    scene: Mapped[str] = mapped_column(String(32), nullable=False, comment="greeting/refund/shipping")
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sort: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)