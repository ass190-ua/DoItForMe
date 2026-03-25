import pytest
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.api.deps import db_session_dependency
from app.models.user import User, UserRole
from app.models.task import Task, TaskStatus

# Reuse dependency overrides
class MockSession:
    async def commit(self): pass
    async def rollback(self): pass
    async def flush(self): pass
    async def close(self): pass
    def add(self, obj): pass

async def override_db_session():
    yield MockSession()

def create_mock_task(i):
    return Task(
        task_id=uuid4(),
        creator_id=uuid4(),
        title=f"Task {i}",
        description="Description",
        status=TaskStatus.PUBLISHED,
        location_lat=Decimal("40.0"),
        location_lng=Decimal("-3.0"),
        address="Address",
        category="Category",
        initial_offer=Decimal("10.00"),
        created_at=datetime.now(timezone.utc)
    )

@pytest.mark.asyncio
async def test_pagination_available_tasks(monkeypatch):
    from app.repositories.task_repository import TaskRepository
    
    tasks = []
    # Create 25 mock tasks
    for i in range(25):
        tasks.append((create_mock_task(i), 1.0))

    async def fake_get_available(s, **kwargs):
        limit = kwargs.get("limit", 20)
        offset = kwargs.get("offset", 0)
        return tasks[offset : offset + limit]

    monkeypatch.setattr(TaskRepository, "get_available_tasks", fake_get_available)
    
    from app.api.deps import require_authenticated_user
    async def override_user(): return {"sub": str(uuid4()), "role": "poster"}
    app.dependency_overrides[require_authenticated_user] = override_user
    app.dependency_overrides[db_session_dependency] = override_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Test default limit (20)
        resp = await client.get("/api/v1/tasks/available?lat=40&lng=-3")
        assert resp.status_code == 200
        assert len(resp.json()["data"]["tasks"]) == 20

@pytest.mark.asyncio
async def test_password_recovery_flow(monkeypatch):
    from app.repositories.user_repository import UserRepository
    from app.core.security import verify_password
    
    user = User(
        email="test@example.com", 
        password_hash="old_hash",
        password_reset_token=None
    )
    
    async def fake_get_by_email(s, email): return user
    async def fake_get_by_token(s, token): return user if user.password_reset_token == token else None
    async def fake_update(s, u): return u

    monkeypatch.setattr(UserRepository, "get_by_email", fake_get_by_email)
    monkeypatch.setattr(UserRepository, "get_by_reset_token", fake_get_by_token)
    monkeypatch.setattr(UserRepository, "update", fake_update)
    
    # Mock hashing/verification to avoid environment-specific bcrypt 72-byte issues
    monkeypatch.setattr("app.services.auth_service.hash_password", lambda p: f"hashed_{p}")
    monkeypatch.setattr("app.core.security.verify_password", lambda p, h: h == f"hashed_{p}")

    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            # 1. Request recovery
            resp = await client.post("/api/v1/auth/password-recovery", json={"email": "test@example.com"})
            assert resp.status_code == 200
            assert user.password_reset_token is not None
            token = user.password_reset_token
            
            # 2. Reset password
            resp = await client.post("/api/v1/auth/password-reset", json={
                "token": token,
                "new_password": "secure123"
            })
            assert resp.status_code == 200
            assert user.password_reset_token is None
    finally:
        app.dependency_overrides.clear()
