"""知识库应用服务。"""
from __future__ import annotations
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.kb import KbCategory, KbDocument, KbChunk, KbQaPair, KbImportTask
from app.repositories.kb_repo import CategoryRepository, DocumentRepository, ChunkRepository, QaPairRepository, ImportTaskRepository


class KBService:
    """知识库文档/分片/分类管理。"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.cat_repo = CategoryRepository(session)
        self.doc_repo = DocumentRepository(session)
        self.chunk_repo = ChunkRepository(session)
        self.qa_repo = QaPairRepository(session)
        self.task_repo = ImportTaskRepository(session)

    async def create_document(self, title: str, file_type: str, file_url: str, file_hash: str, category_id: int = 0, created_by: int = 0) -> KbDocument:
        existing = await self.doc_repo.get_by_hash(file_hash)
        if existing:
            raise ValueError("相同内容的文档已存在")
        doc = KbDocument(
            title=title,
            file_type=file_type,
            file_url=file_url,
            file_hash=file_hash,
            category_id=category_id if category_id else None,
            created_by=created_by,
            status=1,  # draft
        )
        return await self.doc_repo.add(doc)

    async def publish_document(self, doc_id: int) -> KbDocument:
        doc = await self.doc_repo.get_by_id(doc_id)
        if not doc:
            raise ValueError("文档不存在")
        doc.status = 3  # published
        await self.session.flush()
        return doc

    async def offline_document(self, doc_id: int) -> KbDocument:
        doc = await self.doc_repo.get_by_id(doc_id)
        if not doc:
            raise ValueError("文档不存在")
        doc.status = 4  # offline
        await self.session.flush()
        return doc

    async def create_chunk(self, doc_id: int, content: str, chunk_index: int, token_count: int = 0, meta: dict | None = None) -> KbChunk:
        chunk = KbChunk(
            doc_id=doc_id,
            content=content,
            chunk_index=chunk_index,
            token_count=token_count,
            meta=meta,
            embedding_status=1,  # pending
        )
        return await self.chunk_repo.add(chunk)

    async def list_chunks_by_doc(self, doc_id: int) -> Sequence[KbChunk]:
        return await self.chunk_repo.list_by_doc(doc_id)

    async def list_documents(self, category_id: int | None = None, skip: int = 0, limit: int = 100) -> Sequence[KbDocument]:
        if category_id:
            return await self.doc_repo.list_by_category(category_id, skip, limit)
        return await self.doc_repo.list_all(skip, limit)