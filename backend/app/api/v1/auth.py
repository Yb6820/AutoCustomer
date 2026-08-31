"""认证接口：登录/刷新/登出。"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.config import settings
from app.repositories.user_repo import UserRepository
from datetime import timedelta

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, session: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_username(req.username)
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if user.status != 1:
        raise HTTPException(status_code=403, detail="账号已被禁用")

    access_token = create_access_token(
        user.id,
        {"username": user.username},
        timedelta(minutes=settings.jwt.access_token_expire_minutes),
    )
    refresh_token = create_refresh_token(
        user.id,
        {"username": user.username},
        timedelta(days=settings.jwt.refresh_token_expire_days),
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh")
async def refresh_token(refresh_token: str, session: AsyncSession = Depends(get_db)):
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="无效的刷新令牌")

    user_id = payload.get("sub")
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    access_token = create_access_token(user.id, {"username": user.username}, timedelta(minutes=settings.jwt.access_token_expire_minutes))
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout")
async def logout(user=Depends(get_current_user)):
    return {"message": "已登出"}