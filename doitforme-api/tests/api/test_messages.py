import pytest
from uuid import uuid4
from decimal import Decimal
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus
from app.models.user import User, UserRole
from app.schemas.messages import MessageCreateRequest
from app.main import app
from app.api.deps import db_session_dependency, require_authenticated_user

@pytest.mark.asyncio
async def test_chat_authorization_logic(async_client: AsyncClient, session: AsyncSession):
    # Override DB session to reuse the test session
    app.dependency_overrides[db_session_dependency] = lambda: session
    
    # 1. Setup Data
    suffix = str(uuid4())[:8]
    task_id = uuid4()

    # Create Users (let DB generate IDs)
    u1 = User(email=f"c_{suffix}@x.com", password_hash="h", name="C", role=UserRole.POSTER)
    u2 = User(email=f"r_{suffix}@x.com", password_hash="h", name="R", role=UserRole.PERFORMER)
    u3 = User(email=f"s_{suffix}@x.com", password_hash="h", name="S", role=UserRole.PERFORMER)
    
    session.add_all([u1, u2, u3])
    await session.flush()

    creator_id = u1.user_id
    runner_id = u2.user_id
    stranger_id = u3.user_id

    # Create Task
    task = Task(
        task_id=task_id,
        title="Chat Task",
        description="Testing chat",
        creator_id=creator_id,
        runner_id=runner_id,
        status=TaskStatus.ACCEPTED,
        location_lat=Decimal("0"),
        location_lng=Decimal("0"),
        address="X",
        initial_offer=Decimal("10")
    )
    
    session.add(task)
    try:
        await session.commit()
    except Exception as e:
        print(f"ERROR DURING SETUP COMMIT: {e}")
        raise

    # 2. Test Success: Creator sends message
    app.dependency_overrides[require_authenticated_user] = lambda: {"sub": str(creator_id)}
    try:
        resp = await async_client.post(f"/api/v1/tasks/{task_id}/messages", json={"content": "Hello Runner"})
        if resp.status_code != 201:
            print(f"DEBUG RESPONSE: {resp.status_code} - {resp.json()}")
    except Exception as e:
        print(f"ERROR DURING POST: {e}")
        raise
    
    assert resp.status_code == 201
    
    # 3. Test Success: Runner reads messages
    app.dependency_overrides[require_authenticated_user] = lambda: {"sub": str(runner_id)}
    resp = await async_client.get(f"/api/v1/tasks/{task_id}/messages")
    assert resp.status_code == 200
    data = resp.json()["data"]
    messages = data["messages"]
    assert len(messages) == 1
    assert messages[0]["content"] == "Hello Runner"

    # 4. Test Forbidden: Stranger tries to access
    app.dependency_overrides[require_authenticated_user] = lambda: {"sub": str(stranger_id)}
    resp = await async_client.post(f"/api/v1/tasks/{task_id}/messages", json={"content": "I am a hacker"})
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "FORBIDDEN_CHAT_ACCESS"

    resp = await async_client.get(f"/api/v1/tasks/{task_id}/messages")
    assert resp.status_code == 403

    # Cleanup overrides
    app.dependency_overrides.clear()
