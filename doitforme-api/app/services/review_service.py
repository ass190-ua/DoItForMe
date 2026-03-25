from uuid import UUID
from typing import Sequence
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.review import Review
from app.models.task import TaskStatus
from app.repositories.review_repository import ReviewRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.schemas.reviews import ReviewCreateRequest, ReviewPublic

class ReviewService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.review_repository = ReviewRepository(session)
        self.task_repository = TaskRepository(session)
        self.user_repository = UserRepository(session)

    async def create_review(
        self,
        current_user: dict[str, str],
        data: ReviewCreateRequest,
    ) -> ReviewPublic:
        reviewer_id = UUID(current_user["sub"])
        
        task = await self.task_repository.get_by_id(data.task_id)
        if not task:
            raise AppException(
                code="NOT_FOUND", message="Task not found", status_code=404
            )
            
        if task.status != TaskStatus.COMPLETED:
            raise AppException(
                code="INVALID_STATE", 
                message="Reviews can only be created for completed tasks", 
                status_code=400
            )

        if reviewer_id not in (task.creator_id, task.runner_id):
            raise AppException(
                code="FORBIDDEN_RULE", 
                message="Only the task creator or runner can leave a review", 
                status_code=403
            )
            
        expected_reviewee = task.runner_id if reviewer_id == task.creator_id else task.creator_id
        if data.reviewee_id != expected_reviewee:
            raise AppException(
                code="INVALID_REVIEWEE", 
                message="The reviewee_id does not match the other party of this task", 
                status_code=400
            )

        existing_review = await self.review_repository.get_by_task_and_reviewer(task.task_id, reviewer_id)
        if existing_review:
            raise AppException(
                code="DUPLICATE_REVIEW", 
                message="You have already reviewed this task", 
                status_code=400
            )
            
        review = Review(
            task_id=data.task_id,
            reviewer_id=reviewer_id,
            reviewee_id=data.reviewee_id,
            rating=data.rating,
            comment=data.comment
        )
        
        created_review = await self.review_repository.create(review)
        
        user = await self.user_repository.get_for_update(data.reviewee_id)
        if not user:
            raise AppException(
                code="NOT_FOUND", message="Reviewee user not found", status_code=404
            )
            
        old_rating = float(user.rating)
        old_count = user.rating_count
        
        if old_count == 0:
            new_rating = float(data.rating)
        else:
            new_rating = ((old_rating * old_count) + data.rating) / (old_count + 1)
            
        user.rating = Decimal(str(round(new_rating, 2)))
        user.rating_count += 1
        
        await self.session.commit()
        return ReviewPublic.model_validate(created_review)

    async def get_user_reviews(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> Sequence[ReviewPublic]:
        reviews = await self.review_repository.get_by_user(user_id, limit=limit, offset=offset)
        return [ReviewPublic.model_validate(r) for r in reviews]
