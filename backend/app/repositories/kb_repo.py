"""Knowledge base repository."""
from __future__ import annotations
from typing import Optional, Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.kb import KbCategory, KbDocument, KbChunk, KbQaPair, KbImportTask
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[KbCategory]):
    model = KbCategory


class DocumentRepository(BaseRepository[KbDocument]):
    model = KbDocument

    async def get_by_hash(self, file_hash: str) -> Optional[KbDocument]:
        result = await self.session.execute(
            select(KbDocument).where(KbDocument.file_hash == file_hash, KbDocument.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_by_category(self, category_id: int, skip: int = 0, limit: int = 100) -> Sequence[KbDocument]:
        result = await self.session.execute(
            select(KbDocument)
            .where(KbDocument.category_id == category_id, KbDocument.deleted_at.is_(None))
            .offset(skip).limit(limit)
        )
        return result.scalars().all()


class ChunkRepository(BaseRepository[KbChunk]):
    model = KbChunk

    async def list_by_doc(self, doc_id: int) -> Sequence[KbChunk]:
        result = await self.session.execute(
            select(KbChunk).where(KbChunk.doc_id == doc_id).order_by(KbChunk.chunk_index)
        )
        return result.scalars().all()

    async def count_active(self) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(KbChunk).where(KbChunk.status == 1, KbChunk.embedding_status == 2)
        )
        return result.scalar() or 0

    async def count_pending(self) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(KbChunk).where(KbChunk.embedding_status == 1)
        )
        return result.scalar() or 0


class QaPairRepository(BaseRepository[KbQaPair]):
    model = KbQaPair


class ImportTaskRepository(BaseRepository[KbImportTask]):
    model = KbImportTask