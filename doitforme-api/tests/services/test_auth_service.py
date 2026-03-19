from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.exceptions import AppException
from app.core.security import decode_token
from app.models.user import UserRole
from app.schemas.auth import LoginRequest
from app.services import auth_service as auth_service_module
from app.services.auth_service import AuthService


def test_auth_service_initializes_with_session_stub():
    service = AuthService(session=None)  # type: ignore[arg-type]

    assert service.session is None
    assert service.user_repository is not None


class StubUserRepository:
    def __init__(self, user):
        self.user = user

    async def get_by_email(self, email: str):
        if self.user is not None and self.user.email == email:
            return self.user
        return None


@pytest.mark.asyncio
async def test_login_returns_user_and_tokens():
    user = SimpleNamespace(
        user_id=uuid4(),
        email="login@example.com",
        password_hash="stored-hash",
        name="Login User",
        role=UserRole.POSTER,
    )
    service = AuthService(session=None)  # type: ignore[arg-type]
    service.user_repository = StubUserRepository(user)

    original_verify_password = auth_service_module.verify_password
    auth_service_module.verify_password = lambda plain, hashed: (
        plain == "securepassword123" and hashed == "stored-hash"
    )

    try:
        result = await service.login(
            LoginRequest(email="login@example.com", password="securepassword123")
        )
    finally:
        auth_service_module.verify_password = original_verify_password

    assert result.user.email == "login@example.com"
    assert result.user.role == "poster"
    assert result.access_token
    assert result.refresh_token
    assert result.token_type == "bearer"

    access_payload = decode_token(result.access_token)
    refresh_payload = decode_token(result.refresh_token)
    assert access_payload["sub"] == str(user.user_id)
    assert access_payload["email"] == user.email
    assert access_payload["role"] == user.role.value
    assert refresh_payload["sub"] == str(user.user_id)


@pytest.mark.asyncio
async def test_login_rejects_unknown_email():
    service = AuthService(session=None)  # type: ignore[arg-type]
    service.user_repository = StubUserRepository(None)

    with pytest.raises(AppException) as exc_info:
        await service.login(
            LoginRequest(email="missing@example.com", password="securepassword123")
        )

    assert exc_info.value.code == "INVALID_CREDENTIALS"
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_login_rejects_wrong_password():
    user = SimpleNamespace(
        user_id=uuid4(),
        email="login@example.com",
        password_hash="stored-hash",
        name="Login User",
        role=UserRole.PERFORMER,
    )
    service = AuthService(session=None)  # type: ignore[arg-type]
    service.user_repository = StubUserRepository(user)

    original_verify_password = auth_service_module.verify_password
    auth_service_module.verify_password = lambda plain, hashed: False

    try:
        with pytest.raises(AppException) as exc_info:
            await service.login(
                LoginRequest(email="login@example.com", password="wrongpassword123")
            )
    finally:
        auth_service_module.verify_password = original_verify_password

    assert exc_info.value.code == "INVALID_CREDENTIALS"
    assert exc_info.value.status_code == 401
