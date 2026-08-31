from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, Integer, JSON, SmallInteger, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class KbCategory(Base, TimestampMixin):
    __tablename__ = "kb_category"

    parent_id: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    sort: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class KbDocument(Base, TimestampMixin):
    __tablename__ = "kb_document"
    __table_args__ = (
        Index("ix_kb_document_category_id_status", "category_id", "status"),
        UniqueConstraint("file_hash", name="uq_kb_document_file_hash"),
    )

    category_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(16), nullable=False)
    file_url: Mapped[str] = mapped_column(String(512), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="1=draft 2=pending_review 3=published 4=offline"
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class KbChunk(Base, TimestampMixin):
    __tablename__ = "kb_chunk"
    __table_args__ = (
        UniqueConstraint("doc_id", "chunk_index", name="uq_kb_chunk_doc_id_chunk_index"),
        Index("ix_kb_chunk_embedding_status", "embedding_status"),
    )

    doc_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    token_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="1=active 2=archived")
    embedding_status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="1=pending 2=done 3=failed"
    )


class KbQaPair(Base, TimestampMixin):
    __tablename__ = "kb_qa_pair"

    doc_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    chunk_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    hit_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)


class KbImportTask(Base, TimestampMixin):
    __tablename__ = "kb_import_task"

    doc_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    task_type: Mapped[str] = mapped_column(String(16), nullable=False, comment="parse/chunk/embed/index")
    status: Mapped[str] = mapped_column(String(16), nullable=False, comment="pending/running/done/failed")
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_msg: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)