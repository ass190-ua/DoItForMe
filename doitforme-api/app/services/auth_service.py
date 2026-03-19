from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest, UserPublic


PASSWORD_POLICY_MESSAGE = "Password must be at least 8 characters"


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repository = UserRepository(session)

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

        created = await self.user_repository.create(user)
        await self.session.commit()

        return UserPublic.model_validate(created)

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        return await self.user_repository.get_by_id(user_id)
