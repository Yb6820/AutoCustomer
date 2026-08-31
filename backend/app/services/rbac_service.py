"""RBAC 应用服务：用户、角色、权限、菜单管理。"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password
from app.domain.rbac.data_scope import DataScope, PermissionSet
from app.models.rbac import SysUser, SysRole, SysPermission, SysUserRole, SysMenu, SysDept, SysAuditLog
from app.repositories.user_repo import UserRepository
from app.repositories.rbac_repo import RoleRepository, PermissionRepository, MenuRepository, DeptRepository, AuditLogRepository


@dataclass
class UserCreate:
    username: str
    password: str
    nickname: str = ""
    email: str = ""
    phone: str = ""
    dept_id: int | None = None


@dataclass
class RoleCreate:
    code: str
    name: str
    role_type: int = 3
    data_scope: int = DataScope.SELF
    remark: str = ""


class RBACService:
    """用户/角色/权限/菜单管理服务。"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.role_repo = RoleRepository(session)
        self.perm_repo = PermissionRepository(session)
        self.menu_repo = MenuRepository(session)
        self.dept_repo = DeptRepository(session)
        self.audit_repo = AuditLogRepository(session)

    async def create_user(self, data: UserCreate) -> SysUser:
        existing = await self.user_repo.get_by_username(data.username)
        if existing:
            raise ValueError(f"用户名 {data.username} 已存在")
        user = SysUser(
            username=data.username,
            password_hash=hash_password(data.password),
            nickname=data.nickname or data.username,
            email=data.email,
            phone=data.phone,
            dept_id=data.dept_id,
        )
        return await self.user_repo.add(user)

    async def get_user_permissions(self, user_id: int) -> PermissionSet:
        """计算用户完整权限集（角色并集）。"""
        roles = await self.role_repo.get_user_roles(user_id)
        ps = PermissionSet(user_id=user_id)
        for role in roles:
            perms = await self.perm_repo.get_role_permissions(role.id)
            ps.perm_codes.update(p.code for p in perms)
            # 数据范围取最宽档
            role_scope = DataScope(role.data_scope)
            if role_scope < ps.data_scope:
                ps.data_scope = role_scope
        return ps

    async def create_role(self, data: RoleCreate) -> SysRole:
        existing = await self.role_repo.get_by_code(data.code)
        if existing:
            raise ValueError(f"角色码 {data.code} 已存在")
        role = SysRole(
            code=data.code,
            name=data.name,
            role_type=data.role_type,
            data_scope=data.data_scope,
            remark=data.remark,
        )
        return await self.role_repo.add(role)

    async def assign_role(self, user_id: int, role_id: int) -> SysUserRole:
        mapping = SysUserRole(user_id=user_id, role_id=role_id)
        self.session.add(mapping)
        await self.session.flush()
        return mapping

    async def assign_permission(self, role_id: int, perm_id: int) -> None:
        from app.models.rbac import SysRolePerm
        mapping = SysRolePerm(role_id=role_id, perm_id=perm_id)
        self.session.add(mapping)
        await self.session.flush()

    async def get_menus_for_user(self, user_id: int) -> list[SysMenu]:
        """获取用户可见菜单树。"""
        ps = await self.get_user_permissions(user_id)
        all_menus = await self.menu_repo.list_visible()
        visible = [m for m in all_menus if not m.perm_code or m.perm_code in ps.perm_codes]
        return visible

    async def write_audit(self, user_id: int, action: str, resource: str, detail: dict | None = None, ip: str = "", user_agent: str = "") -> SysAuditLog:
        import json
        log = SysAuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            detail=json.dumps(detail) if detail else None,
            ip=ip,
            user_agent=user_agent,
        )
        return await self.audit_repo.add(log)