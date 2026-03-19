from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.exceptions import AppException
from app.schemas.tasks import TaskCreateRequest
from app.services.task_service import TaskService


class StubSession:
    def __init__(self) -> None:
        self.commit_called = False

    async def commit(self) -> None:
        self.commit_called = True


class StubTaskRepository:
    def __init__(self) -> None:
        self.created_task = None

    async def create(self, task):
        if getattr(task, "task_id", None) is None:
            task.task_id = uuid4()
        if getattr(task, "created_at", None) is None:
            task.created_at = datetime.now(UTC)
        self.created_task = task
        return task


@pytest.mark.asyncio
async def test_create_task_creates_open_task_for_poster():
    session = StubSession()
    service = TaskService(session=session)
    service.task_repository = StubTaskRepository()

    task = await service.create_task(
        {
            "sub": str(uuid4()),
            "email": "poster@example.com",
            "role": "poster",
            "jti": "task-session",
        },
        TaskCreateRequest(
            title="Pick up dry cleaning",
            description="Get my suit from the cleaner",
            location={"latitude": Decimal("40.7128"), "longitude": Decimal("-74.0060")},
            initial_price=Decimal("15.00"),
            category="errand",
        ),
    )

    assert service.task_repository.created_task is not None
    assert service.task_repository.created_task.status.value == "open"
    assert session.commit_called is True
    assert task.title == "Pick up dry cleaning"
    assert task.status == "open"
    assert task.location.latitude == Decimal("40.7128")
    assert task.initial_price == Decimal("15.00")


@pytest.mark.asyncio
async def test_create_task_rejects_non_poster_role():
    session = StubSession()
    service = TaskService(session=session)
    service.task_repository = StubTaskRepository()

    with pytest.raises(AppException) as exc_info:
        await service.create_task(
            {
                "sub": str(uuid4()),
                "email": "performer@example.com",
                "role": "performer",
                "jti": "task-session",
            },
            TaskCreateRequest(
                title="Pick up groceries",
                description="Get milk and bread",
                location={
                    "latitude": Decimal("40.7128"),
                    "longitude": Decimal("-74.0060"),
                },
                initial_price=Decimal("12.00"),
            ),
        )

    assert exc_info.value.code == "FORBIDDEN_ROLE"
    assert exc_info.value.status_code == 403
    assert session.commit_called is False
