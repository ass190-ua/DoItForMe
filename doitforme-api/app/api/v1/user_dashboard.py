from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session_dependency, require_authenticated_user
from app.core.response import success_response
from app.services.task_service import TaskService

router = APIRouter()

@router.get(
    "/tasks",
    status_code=status.HTTP_200_OK,
    summary="Get tasks related to the authenticated user",
)
async def get_my_tasks(
    role: str = Query("creator", pattern="^(creator|runner)$"),
    limit: int = Query(20, gt=0, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict[str, str] = Depends(require_authenticated_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    """
    Returns tasks where the user is either the creator or the assigned runner.
    """
    service = TaskService(session)
    tasks = await service.get_user_tasks(
        current_user=current_user,
        role=role,
        limit=limit,
        offset=offset
    )
    payload, status_code = success_response(
        {"tasks": [task.model_dump(mode="json") for task in tasks]}
    )
    return JSONResponse(status_code=status_code, content=payload)
