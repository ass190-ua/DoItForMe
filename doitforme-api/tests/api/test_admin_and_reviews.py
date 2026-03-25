import pytest
from uuid import UUID, uuid4
from decimal import Decimal
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.api.deps import db_session_dependency, require_authenticated_user, require_admin_user
from app.models.task import Task, TaskStatus
from app.models.user import User, UserRole
from app.models.review import Review

class DummySession:
    async def commit(self): pass
    async def flush(self): pass
    async def refresh(self, obj): pass
    def add(self, obj): pass
    async def execute(self, stmt):
        class Result:
            def scalars(self):
                class Scalars:
                    def all(self): return []
                    def first(self): return None
                return Scalars()
            def scalar_one_or_none(self): return None
        return Result()
    async def scalar(self, stmt): return 0
    async def get(self, model, id): return None

async def override_db_session():
    yield DummySession()

def override_admin_user():
    return {"sub": str(uuid4()), "role": "admin", "email": "admin@test.com"}

def override_poster_user():
    return {"sub": "00000000-0000-0000-0000-000000000020", "role": "poster", "email": "poster@test.com"}

# ─── Review Tests ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_review_success(monkeypatch):
    from app.repositories.task_repository import TaskRepository
    from app.repositories.user_repository import UserRepository
    from app.repositories.review_repository import ReviewRepository
    from datetime import datetime, timezone
    
    task_id = uuid4()
    creator_id = UUID("00000000-0000-0000-0000-000000000020")
    runner_id = UUID("00000000-0000-0000-0000-000000000010")
    
    mock_task = Task(
        task_id=task_id, creator_id=creator_id, runner_id=runner_id,
        status=TaskStatus.COMPLETED, accepted_price=Decimal("50.00")
    )
    mock_user = User(user_id=runner_id, rating=Decimal("0.00"), rating_count=0)

    async def fake_get_task(self, tid): return mock_task
    async def fake_get_user(self, uid): return mock_user
    async def fake_get_review(self, tid, rid): return None
    async def fake_create_review(self, rev): 
        rev.id = uuid4()
        rev.created_at = datetime.now(timezone.utc)
        return rev

    monkeypatch.setattr(TaskRepository, "get_by_id", fake_get_task)
    monkeypatch.setattr(UserRepository, "get_for_update", fake_get_user)
    monkeypatch.setattr(ReviewRepository, "get_by_task_and_reviewer", fake_get_review)
    monkeypatch.setattr(ReviewRepository, "create", fake_create_review)

    from app.api.deps import get_current_token_payload
    app.dependency_overrides[get_current_token_payload] = override_poster_user
    app.dependency_overrides[db_session_dependency] = override_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(
            f"/api/v1/reviews/{task_id}",
            json={"reviewee_id": str(runner_id), "rating": 5, "comment": "Great job!"}
        )
        assert resp.status_code == 201
        assert mock_user.rating == Decimal("5")
        assert mock_user.rating_count == 1
    
    app.dependency_overrides.clear()

# ─── Admin Tests ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_admin_metrics_access_denied():
    from app.api.deps import get_current_token_payload
    app.dependency_overrides[get_current_token_payload] = override_poster_user
    app.dependency_overrides[db_session_dependency] = override_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/api/v1/admin/metrics")
        assert resp.status_code == 403 # Only admins
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_admin_metrics_success():
    from app.api.deps import get_current_token_payload
    app.dependency_overrides[get_current_token_payload] = override_admin_user
    app.dependency_overrides[db_session_dependency] = override_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/api/v1/admin/metrics")
        assert resp.status_code == 200
        assert "total_users" in resp.json()["data"]
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_admin_force_refund(monkeypatch):
    from app.repositories.task_repository import TaskRepository
    from app.repositories.user_repository import UserRepository
    from app.repositories.transaction_repository import TransactionRepository
    from datetime import datetime, timezone

    task_id = uuid4()
    creator_id = uuid4()
    task = Task(
        task_id=task_id, 
        creator_id=creator_id, 
        status=TaskStatus.ACCEPTED, 
        accepted_price=Decimal("100.00"),
        title="Test Task",
        description="Test Description",
        location_lat=Decimal("40.0"),
        location_lng=Decimal("-3.0"),
        address="Test Address",
        category="Testing",
        initial_offer=Decimal("100.00"),
        created_at=datetime.now(timezone.utc)
    )
    creator = User(user_id=creator_id, balance=Decimal("0.00"))

    async def fake_get_task(s, tid): return task
    async def fake_update_task(s, t): return t
    async def fake_get_user(s, uid): return creator
    async def fake_update_user(s, u): return u
    async def fake_create_tx(s, tx): return tx

    monkeypatch.setattr(TaskRepository, "get_by_id", fake_get_task)
    monkeypatch.setattr(TaskRepository, "update", fake_update_task)
    monkeypatch.setattr(UserRepository, "get_for_update", fake_get_user)
    monkeypatch.setattr(UserRepository, "update", fake_update_user)
    monkeypatch.setattr(TransactionRepository, "create", fake_create_tx)

    from app.api.deps import get_current_token_payload
    app.dependency_overrides[get_current_token_payload] = override_admin_user
    app.dependency_overrides[db_session_dependency] = override_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(f"/api/v1/admin/payments/{task_id}/adjust?action=refund")
        assert resp.status_code == 200
        assert task.status == TaskStatus.CANCELLED
        assert creator.balance == Decimal("100.00")
    
    app.dependency_overrides.clear()
