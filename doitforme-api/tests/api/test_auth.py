import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app as fastapi_app


class TestRegisterValidation:
    client = TestClient(fastapi_app)

    def test_register_invalid_email(self):
        payload = {
            "email": "not-an-email",
            "password": "securepassword123",
            "name": "Test User",
            "role": "poster",
        }
        response = self.client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_register_missing_required_fields(self):
        payload = {"email": "some@example.com"}
        response = self.client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_register_weak_password(self):
        payload = {
            "email": "weakpass@example.com",
            "password": "short",
            "name": "Test User",
            "role": "poster",
        }
        response = self.client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_register_unsupported_role(self):
        payload = {
            "email": "adminattempt@example.com",
            "password": "securepassword123",
            "name": "Admin Attempt",
            "role": "admin",
        }
        response = self.client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.skip(reason="requires live PostgreSQL database")
@pytest.mark.asyncio
async def test_register_success(async_client: AsyncClient):
    payload = {
        "email": "testuser@example.com",
        "password": "securepassword123",
        "name": "Test User",
        "role": "poster",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["user"]["email"] == "testuser@example.com"
    assert body["data"]["user"]["name"] == "Test User"
    assert body["data"]["user"]["role"] == "poster"
    assert "password_hash" not in body["data"]["user"]
    assert "password" not in body["data"]["user"]
    assert body["error"] is None


@pytest.mark.skip(reason="requires live PostgreSQL database")
@pytest.mark.asyncio
async def test_register_duplicate_email(async_client: AsyncClient, session):
    existing = User(
        email="existing@example.com",
        password_hash=hash_password("existingpassword"),
        name="Existing User",
        role=UserRole.PERFORMER,
    )
    repo = UserRepository(session)
    await repo.create(existing)
    await session.commit()

    payload = {
        "email": "existing@example.com",
        "password": "anotherpassword123",
        "name": "Another User",
        "role": "poster",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 409
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "EMAIL_ALREADY_EXISTS"


@pytest.mark.skip(reason="requires live PostgreSQL database")
@pytest.mark.asyncio
async def test_register_role_performer(async_client: AsyncClient):
    payload = {
        "email": "performer@example.com",
        "password": "securepassword123",
        "name": "Performer User",
        "role": "performer",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["user"]["role"] == "performer"


from app.core.security import hash_password
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
