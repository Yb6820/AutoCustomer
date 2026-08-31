"""用户管理接口。"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user
from app.repositories.user_repo import UserRepository
from app.services.rbac_service import RBACService, UserCreate

router = APIRouter()


class UserCreateRequest(BaseModel):
    username: str
    password: str
    nickname: str = ""
    email: str = ""
    phone: str = ""
    dept_id: int | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nickname: str
    email: str
    phone: str
    status: int
    dept_id: int | None


@router.get("", response_model=list[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = UserRepository(session)
    users = await repo.list_all(skip, limit)
    return [UserResponse.model_validate(u) for u in users]


@router.post("", response_model=UserResponse)
async def create_user(
    req: UserCreateRequest,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    svc = RBACService(session)
    new_user = await svc.create_user(UserCreate(
        username=req.username,
        password=req.password,
        nickname=req.nickname,
        email=req.email,
        phone=req.phone,
        dept_id=req.dept_id,
    ))
    return UserResponse.model_validate(new_user)


@router.get("/me", response_model=UserResponse)
async def get_me(user=Depends(get_current_user)):
    return UserResponse.model_validate(user)