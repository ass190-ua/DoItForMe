from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.exceptions import AppException
from app.models.task import Task
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

    async def update(self, task):
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
            location_lat=Decimal("40.7128"),
            location_lng=Decimal("-74.0060"),
            address="123 Clean St",
            initial_offer=Decimal("15.00"),
            category="errand",
        ),
    )

    assert service.task_repository.created_task is not None
    assert service.task_repository.created_task.status.value == "published"
    assert session.commit_called is True
    assert task.title == "Pick up dry cleaning"
    assert task.status == "published"
    assert task.location_lat == Decimal("40.7128")
    assert task.initial_offer == Decimal("15.00")


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
                location_lat=Decimal("40.7128"),
                location_lng=Decimal("-74.0060"),
                address="123 Grocery St",
                initial_offer=Decimal("12.00"),
            ),
        )

    assert exc_info.value.code == "FORBIDDEN_ROLE"
    assert exc_info.value.status_code == 403
    assert session.commit_called is False


@pytest.mark.asyncio
async def test_start_task_success():
    session = StubSession()
    service = TaskService(session=session)
    service.task_repository = StubTaskRepository()
    
    task_id = uuid4()
    runner_id = uuid4()
    
    mock_task = Task(
        task_id=task_id,
        creator_id=uuid4(),
        runner_id=runner_id,
        status="accepted",
        title="Test Task",
        description="Just a test",
        location_lat=Decimal("0"),
        location_lng=Decimal("0"),
        address="123 Test",
        initial_offer=Decimal("10"),
        created_at=datetime.now(UTC)
    )
    
    # Overriding the get_by_id in the stub
    async def mock_get_by_id(tid):
        return mock_task
    service.task_repository.get_by_id = mock_get_by_id
    
    current_user = {"sub": str(runner_id)}
    
    # Call the service method
    result = await service.start_task(current_user, task_id)
    
    assert result.status == "in_progress"
    assert mock_task.status == "in_progress"
    assert session.commit_called is True


@pytest.mark.asyncio
async def test_complete_task_success():
    session = StubSession()
    service = TaskService(session=session)
    service.task_repository = StubTaskRepository()
    
    task_id = uuid4()
    creator_id = uuid4()
    runner_id = uuid4()
    
    mock_task = Task(
        task_id=task_id,
        creator_id=creator_id,
        runner_id=runner_id,
        status="in_progress",
        title="Test Task",
        description="Just a test",
        location_lat=Decimal("0"),
        location_lng=Decimal("0"),
        address="123 Test",
        initial_offer=Decimal("10"),
        accepted_price=Decimal("10"),
        created_at=datetime.now(UTC)
    )
    
    async def mock_get_by_id(tid):
        return mock_task
    service.task_repository.get_by_id = mock_get_by_id

    # Stub user repository (for escrow release)
    mock_runner = SimpleNamespace(
        user_id=runner_id,
        balance=Decimal("0.00"),
    )
    
    class StubUserRepo:
        async def get_for_update(self, uid):
            return mock_runner
        async def update(self, user):
            return user
    service.user_repository = StubUserRepo()

    # Stub transaction repository
    class StubTxRepo:
        async def create(self, tx):
            tx.id = uuid4()
            return tx
    service.transaction_repository = StubTxRepo()
    
    current_user = {"sub": str(creator_id)}
    
    result = await service.complete_task(current_user, task_id)
    
    assert result.status == "completed"
    assert mock_task.status == "completed"
    assert mock_runner.balance == Decimal("10.00")
    assert session.commit_called is True
