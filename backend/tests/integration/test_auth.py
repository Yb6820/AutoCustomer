"""认证集成测试。"""
import pytest
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_login(db_session):
    from app.main import app
    from app.services.rbac_service import RBACService, UserCreate
    from app.core.deps import get_db

    # 覆盖依赖：使用测试数据库会话
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    svc = RBACService(db_session)
    await svc.create_user(UserCreate(username="test", password="test123", nickname="Test"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/auth/login", json={"username": "test", "password": "test123"})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_login_wrong_password(db_session):
    from app.main import app
    from app.services.rbac_service import RBACService, UserCreate
    from app.core.deps import get_db

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    svc = RBACService(db_session)
    await svc.create_user(UserCreate(username="test", password="test123", nickname="Test"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/auth/login", json={"username": "test", "password": "wrong"})
        assert resp.status_code == 401

    app.dependency_overrides.clear()