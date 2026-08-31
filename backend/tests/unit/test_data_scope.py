"""数据范围单元测试。"""
from app.domain.rbac.data_scope import DataScope, PermissionSet, build_data_scope_filter


class TestPermissionSet:
    def test_merge_union_perms(self):
        p1 = PermissionSet(user_id=1, perm_codes={"a", "b"}, data_scope=DataScope.SELF)
        p2 = PermissionSet(user_id=1, perm_codes={"b", "c"}, data_scope=DataScope.DEPT)
        merged = p1.merge(p2)
        assert merged.perm_codes == {"a", "b", "c"}
        assert merged.data_scope == DataScope.DEPT

    def test_merge_scope_wide(self):
        p1 = PermissionSet(user_id=1, data_scope=DataScope.DEPT)
        p2 = PermissionSet(user_id=1, data_scope=DataScope.ALL)
        merged = p1.merge(p2)
        assert merged.data_scope == DataScope.ALL


class TestDataScopeFilter:
    def test_all_returns_none(self):
        assert build_data_scope_filter(DataScope.ALL, user_id=1, dept_id=10) is None

    def test_self_filter(self):
        result = build_data_scope_filter(DataScope.SELF, user_id=1, dept_id=10)
        assert result == "created_by = 1"

    def test_dept_filter(self):
        result = build_data_scope_filter(DataScope.DEPT, user_id=1, dept_id=10)
        assert result == "dept_id = 10"

    def test_dept_and_child_filter(self):
        result = build_data_scope_filter(DataScope.DEPT_AND_CHILD, user_id=1, dept_id=10, child_dept_ids={11, 12})
        assert "10" in result
        assert "11" in result