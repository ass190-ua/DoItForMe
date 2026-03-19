from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session_dependency
from app.core.response import error_response, success_response
from app.schemas.auth import RegisterRequest, RegisterResponse
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
        {"user": user_public.model_dump(mode="json")}
    )
    return JSONResponse(status_code=status_code, content=payload)
