from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session_dependency, require_authenticated_user
from app.core.response import success_response
from app.schemas.tasks import TaskCreateRequest, TaskResponse
from app.services.task_service import TaskService


router = APIRouter()


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
async def create_task(
    data: TaskCreateRequest,
    current_user: dict[str, str] = Depends(require_authenticated_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    service = TaskService(session)
    task = await service.create_task(current_user, data)
    payload, status_code = success_response(
        {"task": task.model_dump(mode="json")},
        status_code=status.HTTP_201_CREATED,
    )
    return JSONResponse(status_code=status_code, content=payload)
