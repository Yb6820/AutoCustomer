from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Float, Integer, JSON, SmallInteger, String, Text, VARBINARY, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class SysModelConfig(Base, TimestampMixin):
    __tablename__ = "sys_model_config"

    model_type: Mapped[str] = mapped_column(String(16), nullable=False, comment="llm/embedding/rerank")
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    model_name: Mapped[str] = mapped_column(String(64), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(512), nullable=False)
    api_key_enc: Mapped[Optional[bytes]] = mapped_column(VARBINARY(512), nullable=True)
    params: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)


class SysPromptTemplate(Base, TimestampMixin):
    __tablename__ = "sys_prompt_template"

    scene: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="chat_hit/chat_miss/rewrite/summarize"
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)


class KbRetrievalConfig(Base, TimestampMixin):
    __tablename__ = "kb_retrieval_config"

    scope: Mapped[str] = mapped_column(String(16), nullable=False, comment="global/category/doc")
    target_id: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    topk: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    score_threshold: Mapped[float] = mapped_column(Float, default=0.78, nullable=False)
    rerank_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rerank_model_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    status: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)