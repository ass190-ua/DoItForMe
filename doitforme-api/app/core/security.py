from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.exceptions import AppException


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    *, subject: str, email: str, role: str, expires_delta: timedelta | None = None
) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    expire_at = now + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {
        "sub": subject,
        "email": email,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire_at.timestamp()),
    }
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
    except JWTError as exc:
        raise AppException(
            code="INVALID_TOKEN", message="Token is invalid or expired", status_code=401
        ) from exc
    required_fields = {"sub", "email", "role", "iat", "exp"}
    if not required_fields.issubset(payload):
        raise AppException(
            code="INVALID_TOKEN", message="Token payload is incomplete", status_code=401
        )
    return payload
