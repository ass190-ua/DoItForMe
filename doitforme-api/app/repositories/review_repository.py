from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review

class ReviewRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, review: Review) -> Review:
        self.session.add(review)
        await self.session.flush()
        await self.session.refresh(review)
        return review

    async def get_by_task_and_reviewer(self, task_id: UUID, reviewer_id: UUID) -> Review | None:
        result = await self.session.execute(
            select(Review).where(
                Review.task_id == task_id,
                Review.reviewer_id == reviewer_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, reviewee_id: UUID, limit: int = 20, offset: int = 0) -> Sequence[Review]:
        result = await self.session.execute(
            select(Review).where(Review.reviewee_id == reviewee_id)
            .limit(limit).offset(offset)
            .order_by(Review.created_at.desc())
        )
        return result.scalars().all()
