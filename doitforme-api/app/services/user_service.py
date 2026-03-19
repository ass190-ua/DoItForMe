from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.repositories.user_repository import UserRepository
from app.schemas.users import (
    PublicProfile,
    SelfProfile,
    SelfProfileUpdateRequest,
)


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repository = UserRepository(session)

    async def get_self_profile(self, user_id: UUID) -> SelfProfile:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise AppException(
                code="USER_NOT_FOUND",
                message="User profile was not found",
                status_code=404,
            )
        return SelfProfile.model_validate(user)

    async def get_public_profile(self, user_id: UUID) -> PublicProfile:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise AppException(
                code="USER_NOT_FOUND",
                message="User profile was not found",
                status_code=404,
            )
        return PublicProfile.model_validate(user)

    async def update_self_profile(
        self, user_id: UUID, data: SelfProfileUpdateRequest
    ) -> SelfProfile:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise AppException(
                code="USER_NOT_FOUND",
                message="User profile was not found",
                status_code=404,
            )

        updated_user = await self.user_repository.update_profile(
            user,
            name=data.name,
            latitude=data.latitude,
            longitude=data.longitude,
        )
        await self.session.commit()
        return SelfProfile.model_validate(updated_user)
