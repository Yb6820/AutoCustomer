"""角色管理接口。"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user
from app.repositories.rbac_repo import RoleRepository, PermissionRepository
from app.services.rbac_service import RBACService, RoleCreate

router = APIRouter()


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    role_type: int
    data_scope: int
    is_system: bool
    status: int


class RoleCreateRequest(BaseModel):
    code: str
    name: str
    data_scope: int = 4
    remark: str = ""


@router.get("", response_model=list[RoleResponse])
async def list_roles(
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = RoleRepository(session)
    roles = await repo.list_all()
    return [RoleResponse.model_validate(r) for r in roles]


@router.post("", response_model=RoleResponse)
async def create_role(
    req: RoleCreateRequest,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    svc = RBACService(session)
    role = await svc.create_role(RoleCreate(
        code=req.code,
        name=req.name,
        data_scope=req.data_scope,
        remark=req.remark,
    ))
    return RoleResponse.model_validate(role)


@router.post("/{role_id}/permissions/{perm_id}")
async def assign_permission(
    role_id: int,
    perm_id: int,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    svc = RBACService(session)
    await svc.assign_permission(role_id, perm_id)
    return {"message": "权限已分配"}