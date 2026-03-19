from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session_dependency, require_authenticated_user
from app.core.response import success_response
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    RegisterRequest,
    RegisterResponse,
)
from app.services.auth_service import AuthService


router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    data: RegisterRequest,
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    service = AuthService(session)
    user_public = await service.register(data)
    payload, status_code = success_response(
        {"user": user_public.model_dump(mode="json")},
        status_code=status.HTTP_201_CREATED,
    )
    return JSONResponse(status_code=status_code, content=payload)


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Log in and receive session tokens",
)
async def login(
    data: LoginRequest,
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    service = AuthService(session)
    login_response = await service.login(data)
    payload, status_code = success_response(login_response.model_dump(mode="json"))
    return JSONResponse(status_code=status_code, content=payload)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Log out and revoke the current session",
)
async def logout(
    current_user: dict[str, str] = Depends(require_authenticated_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    service = AuthService(session)
    logout_response = await service.logout(current_user)
    payload, status_code = success_response(logout_response.model_dump(mode="json"))
    return JSONResponse(status_code=status_code, content=payload)
