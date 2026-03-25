from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session_dependency, require_authenticated_user
from app.core.response import success_response
from app.schemas.messages import MessageCreateRequest, MessagePublic
from app.services.message_service import MessageService

router = APIRouter()

@router.post(
    "/{task_id}/messages",
    response_model=MessagePublic,
    status_code=status.HTTP_201_CREATED,
    summary="Send a message to a task chat",
)
async def create_message(
    task_id: UUID,
    data: MessageCreateRequest,
    current_user: dict[str, str] = Depends(require_authenticated_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    service = MessageService(session)
    message = await service.create_message(current_user, task_id, data)
    payload, status_code = success_response(
        {"message": message.model_dump(mode="json")},
        status_code=status.HTTP_201_CREATED,
    )
    return JSONResponse(status_code=status_code, content=payload)


@router.get(
    "/{task_id}/messages",
    status_code=status.HTTP_200_OK,
    summary="Get all messages from a task chat",
)
async def get_task_messages(
    task_id: UUID,
    current_user: dict[str, str] = Depends(require_authenticated_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    service = MessageService(session)
    messages = await service.get_task_messages(current_user, task_id)
    payload, status_code = success_response(
        {"messages": [message.model_dump(mode="json") for message in messages]},
        status_code=status.HTTP_200_OK,
    )
    return JSONResponse(status_code=status_code, content=payload)
