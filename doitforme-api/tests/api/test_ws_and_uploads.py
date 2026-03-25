"""Tests for WebSocket chat and file upload endpoints."""
import io
from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.security import create_access_token
from app.main import app


def _make_token(user_id, email="ws@test.com", role="poster"):
    return create_access_token(
        subject=str(user_id),
        email=email,
        role=role,
        token_type="access",
    )


# ─── Upload Tests ────────────────────────────────────────────────
import io
from types import SimpleNamespace
from httpx import ASGITransport, AsyncClient
from uuid import UUID, uuid4

from app.api.deps import db_session_dependency, require_authenticated_user


class DummySession:
    async def commit(self):
        pass


async def override_db_session():
    yield DummySession()


def override_runner_user():
    return {"sub": "00000000-0000-0000-0000-000000000010"}


def override_creator_user():
    return {"sub": "00000000-0000-0000-0000-000000000020"}


def override_other_user():
    return {"sub": "00000000-0000-0000-0000-000000000030"}


@pytest.fixture
def mock_task(monkeypatch):
    from app.repositories.task_repository import TaskRepository
    from app.models.task import Task
    
    # By default, task is in_progress, runner is 00...10, creator is 00...20
    task = Task(
        task_id=uuid4(),
        runner_id=UUID("00000000-0000-0000-0000-000000000010"),
        creator_id=UUID("00000000-0000-0000-0000-000000000020"),
        status="in_progress"
    )

    async def fake_get_by_id(self, task_id):
        return task

    async def fake_update(self, t):
        return t

    monkeypatch.setattr(TaskRepository, "get_by_id", fake_get_by_id)
    monkeypatch.setattr(TaskRepository, "update", fake_update)
    return task


@pytest.fixture
def mock_message(monkeypatch):
    from app.repositories.message_repository import MessageRepository
    from app.models.message import Message
    from datetime import datetime, UTC

    async def fake_create(self, msg):
        msg.id = uuid4()
        msg.created_at = datetime.now(UTC)
        return msg

    monkeypatch.setattr(MessageRepository, "create", fake_create)


@pytest.mark.asyncio
async def test_upload_task_proof_success(mock_task):
    """Runner can upload a proof image for an in-progress task."""
    app.dependency_overrides[require_authenticated_user] = override_runner_user
    app.dependency_overrides[db_session_dependency] = override_db_session
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        fake_image = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        resp = await client.post(
            f"/api/v1/uploads/task-proof/{mock_task.task_id}",
            files={"file": ("proof.jpg", io.BytesIO(fake_image), "image/jpeg")},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "image_url" in body["data"]
        assert body["data"]["image_url"].startswith("/uploads/tasks/")
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_task_proof_forbidden_for_creator(mock_task):
    """Creator cannot upload proof — only the runner can."""
    app.dependency_overrides[require_authenticated_user] = override_creator_user
    app.dependency_overrides[db_session_dependency] = override_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        fake_image = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        resp = await client.post(
            f"/api/v1/uploads/task-proof/{mock_task.task_id}",
            files={"file": ("proof.jpg", io.BytesIO(fake_image), "image/jpeg")},
        )
        assert resp.status_code == 403
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_rejects_invalid_mime_type(mock_task):
    """Uploading a non-image file returns 400."""
    app.dependency_overrides[require_authenticated_user] = override_runner_user
    app.dependency_overrides[db_session_dependency] = override_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(
            f"/api/v1/uploads/task-proof/{mock_task.task_id}",
            files={"file": ("doc.pdf", io.BytesIO(b"not an image"), "application/pdf")},
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "INVALID_FILE_TYPE"
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_rejects_oversized_file(mock_task):
    """Uploading a file larger than 5MB returns 400."""
    app.dependency_overrides[require_authenticated_user] = override_runner_user
    app.dependency_overrides[db_session_dependency] = override_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Create a faux file slightly larger than 5MB without actually allocating 6MB of memory
        # Wait, the application reads the file into memory to check size.
        big_file = b"\xff\xd8\xff\xe0" + b"\x00" * (6 * 1024 * 1024)
        resp = await client.post(
            f"/api/v1/uploads/task-proof/{mock_task.task_id}",
            files={"file": ("big.jpg", io.BytesIO(big_file), "image/jpeg")},
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "FILE_TOO_LARGE"
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_chat_image_success(mock_task, mock_message):
    """Both creator and runner can upload chat images."""
    app.dependency_overrides[require_authenticated_user] = override_creator_user
    app.dependency_overrides[db_session_dependency] = override_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        fake_image = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        resp = await client.post(
            f"/api/v1/uploads/chat-image/{mock_task.task_id}",
            files={"file": ("chat.jpg", io.BytesIO(fake_image), "image/jpeg")},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["message"]["image_url"].startswith("/uploads/messages/")
        assert body["data"]["message"]["content"] == "[image]"
    app.dependency_overrides.clear()


# ─── WebSocket ConnectionManager Unit Tests ──────────────────────


@pytest.mark.asyncio
async def test_connection_manager_connect_disconnect():
    """ConnectionManager correctly tracks connections by room."""
    from app.core.ws_manager import ConnectionManager
    
    manager = ConnectionManager()
    task_id = uuid4()
    user_id = uuid4()
    
    class FakeWebSocket:
        accepted = False
        async def accept(self):
            self.accepted = True
        async def send_json(self, data):
            pass
    
    ws = FakeWebSocket()
    await manager.connect(task_id, user_id, ws)
    
    assert task_id in manager.active_connections
    assert user_id in manager.active_connections[task_id]
    assert ws.accepted is True
    
    manager.disconnect(task_id, user_id)
    assert task_id not in manager.active_connections


@pytest.mark.asyncio
async def test_connection_manager_broadcast():
    """Broadcast sends to all users in a room except the sender."""
    from app.core.ws_manager import ConnectionManager
    
    manager = ConnectionManager()
    task_id = uuid4()
    sender_id = uuid4()
    receiver_id = uuid4()
    
    received_messages = []
    
    class FakeWebSocket:
        async def accept(self):
            pass
        async def send_json(self, data):
            received_messages.append(data)
    
    ws_sender = FakeWebSocket()
    ws_receiver = FakeWebSocket()
    
    await manager.connect(task_id, sender_id, ws_sender)
    await manager.connect(task_id, receiver_id, ws_receiver)
    
    await manager.broadcast_to_task(
        task_id, {"content": "hello"}, exclude_sender=sender_id
    )
    
    # Only receiver should have gotten the message
    assert len(received_messages) == 1
    assert received_messages[0]["content"] == "hello"
    
    # Cleanup
    manager.disconnect(task_id, sender_id)
    manager.disconnect(task_id, receiver_id)
