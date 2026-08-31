"""FastAPI 应用工厂与生命周期管理。"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.middleware import register_middleware

# 全局引擎与会话工厂（在 lifespan 中初始化）
_engine = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


def _get_db_url() -> str:
    return (
        f"mysql+asyncmy://{settings.db.user}:{settings.db.password}"
        f"@{settings.db.host}:{settings.db.port}/{settings.db.name}"
        f"?charset=utf8mb4"
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期：初始化连接池 → 服务 → 关闭连接池。"""
    global _engine, _async_session_factory

    _engine = create_async_engine(
        _get_db_url(),
        pool_size=settings.db.pool_size,
        max_overflow=settings.db.pool_overflow,
        pool_pre_ping=True,
        echo=False,
    )
    _async_session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # 健康检查就绪
    app.state.ready = True

    yield

    # 关闭连接池
    if _engine:
        await _engine.dispose()
        _engine = None
        _async_session_factory = None


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例。"""
    app = FastAPI(
        title="AutoCustomer",
        description="电商智能客服机器人 API",
        version="0.1.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # 注册异常处理器
    register_exception_handlers(app)

    # 注册中间件
    register_middleware(app)

    # 注册路由
    _register_routes(app)

    # 健康检查
    @app.get("/healthz")
    async def healthz():
        return {"status": "ok"}

    @app.get("/readyz")
    async def readyz():
        ready = getattr(app.state, "ready", False)
        if not ready:
            return {"status": "not_ready"}, 503
        return {"status": "ready"}

    return app


def _register_routes(app: FastAPI):
    """注册各模块路由。"""
    from app.api.v1 import auth, chat, kb, tickets, users, roles, admin

    app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["用户管理"])
    app.include_router(roles.router, prefix="/api/v1/roles", tags=["角色管理"])
    app.include_router(kb.router, prefix="/api/v1/kb", tags=["知识库"])
    app.include_router(chat.router, prefix="/api/v1/chat", tags=["对话"])
    app.include_router(tickets.router, prefix="/api/v1/tickets", tags=["工单"])
    app.include_router(admin.router, prefix="/api/v1/admin", tags=["系统管理"])


app = create_app()