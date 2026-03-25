from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.api.deps import db_session_dependency, require_authenticated_user
from app.core.exceptions import AppException
from app.main import app as fastapi_app
from app.schemas.users import PublicProfile, SelfProfile
from app.services.user_service import UserService


class DummySession:
    pass


def override_authenticated_user():
    return {
        "sub": "00000000-0000-0000-0000-000000000001",
        "email": "me@example.com",
        "role": "poster",
        "jti": "session-jti",
    }


async def override_db_session():
    yield DummySession()


def make_self_profile(
    *,
    user_id: UUID,
    email: str,
    name: str,
    role: str,
    latitude: Decimal | None,
    longitude: Decimal | None,
    balance: Decimal,
    rating: Decimal,
    completed_tasks_count: int,
    rating_count: int,
) -> SelfProfile:
    now = datetime.now().astimezone()
    return SelfProfile(
        user_id=user_id,
        email=email,
        name=name,
        role=role,
        latitude=latitude,
        longitude=longitude,
        balance=balance,
        rating=rating,
        completed_tasks_count=completed_tasks_count,
        rating_count=rating_count,
        created_at=now,
        updated_at=now,
    )


def make_public_profile(
    *,
    user_id: UUID,
    name: str,
    role: str,
    rating: Decimal,
    completed_tasks_count: int,
    rating_count: int,
) -> PublicProfile:
    return PublicProfile(
        user_id=user_id,
        name=name,
        role=role,
        rating=rating,
        completed_tasks_count=completed_tasks_count,
        rating_count=rating_count,
    )


class TestUsersAuthValidation:
    client = TestClient(fastapi_app)

    def test_get_my_profile_requires_authorization(self):
        response = self.client.get("/api/v1/users/me")

        assert response.status_code == 401
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "AUTHENTICATION_REQUIRED"

    def test_update_my_profile_requires_authorization(self):
        response = self.client.put(
            "/api/v1/users/me",
            json={
                "name": "Updated User",
                "latitude": 41.3874,
                "longitude": 2.1686,
            },
        )

        assert response.status_code == 401
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "AUTHENTICATION_REQUIRED"

    def test_update_my_profile_rejects_invalid_payload(self):
        fastapi_app.dependency_overrides[require_authenticated_user] = (
            override_authenticated_user
        )
        fastapi_app.dependency_overrides[db_session_dependency] = override_db_session

        try:
            response = self.client.put(
                "/api/v1/users/me",
                json={
                    "name": "",
                    "latitude": 120,
                    "longitude": 2.1686,
                    "role": "admin",
                },
            )
        finally:
            fastapi_app.dependency_overrides.clear()

        assert response.status_code == 422
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"


class TestPublicProfileValidation:
    client = TestClient(fastapi_app)

    def test_get_public_profile_rejects_invalid_uuid(self):
        response = self.client.get("/api/v1/users/not-a-uuid")

        assert response.status_code == 422
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_get_my_profile_success(async_client: AsyncClient, monkeypatch):
    user_id = uuid4()
    fastapi_app.dependency_overrides[require_authenticated_user] = lambda: {
        "sub": str(user_id),
        "email": "profile-self@example.com",
        "role": "poster",
        "jti": "profile-self-jti",
    }
    fastapi_app.dependency_overrides[db_session_dependency] = override_db_session

    async def fake_get_self_profile(self, current_user_id):
        assert current_user_id == user_id
        return make_self_profile(
            user_id=user_id,
            email="profile-self@example.com",
            name="Profile Self User",
            role="poster",
            latitude=Decimal("40.41680000"),
            longitude=Decimal("-3.70380000"),
            balance=Decimal("100.00"),
            rating=Decimal("4.75"),
            completed_tasks_count=12,
            rating_count=9,
        )

    monkeypatch.setattr(UserService, "get_self_profile", fake_get_self_profile)

    try:
        response = await async_client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer ignored-by-override"},
        )
    finally:
        fastapi_app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["profile"]["user_id"] == str(user_id)
    assert body["data"]["profile"]["email"] == "profile-self@example.com"
    assert body["data"]["profile"]["name"] == "Profile Self User"
    assert body["data"]["profile"]["role"] == "poster"
    assert body["data"]["profile"]["rating"] == "4.75"
    assert body["data"]["profile"]["completed_tasks_count"] == 12
    assert body["data"]["profile"]["rating_count"] == 9
    assert body["error"] is None


@pytest.mark.asyncio
async def test_update_my_profile_success(async_client: AsyncClient, monkeypatch):
    user_id = uuid4()
    fastapi_app.dependency_overrides[require_authenticated_user] = lambda: {
        "sub": str(user_id),
        "email": "profile-update@example.com",
        "role": "poster",
        "jti": "profile-update-jti",
    }
    fastapi_app.dependency_overrides[db_session_dependency] = override_db_session

    async def fake_update_self_profile(self, current_user_id, data):
        assert current_user_id == user_id
        assert data.name == "Updated Name"
        return make_self_profile(
            user_id=user_id,
            email="profile-update@example.com",
            name=data.name,
            role="poster",
            latitude=data.latitude,
            longitude=data.longitude,
            balance=Decimal("0.00"),
            rating=Decimal("5.00"),
            completed_tasks_count=0,
            rating_count=0,
        )

    monkeypatch.setattr(UserService, "update_self_profile", fake_update_self_profile)

    try:
        response = await async_client.put(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer ignored-by-override"},
            json={
                "name": "Updated Name",
                "latitude": 41.3874,
                "longitude": 2.1686,
            },
        )
    finally:
        fastapi_app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["profile"]["user_id"] == str(user_id)
    assert body["data"]["profile"]["email"] == "profile-update@example.com"
    assert body["data"]["profile"]["name"] == "Updated Name"
    assert body["data"]["profile"]["role"] == "poster"
    assert body["data"]["profile"]["latitude"] == "41.3874"
    assert body["data"]["profile"]["longitude"] == "2.1686"
    assert body["error"] is None


@pytest.mark.asyncio
async def test_update_my_profile_ignores_attempted_identity_override(
    async_client: AsyncClient, monkeypatch
):
    owner_id = uuid4()
    other_user_id = uuid4()
    fastapi_app.dependency_overrides[require_authenticated_user] = lambda: {
        "sub": str(owner_id),
        "email": "owner@example.com",
        "role": "poster",
        "jti": "owner-profile-jti",
    }
    fastapi_app.dependency_overrides[db_session_dependency] = override_db_session

    async def fake_update_self_profile(self, current_user_id, data):
        assert current_user_id == owner_id
        return make_self_profile(
            user_id=current_user_id,
            email="owner@example.com",
            name=data.name,
            role="poster",
            latitude=data.latitude,
            longitude=data.longitude,
            balance=Decimal("0.00"),
            rating=Decimal("5.00"),
            completed_tasks_count=0,
            rating_count=0,
        )

    monkeypatch.setattr(UserService, "update_self_profile", fake_update_self_profile)

    try:
        response = await async_client.put(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer ignored-by-override"},
            json={
                "name": "Owner Updated",
                "latitude": 41.3874,
                "longitude": 2.1686,
                "user_id": str(other_user_id),
            },
        )
    finally:
        fastapi_app.dependency_overrides.clear()

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_get_public_profile_success(async_client: AsyncClient, monkeypatch):
    user_id = uuid4()
    fastapi_app.dependency_overrides[db_session_dependency] = override_db_session

    async def fake_get_public_profile(self, requested_user_id):
        assert requested_user_id == user_id
        return make_public_profile(
            user_id=user_id,
            name="Public Profile User",
            role="performer",
            rating=Decimal("4.80"),
            completed_tasks_count=18,
            rating_count=11,
        )

    monkeypatch.setattr(UserService, "get_public_profile", fake_get_public_profile)

    try:
        response = await async_client.get(f"/api/v1/users/{user_id}")
    finally:
        fastapi_app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["profile"] == {
        "user_id": str(user_id),
        "name": "Public Profile User",
        "role": "performer",
        "rating": "4.80",
        "completed_tasks_count": 18,
        "rating_count": 11,
    }
    assert "email" not in body["data"]["profile"]
    assert "latitude" not in body["data"]["profile"]
    assert "longitude" not in body["data"]["profile"]
    assert body["error"] is None


@pytest.mark.asyncio
async def test_get_public_profile_not_found(async_client: AsyncClient, monkeypatch):
    fastapi_app.dependency_overrides[db_session_dependency] = override_db_session

    async def fake_get_public_profile(self, requested_user_id):
        raise AppException(
            code="USER_NOT_FOUND",
            message="User profile was not found",
            status_code=404,
        )

    monkeypatch.setattr(UserService, "get_public_profile", fake_get_public_profile)

    try:
        response = await async_client.get(
            "/api/v1/users/00000000-0000-0000-0000-000000000099"
        )
    finally:
        fastapi_app.dependency_overrides.clear()

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "USER_NOT_FOUND"
    assert body["error"]["message"] == "User profile was not found"
