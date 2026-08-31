"""FastAPI 依赖注入容器。

L2/L3 只依赖 L3 Protocol，L4 实现由本模块装配。
"""

from typing import AsyncGenerator

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_token


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（FastAPI lifespan 注入 engine）。"""
    from app.main import _async_session_factory

    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    request: Request,
    authorization: str | None = Header(None),
    session: AsyncSession = Depends(get_db),
):
    """从 JWT 解析当前用户，注入 request.state。"""
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException(message="缺少认证令牌")

    token = authorization.removeprefix("Bearer ")
    payload = decode_token(token)
    if payload is None:
        raise UnauthorizedException(message="令牌无效或已过期")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException(message="令牌格式无效")

    # 延迟导入避免循环依赖
    from app.repositories.user_repo import UserRepository

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(int(user_id))
    if not user or user.status != 1:
        raise UnauthorizedException(message="用户不存在或已禁用")

    request.state.user = user
    request.state.user_id = user.id
    return user


def require_permission(code: str):
    """权限校验依赖工厂。

    用法: @router.get(...) -> Depends(require_permission("kb:doc:view"))
    """

    async def _check(
        request: Request,
        user=Depends(get_current_user),
    ):
        # 延迟导入
        from app.repositories.rbac_repo import RBACRepository
        from app.services.rbac_service import RBACService

        session = request.state._session if hasattr(request.state, "_session") else None
        # 简化：通过 redis 缓存验证
        from app.core.config import settings as s

        import redis.asyncio as aioredis

        redis = aioredis.from_url(s.redis.url)
        cache_key = f"rbac:perm:{user.id}"
        perms = await redis.smembers(cache_key)
        perm_set = {p.decode() for p in perms}

        if not perm_set and code not in perm_set:
            # 缓存未命中，从 DB 加载
            from app.repositories.user_repo import UserRepository
            from app.repositories.rbac_repo import RBACRepository

            user_repo = UserRepository(request.state._session)
            rbac_repo = RBACRepository(request.state._session)

            # 简化：先放行，实际由中间件层处理
            # TODO: 完整 RBAC 校验链
            pass

        if code not in perm_set:
            raise ForbiddenException(message=f"缺少权限: {code}")

        return user

    return _check


async def get_current_user_or_none(
    authorization: str | None = Header(None),
):
    """可选认证（用于部分公开接口）。"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ")
    payload = decode_token(token)
    if payload is None:
        return None
    return payload.get("sub")


def get_cache():
    """获取 Redis 连接（延迟导入）。"""
    import redis.asyncio as aioredis

    return aioredis.from_url(settings.redis.url)