from collections.abc import AsyncIterator

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.core.security import decode_token
from app.repositories.auth_session_repository import AuthSessionRepository
from app.db.session import get_db_session


async def db_session_dependency(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncIterator[AsyncSession]:
    yield session


async def get_current_token_payload(
    authorization: str | None = Header(default=None),
    session: AsyncSession = Depends(db_session_dependency),
) -> dict[str, str]:
    if authorization is None:
        raise AppException(
            code="AUTHENTICATION_REQUIRED",
            message="Authorization header is required",
            status_code=401,
        )
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise AppException(
            code="INVALID_AUTH_HEADER",
            message="Bearer token is required",
            status_code=401,
        )
    payload = decode_token(token)
    if payload["token_type"] != "access":
        raise AppException(
            code="INVALID_TOKEN",
            message="Access token is required",
            status_code=401,
        )
    auth_session_repository = AuthSessionRepository(session)
    auth_session = await auth_session_repository.get_active_by_access_jti(
        str(payload["jti"])
    )
    if auth_session is None:
        raise AppException(
            code="INVALID_TOKEN",
            message="Session is no longer active",
            status_code=401,
        )
    return {key: str(payload[key]) for key in ("sub", "email", "role", "jti")}


async def require_authenticated_user(
    payload: dict[str, str] = Depends(get_current_token_payload),
) -> dict[str, str]:
    return payload
