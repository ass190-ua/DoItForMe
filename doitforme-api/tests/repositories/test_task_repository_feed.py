import pytest
import os
from decimal import Decimal
from datetime import datetime, UTC
from uuid import uuid4

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.repositories.task_repository import TaskRepository
from app.db.base import Base

TEST_DB_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/doitforme_test")

@pytest.fixture
async def test_session():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
    async with SessionLocal() as session:
        yield session
        
    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_get_available_tasks_spatial_filtering(test_session):
    repo = TaskRepository(test_session)
    
    # 1. Create a mock user
    user_id = uuid4()
    user = User(
        user_id=user_id,
        email="creator@example.com",
        password_hash="hash",
        name="Creator",
        role="poster"
    )
    test_session.add(user)
    await test_session.flush()

    searcher_id = uuid4()
    
    # 2. Add tasks at different locations
    # Madrid Center (Search Origin: 40.4168, -3.7038)
    # Task 1: 1km away (Legazpi approx: 40.3917, -3.6974 -> 2.8km)
    task_near = Task(
        task_id=uuid4(),
        title="Near Task",
        description="Close to center",
        creator_id=user_id,
        status=TaskStatus.PUBLISHED,
        location_lat=Decimal("40.3917"),
        location_lng=Decimal("-3.6974"),
        address="Legazpi",
        initial_offer=Decimal("10.0"),
    )
    
    # Task 2: 20km away (Alcala de Henares approx: 40.4820, -3.3590 -> 30km)
    task_far = Task(
        task_id=uuid4(),
        title="Far Task",
        description="Far from center",
        creator_id=user_id,
        status=TaskStatus.PUBLISHED,
        location_lat=Decimal("40.4820"),
        location_lng=Decimal("-3.3590"),
        address="Alcala",
        initial_offer=Decimal("20.0"),
    )
    
    test_session.add_all([task_near, task_far])
    await test_session.commit()
    
    # Search with 5km radius from Sol (40.4168, -3.7038)
    results = await repo.get_available_tasks(
        exclude_user_id=searcher_id,
        user_lat=40.4168,
        user_lng=-3.7038,
        radius_km=5.0
    )
    
    # Assert
    assert len(results) == 1
    task_out, dist = results[0]
    assert task_out.title == "Near Task"
    assert dist <= 5.0
    
    # Search with 50km radius
    results_50 = await repo.get_available_tasks(
        exclude_user_id=searcher_id,
        user_lat=40.4168,
        user_lng=-3.7038,
        radius_km=50.0
    )
    assert len(results_50) == 2
