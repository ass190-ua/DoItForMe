from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.auth_session import AuthSession
from app.models.user import User
from app.repositories.auth_session_repository import AuthSessionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    PasswordRecoveryRequest,
    PasswordResetRequest,
    PasswordResetResponse,
    RegisterRequest,
    UserPublic,
)


PASSWORD_POLICY_MESSAGE = "Password must be at least 8 characters"
INVALID_CREDENTIALS_MESSAGE = "Invalid email or password"
REFRESH_TOKEN_EXPIRE_DAYS = 7


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repository = UserRepository(session)
        self.auth_session_repository = AuthSessionRepository(session)

    async def user_exists(self, email: str) -> bool:
        return await self.user_repository.get_by_email(email) is not None

    async def register(self, data: RegisterRequest) -> UserPublic:
        existing = await self.user_repository.get_by_email(data.email)
        if existing is not None:
            raise AppException(
                code="EMAIL_ALREADY_EXISTS",
                message="An account with this email already exists",
                status_code=409,
            )

        if len(data.password) < 8:
            raise AppException(
                code="WEAK_PASSWORD",
                message=PASSWORD_POLICY_MESSAGE,
                status_code=422,
            )

        password_hash = hash_password(data.password)

        user = User(
            email=data.email,
            password_hash=password_hash,
            name=data.name,
            role=data.role,
        )

        try:
            created = await self.user_repository.create(user)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise AppException(
                code="EMAIL_ALREADY_EXISTS",
                message="An account with this email already exists",
                status_code=409,
            ) from exc

        return UserPublic.model_validate(created)

    async def login(self, data: LoginRequest) -> LoginResponse:
        user = await self.user_repository.get_by_email(data.email)
        if user is None or not verify_password(data.password, user.password_hash):
            raise AppException(
                code="INVALID_CREDENTIALS",
                message=INVALID_CREDENTIALS_MESSAGE,
                status_code=401,
            )

        access_jti = str(uuid4())
        refresh_jti = str(uuid4())

        access_token = create_access_token(
            subject=str(user.user_id),
            email=user.email,
            role=user.role.value,
            token_type="access",
            token_id=access_jti,
        )
        refresh_token = create_access_token(
            subject=str(user.user_id),
            email=user.email,
            role=user.role.value,
            token_type="refresh",
            token_id=refresh_jti,
            expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )

        refresh_payload = decode_token(refresh_token)
        auth_session = AuthSession(
            user_id=user.user_id,
            access_jti=access_jti,
            refresh_jti=refresh_jti,
            refresh_token_hash=hash_token(refresh_token),
            expires_at=datetime.fromtimestamp(int(refresh_payload["exp"]), tz=UTC),
        )
        await self.auth_session_repository.create(auth_session)
        await self.session.commit()

        return LoginResponse(
            user=UserPublic.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def logout(self, current_user: dict[str, str]) -> LogoutResponse:
        revoked_session = await self.auth_session_repository.revoke_by_access_jti(
            current_user["jti"]
        )
        if revoked_session is None:
            raise AppException(
                code="INVALID_TOKEN",
                message="Session is no longer active",
                status_code=401,
            )
        await self.session.commit()
        return LogoutResponse(message="Successfully logged out")

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        return await self.user_repository.get_by_id(user_id)

    async def password_recovery(self, data: PasswordRecoveryRequest) -> PasswordResetResponse:
        user = await self.user_repository.get_by_email(data.email)
        # We don't want to leak if the email exists, but for the simulation, we'll log the token
        if user:
            token = str(uuid4())
            user.password_reset_token = token
            user.password_reset_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
            await self.user_repository.update(user)
            await self.session.commit()
            # Simulation: In a real app, send an email. Here we just log it or return a generic message.
            print(f"DEBUG: Password reset token for {data.email}: {token}")
        
        return PasswordResetResponse(
            message="If the email exists, a password reset link has been sent"
        )

    async def password_reset(self, data: PasswordResetRequest) -> PasswordResetResponse:
        user = await self.user_repository.get_by_reset_token(data.token)
        if not user or not user.password_reset_expires_at:
            raise AppException(
                code="INVALID_TOKEN", message="Invalid or expired reset token", status_code=400
            )
            
        if datetime.now(timezone.utc) > user.password_reset_expires_at:
            user.password_reset_token = None
            user.password_reset_expires_at = None
            await self.user_repository.update(user)
            await self.session.commit()
            raise AppException(
                code="EXPIRED_TOKEN", message="The reset token has expired", status_code=400
            )
            
        user.password_hash = hash_password(data.new_password)
        user.password_reset_token = None
        user.password_reset_expires_at = None
        await self.user_repository.update(user)
        await self.session.commit()
        
        return PasswordResetResponse(message="Password reset successfully")
