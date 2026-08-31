"""知识库接口。"""
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user
from app.services.kb_service import KBService

router = APIRouter()


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    file_type: str
    file_url: str
    status: int
    category_id: int | None
    created_by: int | None
    published_at: str | None


class DocumentCreateRequest(BaseModel):
    title: str
    file_type: str
    file_url: str
    file_hash: str
    category_id: int = 0


@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents(
    category_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    svc = KBService(session)
    docs = await svc.list_documents(category_id, skip, limit)
    return [DocumentResponse.model_validate(d) for d in docs]


@router.post("/documents", response_model=DocumentResponse)
async def create_document(
    req: DocumentCreateRequest,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    svc = KBService(session)
    try:
        doc = await svc.create_document(
            title=req.title,
            file_type=req.file_type,
            file_url=req.file_url,
            file_hash=req.file_hash,
            category_id=req.category_id,
            created_by=user.id,
        )
        return DocumentResponse.model_validate(doc)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/documents/{doc_id}/publish")
async def publish_document(
    doc_id: int,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    svc = KBService(session)
    try:
        await svc.publish_document(doc_id)
        return {"message": "文档已发布"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/documents/{doc_id}/offline")
async def offline_document(
    doc_id: int,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    svc = KBService(session)
    try:
        await svc.offline_document(doc_id)
        return {"message": "文档已下线"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))