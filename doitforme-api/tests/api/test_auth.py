import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.core.security import hash_password
from app.main import app as fastapi_app
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository


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


class TestLoginValidation:
    client = TestClient(fastapi_app)

    def test_login_invalid_email(self):
        payload = {"email": "not-an-email", "password": "securepassword123"}
        response = self.client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 422
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"


class TestLogoutValidation:
    client = TestClient(fastapi_app)

    def test_logout_requires_authorization_header(self):
        response = self.client.post("/api/v1/auth/logout")

        assert response.status_code == 401
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "AUTHENTICATION_REQUIRED"

    def test_logout_rejects_invalid_auth_header(self):
        response = self.client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Token something"},
        )

        assert response.status_code == 401
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "INVALID_AUTH_HEADER"

    def test_login_missing_required_fields(self):
        payload = {"email": "some@example.com"}
        response = self.client.post("/api/v1/auth/login", json=payload)

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


@pytest.mark.skip(reason="requires live PostgreSQL database")
@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient, session):
    existing = User(
        email="login@example.com",
        password_hash=hash_password("securepassword123"),
        name="Login User",
        role=UserRole.POSTER,
    )
    repo = UserRepository(session)
    await repo.create(existing)
    await session.commit()

    payload = {"email": "login@example.com", "password": "securepassword123"}
    response = await async_client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["user"]["email"] == "login@example.com"
    assert body["data"]["user"]["role"] == "poster"
    assert body["data"]["access_token"]
    assert body["data"]["refresh_token"]
    assert body["data"]["token_type"] == "bearer"
    assert body["error"] is None


@pytest.mark.skip(reason="requires live PostgreSQL database")
@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client: AsyncClient, session):
    existing = User(
        email="existing-login@example.com",
        password_hash=hash_password("rightpassword123"),
        name="Existing Login User",
        role=UserRole.PERFORMER,
    )
    repo = UserRepository(session)
    await repo.create(existing)
    await session.commit()

    bad_password_response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "existing-login@example.com",
            "password": "wrongpassword123",
        },
    )
    unknown_email_response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "missing-login@example.com",
            "password": "wrongpassword123",
        },
    )

    for response in (bad_password_response, unknown_email_response):
        assert response.status_code == 401
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "INVALID_CREDENTIALS"
        assert body["error"]["message"] == "Invalid email or password"
