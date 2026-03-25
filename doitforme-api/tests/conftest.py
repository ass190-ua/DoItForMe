import os

import pytest
from httpx import ASGITransport, AsyncClient


os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("APP_DEBUG", "false")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/doitforme_test_v2",
)
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")

from app.db.session import SessionLocal
from app.main import app  # noqa: E402


@pytest.fixture
async def async_client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    from app.db.base import Base
    from app.db.session import engine
    # Import models to register them in MetaData
    import app.models  # noqa: F401
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
async def session():
    from app.core.config import get_settings
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    
    # Clear settings cache and ensure env is set
    get_settings.cache_clear()
    settings = get_settings()
    
    test_engine = create_async_engine(settings.database_url, future=True)
    TestSessionLocal = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with TestSessionLocal() as s:
        yield s
        await s.rollback()
    
    await test_engine.dispose()
