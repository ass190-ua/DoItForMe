from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session_dependency, require_authenticated_user
from app.core.response import success_response
from app.schemas.users import (
    PublicProfileResponse,
    SelfProfileResponse,
    SelfProfileUpdateRequest,
)
from app.services.user_service import UserService


router = APIRouter()


@router.get(
    "/me",
    response_model=SelfProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="View my profile",
)
async def get_my_profile(
    current_user: dict[str, str] = Depends(require_authenticated_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    service = UserService(session)
    profile = await service.get_self_profile(UUID(current_user["sub"]))
    payload, status_code = success_response(
        {"profile": profile.model_dump(mode="json")}
    )
    return JSONResponse(status_code=status_code, content=payload)


@router.put(
    "/me",
    response_model=SelfProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update my profile",
)
async def update_my_profile(
    data: SelfProfileUpdateRequest,
    current_user: dict[str, str] = Depends(require_authenticated_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    service = UserService(session)
    profile = await service.update_self_profile(UUID(current_user["sub"]), data)
    payload, status_code = success_response(
        {"profile": profile.model_dump(mode="json")}
    )
    return JSONResponse(status_code=status_code, content=payload)


@router.get(
    "/{user_id}",
    response_model=PublicProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="View another user's public profile",
)
async def get_public_profile(
    user_id: UUID,
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    service = UserService(session)
    profile = await service.get_public_profile(user_id)
    payload, status_code = success_response(
        {"profile": profile.model_dump(mode="json")}
    )
    return JSONResponse(status_code=status_code, content=payload)
