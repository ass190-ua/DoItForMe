from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.api.deps import db_session_dependency
from app.core.exceptions import AppException
from app.core.security import create_access_token, hash_password, hash_token
from app.main import app as fastapi_app
from app.models.user import UserRole
from app.repositories.auth_session_repository import AuthSessionRepository
from app.services import auth_service as auth_service_module
from app.services.auth_service import AuthService
from app.schemas.auth import LoginResponse, LogoutResponse, UserPublic


class DummySession:
    async def commit(self):
        return None


async def override_db_session():
    yield DummySession()


def build_access_token(*, subject: str, email: str, role: str, jti: str) -> str:
    return create_access_token(
        subject=subject,
        email=email,
        role=role,
        token_type="access",
        token_id=jti,
        expires_delta=timedelta(minutes=30),
    )


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
async def test_login_success(async_client: AsyncClient, monkeypatch):
    async def fake_login(self, data):
        return LoginResponse(
            user=UserPublic(
                user_id=uuid4(),
                email=data.email,
                name="Login User",
                role="poster",
            ),
            access_token="access-token",
            refresh_token="refresh-token",
        )

    monkeypatch.setattr(AuthService, "login", fake_login)

    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "securepassword123"},
    )

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
async def test_login_invalid_credentials(async_client: AsyncClient, monkeypatch):
    async def fake_login(self, data):
        raise AppException(
            code="INVALID_CREDENTIALS",
            message="Invalid email or password",
            status_code=401,
        )

    monkeypatch.setattr(AuthService, "login", fake_login)

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
async def test_logout_rejects_expired_session(async_client: AsyncClient, monkeypatch):
    fastapi_app.dependency_overrides[db_session_dependency] = override_db_session

    async def fake_get_active(self, access_jti):
        return None

    monkeypatch.setattr(
        AuthSessionRepository, "get_active_by_access_jti", fake_get_active
    )

    access_token = build_access_token(
        subject=str(uuid4()),
        email="expired-session@example.com",
        role="poster",
        jti="expired-access-jti",
    )

    try:
        response = await async_client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    finally:
        fastapi_app.dependency_overrides.clear()

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_TOKEN"
    assert body["error"]["message"] == "Session is no longer active"


@pytest.mark.asyncio
async def test_logout_success(async_client: AsyncClient, monkeypatch):
    fastapi_app.dependency_overrides[db_session_dependency] = override_db_session

    async def fake_get_active(self, access_jti):
        return SimpleNamespace(access_jti=access_jti)

    async def fake_revoke(self, access_jti):
        return SimpleNamespace(access_jti=access_jti, revoked_at=datetime.now(UTC))

    monkeypatch.setattr(
        AuthSessionRepository, "get_active_by_access_jti", fake_get_active
    )
    monkeypatch.setattr(AuthSessionRepository, "revoke_by_access_jti", fake_revoke)

    access_token = build_access_token(
        subject=str(uuid4()),
        email="logout-success@example.com",
        role="poster",
        jti="logout-success-jti",
    )

    try:
        response = await async_client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    finally:
        fastapi_app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"] == {"message": "Successfully logged out"}
    assert body["error"] is None


@pytest.mark.asyncio
async def test_logout_revoked_token_cannot_access_protected_route(
    async_client: AsyncClient, monkeypatch
):
    fastapi_app.dependency_overrides[db_session_dependency] = override_db_session
    active_sessions = {"logout-reuse-jti"}

    async def fake_get_active(self, access_jti):
        if access_jti in active_sessions:
            return SimpleNamespace(access_jti=access_jti)
        return None

    async def fake_revoke(self, access_jti):
        if access_jti in active_sessions:
            active_sessions.remove(access_jti)
            return SimpleNamespace(access_jti=access_jti, revoked_at=datetime.now(UTC))
        return None

    monkeypatch.setattr(
        AuthSessionRepository, "get_active_by_access_jti", fake_get_active
    )
    monkeypatch.setattr(AuthSessionRepository, "revoke_by_access_jti", fake_revoke)

    access_token = build_access_token(
        subject=str(uuid4()),
        email="logout-reuse@example.com",
        role="poster",
        jti="logout-reuse-jti",
    )

    try:
        logout_response = await async_client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert logout_response.status_code == 200

        profile_response = await async_client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    finally:
        fastapi_app.dependency_overrides.clear()

    assert profile_response.status_code == 401
    body = profile_response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_TOKEN"
    assert body["error"]["message"] == "Session is no longer active"
