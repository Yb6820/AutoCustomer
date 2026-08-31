from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import BigInteger, Date, DateTime, Float, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class StatDaily(Base, TimestampMixin):
    __tablename__ = "stat_daily"

    stat_date: Mapped[date] = mapped_column(Date, unique=True, nullable=False)
    session_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ticket_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    transfer_rate: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    hit_rate: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    avg_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_first_response_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    llm_tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)