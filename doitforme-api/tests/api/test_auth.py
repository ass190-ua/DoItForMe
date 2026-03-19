from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.core.security import create_access_token, hash_password, hash_token
from app.main import app as fastapi_app
from app.models.auth_session import AuthSession
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.services import auth_service as auth_service_module


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


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient, session, monkeypatch):
    existing = User(
        email="login@example.com",
        password_hash="stored-hash",
        name="Login User",
        role=UserRole.POSTER,
    )
    monkeypatch.setattr(
        auth_service_module,
        "verify_password",
        lambda plain, hashed: plain == "securepassword123" and hashed == "stored-hash",
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


@pytest.mark.asyncio
async def test_login_invalid_credentials(
    async_client: AsyncClient, session, monkeypatch
):
    existing = User(
        email="existing-login@example.com",
        password_hash="stored-hash",
        name="Existing Login User",
        role=UserRole.PERFORMER,
    )
    monkeypatch.setattr(
        auth_service_module,
        "verify_password",
        lambda plain, hashed: plain == "rightpassword123" and hashed == "stored-hash",
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


@pytest.mark.asyncio
async def test_login_invalid_payload(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "not-an-email", "password": "securepassword123"},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_logout_rejects_expired_session(async_client: AsyncClient, session):
    existing = User(
        email="expired-session@example.com",
        password_hash="stored-hash",
        name="Expired Session User",
        role=UserRole.POSTER,
    )
    repo = UserRepository(session)
    created_user = await repo.create(existing)
    await session.flush()

    access_jti = "expired-access-jti"
    access_token = create_access_token(
        subject=str(created_user.user_id),
        email=created_user.email,
        role=created_user.role.value,
        token_type="access",
        token_id=access_jti,
        expires_delta=timedelta(minutes=5),
    )
    expired_session = AuthSession(
        user_id=created_user.user_id,
        access_jti=access_jti,
        refresh_jti="expired-refresh-jti",
        refresh_token_hash=hash_token("expired-refresh-token"),
        expires_at=datetime.now(UTC) - timedelta(minutes=1),
    )
    session.add(expired_session)
    await session.commit()

    response = await async_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_TOKEN"
    assert body["error"]["message"] == "Session is no longer active"
