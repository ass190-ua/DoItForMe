import os

import pytest
from httpx import ASGITransport, AsyncClient


os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("APP_DEBUG", "false")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/doitforme_test",
)
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")

from app.db.session import SessionLocal
from app.main import app  # noqa: E402


@pytest.fixture
async def async_client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
async def session():
    async with SessionLocal() as s:
        yield s
        await s.rollback()
