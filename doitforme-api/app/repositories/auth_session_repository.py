from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth_session import AuthSession


class AuthSessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def _active_session_filters() -> tuple:
        return (
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > datetime.now(UTC),
        )

    async def create(self, auth_session: AuthSession) -> AuthSession:
        self.session.add(auth_session)
        await self.session.flush()
        await self.session.refresh(auth_session)
        return auth_session

    async def get_active_by_access_jti(self, access_jti: str) -> AuthSession | None:
        result = await self.session.execute(
            select(AuthSession).where(
                AuthSession.access_jti == access_jti,
                *self._active_session_filters(),
            )
        )
        return result.scalar_one_or_none()

    async def revoke_by_access_jti(self, access_jti: str) -> AuthSession | None:
        auth_session = await self.get_active_by_access_jti(access_jti)
        if auth_session is None:
            return None
        auth_session.revoked_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(auth_session)
        return auth_session

    async def get_active_by_refresh_jti(self, refresh_jti: str) -> AuthSession | None:
        result = await self.session.execute(
            select(AuthSession).where(
                AuthSession.refresh_jti == refresh_jti,
                *self._active_session_filters(),
            )
        )
        return result.scalar_one_or_none()

    async def get_active_for_user(self, user_id: UUID) -> list[AuthSession]:
        result = await self.session.execute(
            select(AuthSession).where(
                AuthSession.user_id == user_id,
                *self._active_session_filters(),
            )
        )
        return list(result.scalars().all())
