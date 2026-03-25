from uuid import UUID
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.task import Task, TaskStatus
from app.models.transaction import Transaction, TransactionType
from app.repositories.task_repository import TaskRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.tasks import TaskCreateRequest, TaskPublic


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.task_repository = TaskRepository(session)
        self.user_repository = UserRepository(session)
        self.transaction_repository = TransactionRepository(session)

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
            creator_id=UUID(current_user["sub"]),
            status=TaskStatus.PUBLISHED,
            location_lat=data.location_lat,
            location_lng=data.location_lng,
            address=data.address,
            category=data.category,
            initial_offer=data.initial_offer,
        )

        created_task = await self.task_repository.create(task)
        await self.session.commit()
        return TaskPublic.model_validate(created_task)

    async def get_available_tasks(
        self,
        current_user: dict[str, str],
        lat: float,
        lng: float,
        radius_km: float,
        category: str | None,
        sort_by: str,
        limit: int = 20,
        offset: int = 0
    ) -> Sequence[TaskPublic]:
        user_id = UUID(current_user["sub"])
        rows = await self.task_repository.get_available_tasks(
            exclude_user_id=user_id,
            user_lat=lat,
            user_lng=lng,
            radius_km=radius_km,
            category=category,
            sort_by=sort_by,
            limit=limit,
            offset=offset
        )
        
        response = []
        for task, distance in rows:
            setattr(task, "distance_km", round(float(distance), 2))
            response.append(TaskPublic.model_validate(task))
            
        return response

    async def get_user_tasks(
        self,
        current_user: dict[str, str],
        role: str = "creator",
        limit: int = 20,
        offset: int = 0
    ) -> Sequence[TaskPublic]:
        user_id = UUID(current_user["sub"])
        tasks = await self.task_repository.get_user_tasks(
            user_id=user_id,
            role=role,
            limit=limit,
            offset=offset
        )
        return [TaskPublic.model_validate(task) for task in tasks]

    async def start_task(
        self,
        current_user: dict[str, str],
        task_id: UUID,
    ) -> TaskPublic:
        user_id = UUID(current_user["sub"])
        
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            raise AppException(
                code="NOT_FOUND", message="Task not found", status_code=404
            )
            
        if task.runner_id != user_id:
            raise AppException(
                code="FORBIDDEN_RULE", 
                message="Only the assigned runner can start this task", 
                status_code=403
            )
            
        if task.status != TaskStatus.ACCEPTED:
            raise AppException(
                code="INVALID_STATE", 
                message="Only accepted tasks can be started", 
                status_code=400
            )
            
        task.status = TaskStatus.IN_PROGRESS
        await self.task_repository.update(task)
        
        # Sprint 8: Notification Trigger
        from app.services.notification_service import NotificationService
        await NotificationService.notify_task_status_change(
            user_id=task.creator_id,
            task_title=task.title,
            new_status="EN PROGRESO",
            task_id=task.task_id
        )

        await self.session.commit()
        return TaskPublic.model_validate(task)

    async def complete_task(
        self,
        current_user: dict[str, str],
        task_id: UUID,
    ) -> TaskPublic:
        user_id = UUID(current_user["sub"])
        
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            raise AppException(
                code="NOT_FOUND", message="Task not found", status_code=404
            )
            
        if task.creator_id != user_id:
            raise AppException(
                code="FORBIDDEN_RULE", 
                message="Only the creator can mark this task as completed", 
                status_code=403
            )
            
        if task.status != TaskStatus.IN_PROGRESS:
            raise AppException(
                code="INVALID_STATE", 
                message="Only in-progress tasks can be completed", 
                status_code=400
            )

        # --- ESCROW RELEASE (atomic, same transaction) ---
        # 1. Lock runner row to prevent concurrent balance modifications
        runner = await self.user_repository.get_for_update(task.runner_id)

        # 2. Credit runner balance
        runner.balance += task.accepted_price
        await self.user_repository.update(runner)

        # 3. Record ESCROW_RELEASE transaction (positive amount)
        release_tx = Transaction(
            user_id=runner.user_id,
            amount=task.accepted_price,
            transaction_type=TransactionType.ESCROW_RELEASE,
            task_id=task.task_id,
        )
        await self.transaction_repository.create(release_tx)
        # --- END ESCROW RELEASE ---

        task.status = TaskStatus.COMPLETED
        
        await self.task_repository.update(task)

        # Sprint 8: Notification Trigger
        from app.services.notification_service import NotificationService
        await NotificationService.notify_task_status_change(
            user_id=task.runner_id,
            task_title=task.title,
            new_status="COMPLETADA",
            task_id=task.task_id
        )

        await self.session.commit()
        return TaskPublic.model_validate(task)

    async def cancel_task(
        self,
        current_user: dict[str, str],
        task_id: UUID,
    ) -> TaskPublic:
        user_id = UUID(current_user["sub"])
        
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            raise AppException(
                code="NOT_FOUND", message="Task not found", status_code=404
            )
            
        if task.creator_id != user_id:
            raise AppException(
                code="FORBIDDEN_RULE", 
                message="Only the creator can cancel this task", 
                status_code=403
            )

        return await self._execute_cancel(task)

    async def _execute_cancel(self, task: Task) -> TaskPublic:
        cancellable_states = (
            TaskStatus.PUBLISHED,
            TaskStatus.NEGOTIATING,
            TaskStatus.ACCEPTED,
            TaskStatus.IN_PROGRESS,
        )
        if task.status not in cancellable_states:
            raise AppException(
                code="INVALID_STATE",
                message="This task cannot be cancelled in its current state",
                status_code=400,
            )

        # --- ESCROW REFUND (only if money was held) ---
        if task.status in (TaskStatus.ACCEPTED, TaskStatus.IN_PROGRESS):
            # 1. Lock creator row
            creator = await self.user_repository.get_for_update(task.creator_id)

            # 2. Refund the accepted price back to creator
            creator.balance += task.accepted_price
            await self.user_repository.update(creator)

            # 3. Record ESCROW_REFUND transaction (positive for creator)
            refund_tx = Transaction(
                user_id=creator.user_id,
                amount=task.accepted_price,
                transaction_type=TransactionType.ESCROW_REFUND,
                task_id=task.task_id,
            )
            await self.transaction_repository.create(refund_tx)
        # --- END ESCROW REFUND ---

        task.status = TaskStatus.CANCELLED
        await self.task_repository.update(task)
        await self.session.commit()
        return TaskPublic.model_validate(task)

    async def admin_force_release_payment(self, task_id: UUID) -> TaskPublic:
        """Admin bypass to release escrow to the runner."""
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            raise AppException(
                code="NOT_FOUND", message="Task not found", status_code=404
            )
            
        if task.status != TaskStatus.IN_PROGRESS:
            raise AppException(
                code="INVALID_STATE", 
                message="Only in-progress tasks can have payments forced-released", 
                status_code=400
            )

        # Reuse release logic
        # Lock runner row
        runner = await self.user_repository.get_for_update(task.runner_id)
        runner.balance += task.accepted_price
        await self.user_repository.update(runner)

        release_tx = Transaction(
            user_id=runner.user_id,
            amount=task.accepted_price,
            transaction_type=TransactionType.ESCROW_RELEASE,
            task_id=task.task_id,
            # Note: could add a flag or comment that it was admin-forced
        )
        await self.transaction_repository.create(release_tx)
        
        task.status = TaskStatus.COMPLETED
        await self.task_repository.update(task)
        await self.session.commit()
        return TaskPublic.model_validate(task)

    async def admin_force_refund_payment(self, task_id: UUID) -> TaskPublic:
        """Admin bypass to refund escrow to the creator."""
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            raise AppException(
                code="NOT_FOUND", message="Task not found", status_code=404
            )
            
        return await self._execute_cancel(task)
