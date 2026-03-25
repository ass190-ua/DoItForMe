import pytest
from uuid import uuid4
from decimal import Decimal

from app.services.review_service import ReviewService
from app.schemas.reviews import ReviewCreateRequest
from app.models.task import Task, TaskStatus
from app.models.user import User


class StubSession:
    def __init__(self):
        self.commit_called = False
    
    async def commit(self):
        self.commit_called = True


class StubReviewRepository:
    async def create(self, review):
        from datetime import datetime
        review.id = uuid4()
        review.created_at = datetime.now()
        return review
    
    async def get_by_task_and_reviewer(self, task_id, reviewer_id):
        return None


class StubTaskRepository:
    def __init__(self, task):
        self.task = task
        
    async def get_by_id(self, task_id):
        return self.task


class StubUserRepository:
    def __init__(self, user):
        self.user = user
        
    async def get_by_id(self, user_id):
        return self.user


@pytest.mark.asyncio
async def test_create_review_updates_user_rating():
    session = StubSession()
    service = ReviewService(session)
    
    task_id = uuid4()
    creator_id = uuid4()
    runner_id = uuid4()
    
    # Setup mock task
    task = Task(
        task_id=task_id,
        creator_id=creator_id,
        runner_id=runner_id,
        status=TaskStatus.COMPLETED
    )
    
    # Setup mock user (Reviewee)
    user = User(
        user_id=runner_id,
        rating=Decimal("4.00"),
        rating_count=2
    )
    
    service.review_repository = StubReviewRepository()
    service.task_repository = StubTaskRepository(task)
    service.user_repository = StubUserRepository(user)
    
    current_user = {"sub": str(creator_id)}
    data = ReviewCreateRequest(
        task_id=task_id,
        reviewee_id=runner_id,
        rating=5,
        comment="Great job!"
    )
    
    review_public = await service.create_review(current_user, data)
    
    assert review_public.rating == 5
    assert session.commit_called is True
    # (4.00 * 2 + 5) / 3 = 13 / 3 = 4.333... -> 4.33
    assert user.rating == Decimal("4.33")
    assert user.rating_count == 3
