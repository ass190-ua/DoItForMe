from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import AppException
from app.core.security import decode_token
from app.models.user import UserRole
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services import auth_service as auth_service_module
from app.services.auth_service import AuthService


def test_auth_service_initializes_with_session_stub():
    session = StubSession()
    service = AuthService(session=session)

    assert service.session is session
    assert service.user_repository is not None


class StubUserRepository:
    def __init__(self, user):
        self.user = user
        self.created_user = None
        self.error_to_raise = None

    async def get_by_email(self, email: str):
        if self.user is not None and self.user.email == email:
            return self.user
        return None

    async def create(self, user):
        if self.error_to_raise is not None:
            raise self.error_to_raise
        if getattr(user, "user_id", None) is None:
            user.user_id = uuid4()
        self.created_user = user
        return user


class StubSession:
    def __init__(self) -> None:
        self.commit_called = False
        self.rollback_called = False

    async def commit(self) -> None:
        self.commit_called = True

    async def rollback(self) -> None:
        self.rollback_called = True


class StubAuthSessionRepository:
    def __init__(self) -> None:
        self.created_sessions = []
        self.revoked_jtis = []
        self.active_sessions_by_jti = {}

    async def create(self, auth_session):
        self.created_sessions.append(auth_session)
        self.active_sessions_by_jti[auth_session.access_jti] = auth_session
        return auth_session

    async def revoke_by_access_jti(self, access_jti: str):
        self.revoked_jtis.append(access_jti)
        return self.active_sessions_by_jti.pop(access_jti, None)


@pytest.mark.asyncio
async def test_login_returns_user_and_tokens():
    user = SimpleNamespace(
        user_id=uuid4(),
        email="login@example.com",
        password_hash="stored-hash",
        name="Login User",
        role=UserRole.POSTER,
    )
    service = AuthService(session=StubSession())
    service.user_repository = StubUserRepository(user)
    service.auth_session_repository = StubAuthSessionRepository()

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
    assert len(service.auth_session_repository.created_sessions) == 1

    access_payload = decode_token(result.access_token)
    refresh_payload = decode_token(result.refresh_token)
    assert access_payload["sub"] == str(user.user_id)
    assert access_payload["email"] == user.email
    assert access_payload["role"] == user.role.value
    assert access_payload["token_type"] == "access"
    assert refresh_payload["sub"] == str(user.user_id)
    assert refresh_payload["token_type"] == "refresh"
    persisted_session = service.auth_session_repository.created_sessions[0]
    assert persisted_session.access_jti == access_payload["jti"]
    assert persisted_session.refresh_jti == refresh_payload["jti"]


@pytest.mark.asyncio
async def test_register_creates_user_and_hashes_password():
    session = StubSession()
    service = AuthService(session=session)
    service.user_repository = StubUserRepository(None)
    service.auth_session_repository = StubAuthSessionRepository()

    original_hash_password = auth_service_module.hash_password
    auth_service_module.hash_password = lambda password: f"hashed::{password}"

    try:
        result = await service.register(
            RegisterRequest(
                email="new@example.com",
                password="securepassword123",
                name="New User",
                role=UserRole.POSTER,
            )
        )
    finally:
        auth_service_module.hash_password = original_hash_password

    created_user = service.user_repository.created_user
    assert created_user is not None
    assert created_user.email == "new@example.com"
    assert created_user.name == "New User"
    assert created_user.role == UserRole.POSTER
    assert created_user.password_hash == "hashed::securepassword123"
    assert session.commit_called is True
    assert session.rollback_called is False
    assert result.email == "new@example.com"
    assert result.role == "poster"


@pytest.mark.asyncio
async def test_register_rejects_duplicate_email_before_create():
    existing_user = SimpleNamespace(
        email="existing@example.com",
        password_hash="stored-hash",
        name="Existing User",
        role=UserRole.POSTER,
    )
    session = StubSession()
    service = AuthService(session=session)
    service.user_repository = StubUserRepository(existing_user)
    service.auth_session_repository = StubAuthSessionRepository()

    with pytest.raises(AppException) as exc_info:
        await service.register(
            RegisterRequest(
                email="existing@example.com",
                password="securepassword123",
                name="Another User",
                role=UserRole.PERFORMER,
            )
        )

    assert exc_info.value.code == "EMAIL_ALREADY_EXISTS"
    assert exc_info.value.status_code == 409
    assert service.user_repository.created_user is None
    assert session.commit_called is False


@pytest.mark.asyncio
async def test_register_maps_integrity_error_to_conflict():
    session = StubSession()
    service = AuthService(session=session)
    service.user_repository = StubUserRepository(None)
    service.auth_session_repository = StubAuthSessionRepository()
    service.user_repository.error_to_raise = IntegrityError(
        statement="INSERT INTO users ...",
        params={"email": "race@example.com"},
        orig=Exception("unique violation"),
    )

    original_hash_password = auth_service_module.hash_password
    auth_service_module.hash_password = lambda password: f"hashed::{password}"

    try:
        with pytest.raises(AppException) as exc_info:
            await service.register(
                RegisterRequest(
                    email="race@example.com",
                    password="securepassword123",
                    name="Race User",
                    role=UserRole.POSTER,
                )
            )
    finally:
        auth_service_module.hash_password = original_hash_password

    assert exc_info.value.code == "EMAIL_ALREADY_EXISTS"
    assert exc_info.value.status_code == 409
    assert session.commit_called is False
    assert session.rollback_called is True


@pytest.mark.asyncio
async def test_register_rejects_weak_password_in_service():
    session = StubSession()
    service = AuthService(session=session)
    service.user_repository = StubUserRepository(None)
    service.auth_session_repository = StubAuthSessionRepository()

    weak_request = auth_service_module.RegisterRequest.model_construct(
        email="weak@example.com",
        password="short",
        name="Weak User",
        role=UserRole.POSTER,
    )

    with pytest.raises(AppException) as exc_info:
        await service.register(weak_request)

    assert exc_info.value.code == "WEAK_PASSWORD"
    assert exc_info.value.status_code == 422
    assert service.user_repository.created_user is None
    assert session.commit_called is False


@pytest.mark.asyncio
async def test_login_rejects_unknown_email():
    service = AuthService(session=StubSession())
    service.user_repository = StubUserRepository(None)
    service.auth_session_repository = StubAuthSessionRepository()

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
    service = AuthService(session=StubSession())
    service.user_repository = StubUserRepository(user)
    service.auth_session_repository = StubAuthSessionRepository()

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


@pytest.mark.asyncio
async def test_logout_revokes_active_session():
    session = StubSession()
    service = AuthService(session=session)
    service.user_repository = StubUserRepository(None)
    service.auth_session_repository = StubAuthSessionRepository()
    existing_session = SimpleNamespace(access_jti="access-jti-123")
    service.auth_session_repository.active_sessions_by_jti["access-jti-123"] = (
        existing_session
    )

    result = await service.logout(
        {
            "sub": str(uuid4()),
            "email": "user@example.com",
            "role": "poster",
            "jti": "access-jti-123",
        }
    )

    assert result.message == "Successfully logged out"
    assert session.commit_called is True
    assert service.auth_session_repository.revoked_jtis == ["access-jti-123"]


@pytest.mark.asyncio
async def test_logout_rejects_inactive_session():
    session = StubSession()
    service = AuthService(session=session)
    service.user_repository = StubUserRepository(None)
    service.auth_session_repository = StubAuthSessionRepository()

    with pytest.raises(AppException) as exc_info:
        await service.logout(
            {
                "sub": str(uuid4()),
                "email": "user@example.com",
                "role": "poster",
                "jti": "missing-jti",
            }
        )

    assert exc_info.value.code == "INVALID_TOKEN"
    assert exc_info.value.status_code == 401
    assert session.commit_called is False
