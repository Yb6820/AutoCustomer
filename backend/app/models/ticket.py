from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Index, Integer, JSON, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class AgentGroup(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "agent_group"

    name: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sort: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)


class AgentProfile(Base, TimestampMixin):
    __tablename__ = "agent_profile"

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    group_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    agent_no: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    skill_tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    max_concurrency: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    online_status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="1=在线 2=忙碌 3=离线"
    )


class HumanTicket(Base, TimestampMixin):
    __tablename__ = "human_ticket"
    __table_args__ = (
        Index("ix_human_ticket_assignee_status", "assignee_id", "status"),
        Index("ix_human_ticket_status_priority_created", "status", "priority", "created_at"),
    )

    session_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    ticket_no: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="1=pending 2=assigned 3=processing 4=resolved 5=closed"
    )
    priority: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="1=低 2=中 3=高 4=紧急"
    )
    assignee_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    group_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    first_response_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class TicketComment(Base, TimestampMixin):
    __tablename__ = "ticket_comment"

    ticket_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    author_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class TicketAssignLog(Base, TimestampMixin):
    __tablename__ = "ticket_assign_log"

    ticket_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    from_agent_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    to_agent_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    action: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="assign/transfer/claim/escalate/close"
    )
    operator_id: Mapped[int] = mapped_column(BigInteger, nullable=False)