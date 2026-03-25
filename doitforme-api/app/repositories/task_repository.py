from uuid import UUID
from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, task: Task) -> Task:
        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def get_by_id(self, task_id: UUID) -> Task | None:
        result = await self.session.execute(
            select(Task).where(Task.task_id == task_id)
        )
        return result.scalar_one_or_none()

    async def get_available_tasks(
        self, 
        exclude_user_id: UUID,
        user_lat: float,
        user_lng: float,
        radius_km: float = 5.0,
        category: str | None = None,
        sort_by: str = "distance",
        limit: int = 20,
        offset: int = 0
    ) -> Sequence[tuple[Task, float]]:
        # Haversine spatial SQL computation
        acos_args = (
            func.cos(func.radians(user_lat)) *
            func.cos(func.radians(Task.location_lat)) *
            func.cos(func.radians(Task.location_lng) - func.radians(user_lng)) +
            func.sin(func.radians(user_lat)) *
            func.sin(func.radians(Task.location_lat))
        )
        safe_acos_args = func.greatest(-1.0, func.least(1.0, acos_args))
        distance_expr = (6371.0 * func.acos(safe_acos_args)).label("distance")

        stmt = select(Task, distance_expr).where(
            Task.status == TaskStatus.PUBLISHED,
            Task.creator_id != exclude_user_id,
            distance_expr <= radius_km
        ).limit(limit).offset(offset)
        
        if category:
            stmt = stmt.where(Task.category == category)
            
        if sort_by == "distance":
            stmt = stmt.order_by(distance_expr.asc())
        elif sort_by == "price_desc":
            stmt = stmt.order_by(Task.initial_offer.desc())
        elif sort_by == "recent":
            stmt = stmt.order_by(Task.created_at.desc())
        else:
            stmt = stmt.order_by(distance_expr.asc())

        result = await self.session.execute(stmt)
        return result.all()

    async def get_user_tasks(
        self, 
        user_id: UUID, 
        role: str = "creator", 
        limit: int = 20, 
        offset: int = 0
    ) -> Sequence[Task]:
        stmt = select(Task).limit(limit).offset(offset)
        if role == "creator":
            stmt = stmt.where(Task.creator_id == user_id)
        else:
            stmt = stmt.where(Task.performer_id == user_id)
        
        stmt = stmt.order_by(Task.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, task: Task) -> Task:
        # Assuming task is already attached to the session
        await self.session.flush()
        await self.session.refresh(task)
        return task
