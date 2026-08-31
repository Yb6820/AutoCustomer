"""测试基础配置。"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.models.base import Base

# 确保所有模型表注册到 Base.metadata
import app.models.rbac  # noqa: F401
import app.models.chat  # noqa: F401
import app.models.kb  # noqa: F401
import app.models.ticket  # noqa: F401
import app.models.ai  # noqa: F401
import app.models.stat  # noqa: F401


@pytest_asyncio.fixture
async def db_session():
    """内存 SQLite 测试数据库。"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest.fixture
def mock_embedding():
    from app.integrations.embedding.base import MockEmbeddingProvider
    return MockEmbeddingProvider(dim=768)


@pytest.fixture
def mock_vector_store():
    from app.integrations.milvus.gateway import MockVectorStore
    return MockVectorStore()


@pytest.fixture
def mock_llm():
    from app.integrations.llm.base import MockLLMProvider
    return MockLLMProvider()