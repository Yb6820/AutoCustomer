"""User repository."""
from __future__ import annotations
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.rbac import SysUser
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[SysUser]):
    model = SysUser

    async def get_by_username(self, username: str) -> Optional[SysUser]:
        result = await self.session.execute(
            select(SysUser).where(SysUser.username == username, SysUser.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_by_dept(self, dept_id: int, skip: int = 0, limit: int = 100) -> Sequence[SysUser]:
        result = await self.session.execute(
            select(SysUser)
            .where(SysUser.dept_id == dept_id, SysUser.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()