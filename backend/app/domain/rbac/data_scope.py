"""数据范围过滤器。"""
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional


class DataScope(IntEnum):
    ALL = 1
    DEPT = 2
    DEPT_AND_CHILD = 3
    SELF = 4
    CUSTOM = 5


@dataclass
class PermissionSet:
    """用户权限集（角色并集计算结果）。"""
    user_id: int
    perm_codes: set[str] = field(default_factory=set)
    data_scope: DataScope = DataScope.SELF
    scope_dept_ids: set[int] = field(default_factory=set)

    def has_perm(self, code: str) -> bool:
        return code in self.perm_codes

    def merge(self, other: "PermissionSet") -> "PermissionSet":
        codes = self.perm_codes | other.perm_codes
        # 数值越小范围越宽（ALL=1 最宽，CUSTOM=5 最窄），取最宽档
        scope = self.data_scope if self.data_scope < other.data_scope else other.data_scope
        if scope == DataScope.CUSTOM:
            dept_ids = self.scope_dept_ids | other.scope_dept_ids
        else:
            dept_ids = self.scope_dept_ids
        return PermissionSet(user_id=self.user_id, perm_codes=codes, data_scope=scope, scope_dept_ids=dept_ids)


def build_data_scope_filter(
    scope: DataScope,
    user_id: int,
    dept_id: Optional[int],
    child_dept_ids: Optional[set[int]] = None,
    custom_dept_ids: Optional[set[int]] = None,
    owner_field: str = "created_by",
) -> Optional[str]:
    """根据数据范围生成 SQL WHERE 片段（用于 Repository 拼接）。

    Returns:
        WHERE 片段字符串，ALL 返回 None。
    """
    if scope == DataScope.ALL:
        return None
    elif scope == DataScope.SELF:
        return f"{owner_field} = {user_id}"
    elif scope == DataScope.DEPT:
        return f"dept_id = {dept_id}"
    elif scope == DataScope.DEPT_AND_CHILD:
        ids = {dept_id} | (child_dept_ids or set())
        return f"dept_id IN ({','.join(str(i) for i in ids)})"
    elif scope == DataScope.CUSTOM:
        ids = custom_dept_ids or set()
        return f"dept_id IN ({','.join(str(i) for i in ids)})"
    return None