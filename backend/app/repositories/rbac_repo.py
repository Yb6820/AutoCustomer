"""RBAC repository - roles, permissions, menus."""
from __future__ import annotations
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.rbac import SysRole, SysPermission, SysUserRole, SysRolePerm, SysMenu, SysDept, SysAuditLog, SysLoginLog
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[SysRole]):
    model = SysRole

    async def get_by_code(self, code: str):
        result = await self.session.execute(
            select(SysRole).where(SysRole.code == code, SysRole.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_user_roles(self, user_id: int) -> Sequence[SysRole]:
        result = await self.session.execute(
            select(SysRole)
            .join(SysUserRole, SysUserRole.role_id == SysRole.id)
            .where(SysUserRole.user_id == user_id, SysRole.status == 1, SysRole.deleted_at.is_(None))
        )
        return result.scalars().all()


class PermissionRepository(BaseRepository[SysPermission]):
    model = SysPermission

    async def get_by_code(self, code: str):
        result = await self.session.execute(
            select(SysPermission).where(SysPermission.code == code, SysPermission.status == 1)
        )
        return result.scalar_one_or_none()

    async def get_role_permissions(self, role_id: int) -> Sequence[SysPermission]:
        result = await self.session.execute(
            select(SysPermission)
            .join(SysRolePerm, SysRolePerm.perm_id == SysPermission.id)
            .where(SysRolePerm.role_id == role_id, SysPermission.status == 1)
        )
        return result.scalars().all()


class MenuRepository(BaseRepository[SysMenu]):
    model = SysMenu

    async def list_visible(self) -> Sequence[SysMenu]:
        result = await self.session.execute(
            select(SysMenu).where(SysMenu.visible == True, SysMenu.status == 1).order_by(SysMenu.sort)
        )
        return result.scalars().all()


class DeptRepository(BaseRepository[SysDept]):
    model = SysDept

    async def get_children(self, parent_id: int) -> Sequence[SysDept]:
        result = await self.session.execute(
            select(SysDept).where(SysDept.parent_id == parent_id, SysDept.deleted_at.is_(None))
        )
        return result.scalars().all()

    async def get_all_children_ids(self, parent_id: int) -> set[int]:
        """递归获取所有子部门 ID。"""
        children = await self.get_children(parent_id)
        ids = {c.id for c in children}
        for c in children:
            ids |= await self.get_all_children_ids(c.id)
        ids.add(parent_id)
        return ids


class AuditLogRepository(BaseRepository[SysAuditLog]):
    model = SysAuditLog

    async def list_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> Sequence[SysAuditLog]:
        result = await self.session.execute(
            select(SysAuditLog).where(SysAuditLog.user_id == user_id).order_by(SysAuditLog.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all()


class LoginLogRepository(BaseRepository[SysLoginLog]):
    model = SysLoginLog