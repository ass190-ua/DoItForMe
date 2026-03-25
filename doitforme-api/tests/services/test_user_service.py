from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.exceptions import AppException
from app.models.user import UserRole
from app.schemas.users import SelfProfileUpdateRequest
from app.services.user_service import UserService


class StubSession:
    def __init__(self) -> None:
        self.commit_called = False

    async def commit(self) -> None:
        self.commit_called = True


class StubUserRepository:
    def __init__(self, user) -> None:
        self.user = user
        self.updated_with = None

    async def get_by_id(self, user_id):
        if self.user is not None and self.user.user_id == user_id:
            return self.user
        return None

    async def update_profile(self, user, *, name, latitude, longitude):
        user.name = name
        user.latitude = latitude
        user.longitude = longitude
        self.updated_with = {
            "name": name,
            "latitude": latitude,
            "longitude": longitude,
        }
        return user


def build_user():
    now = datetime.now(UTC)
    return SimpleNamespace(
        user_id=uuid4(),
        email="profile@example.com",
        name="Profile User",
        role=UserRole.POSTER,
        latitude=Decimal("40.41680000"),
        longitude=Decimal("-3.70380000"),
        balance=Decimal("100.00"),
        rating=Decimal("4.75"),
        completed_tasks_count=12,
        rating_count=9,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_get_self_profile_returns_profile():
    user = build_user()
    service = UserService(session=StubSession())
    service.user_repository = StubUserRepository(user)

    profile = await service.get_self_profile(user.user_id)

    assert profile.user_id == user.user_id
    assert profile.email == "profile@example.com"
    assert profile.name == "Profile User"
    assert profile.role == "poster"
    assert profile.rating == Decimal("4.75")
    assert profile.completed_tasks_count == 12


@pytest.mark.asyncio
async def test_get_public_profile_returns_trust_fields_only():
    user = build_user()
    service = UserService(session=StubSession())
    service.user_repository = StubUserRepository(user)

    profile = await service.get_public_profile(user.user_id)

    assert profile.user_id == user.user_id
    assert profile.name == "Profile User"
    assert profile.role == "poster"
    assert profile.rating == Decimal("4.75")
    assert profile.completed_tasks_count == 12
    assert profile.rating_count == 9
    assert not hasattr(profile, "email")
    assert not hasattr(profile, "latitude")
    assert not hasattr(profile, "longitude")


@pytest.mark.asyncio
async def test_get_self_profile_rejects_missing_user():
    service = UserService(session=StubSession())
    service.user_repository = StubUserRepository(None)

    with pytest.raises(AppException) as exc_info:
        await service.get_self_profile(uuid4())

    assert exc_info.value.code == "USER_NOT_FOUND"
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_public_profile_rejects_missing_user():
    service = UserService(session=StubSession())
    service.user_repository = StubUserRepository(None)

    with pytest.raises(AppException) as exc_info:
        await service.get_public_profile(uuid4())

    assert exc_info.value.code == "USER_NOT_FOUND"
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_update_self_profile_updates_editable_fields_only():
    user = build_user()
    session = StubSession()
    service = UserService(session=session)
    service.user_repository = StubUserRepository(user)

    profile = await service.update_self_profile(
        user.user_id,
        SelfProfileUpdateRequest(
            name="Updated User",
            latitude=Decimal("41.38740000"),
            longitude=Decimal("2.16860000"),
        ),
    )

    assert service.user_repository.updated_with == {
        "name": "Updated User",
        "latitude": Decimal("41.38740000"),
        "longitude": Decimal("2.16860000"),
    }
    assert session.commit_called is True
    assert profile.name == "Updated User"
    assert profile.email == "profile@example.com"
    assert profile.role == "poster"


@pytest.mark.asyncio
async def test_update_self_profile_rejects_missing_user():
    session = StubSession()
    service = UserService(session=session)
    service.user_repository = StubUserRepository(None)

    with pytest.raises(AppException) as exc_info:
        await service.update_self_profile(
            uuid4(),
            SelfProfileUpdateRequest(
                name="Updated User",
                latitude=Decimal("41.38740000"),
                longitude=Decimal("2.16860000"),
            ),
        )

    assert exc_info.value.code == "USER_NOT_FOUND"
    assert exc_info.value.status_code == 404
    assert session.commit_called is False
