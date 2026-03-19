from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.task import Task, TaskStatus
from app.repositories.task_repository import TaskRepository
from app.schemas.tasks import TaskCreateRequest, TaskLocation, TaskPublic


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.task_repository = TaskRepository(session)

    async def create_task(
        self,
        current_user: dict[str, str],
        data: TaskCreateRequest,
    ) -> TaskPublic:
        if current_user["role"] != "poster":
            raise AppException(
                code="FORBIDDEN_ROLE",
                message="Only posters can create tasks",
                status_code=403,
            )

        task = Task(
            title=data.title,
            description=data.description,
            created_by=UUID(current_user["sub"]),
            status=TaskStatus.OPEN,
            latitude=data.location.latitude,
            longitude=data.location.longitude,
            category=data.category,
            initial_price=data.initial_price,
        )

        created_task = await self.task_repository.create(task)
        await self.session.commit()
        return TaskPublic(
            task_id=created_task.task_id,
            title=created_task.title,
            description=created_task.description,
            location=TaskLocation(
                latitude=created_task.latitude,
                longitude=created_task.longitude,
            ),
            initial_price=created_task.initial_price,
            category=created_task.category,
            status=created_task.status.value,
            created_by=created_task.created_by,
            created_at=created_task.created_at,
        )
