"""系统管理接口：模型配置/Prompt/检索配置/审计日志。"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user
from app.repositories.rbac_repo import AuditLogRepository, LoginLogRepository

router = APIRouter()


@router.get("/audit-logs")
async def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = AuditLogRepository(session)
    logs = await repo.list_all(skip, limit)
    return [
        {
            "id": l.id,
            "user_id": l.user_id,
            "action": l.action,
            "resource": l.resource,
            "created_at": str(l.created_at),
        }
        for l in logs
    ]


@router.get("/login-logs")
async def list_login_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = LoginLogRepository(session)
    logs = await repo.list_all(skip, limit)
    return [
        {
            "id": l.id,
            "user_id": l.user_id,
            "username": l.username,
            "status": l.status,
            "msg": l.msg,
            "created_at": str(l.created_at),
        }
        for l in logs
    ]