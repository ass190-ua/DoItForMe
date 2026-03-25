from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session_dependency, require_authenticated_user
from app.core.response import success_response
from app.schemas.tasks import TaskCreateRequest, TaskResponse
from app.services.task_service import TaskService


router = APIRouter()


@router.get(
    "/available",
    status_code=status.HTTP_200_OK,
    summary="Get available tasks (published tasks not created by the current user)",
)
async def get_available_tasks(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lng: float = Query(..., ge=-180.0, le=180.0),
    radius: float = Query(5.0, gt=0.0),
    category: str | None = Query(None),
    sort_by: str = Query("distance", pattern="^(distance|price_desc|recent)$"),
    limit: int = Query(20, gt=0, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict[str, str] = Depends(require_authenticated_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    service = TaskService(session)
    tasks = await service.get_available_tasks(
        current_user=current_user,
        lat=lat,
        lng=lng,
        radius_km=radius,
        category=category,
        sort_by=sort_by,
        limit=limit,
        offset=offset
    )
    payload, status_code = success_response(
        {"tasks": [task.model_dump(mode="json") for task in tasks]},
        status_code=status.HTTP_200_OK,
    )
    return JSONResponse(status_code=status_code, content=payload)


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


@router.post(
    "/{task_id}/start",
    status_code=status.HTTP_200_OK,
    summary="Start an accepted task (runner only)",
)
async def start_task(
    task_id: str,
    current_user: dict[str, str] = Depends(require_authenticated_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    from uuid import UUID
    
    service = TaskService(session)
    task = await service.start_task(current_user, UUID(task_id))
    payload, status_code = success_response(
        {"task": task.model_dump(mode="json")}, status_code=status.HTTP_200_OK
    )
    return JSONResponse(status_code=status_code, content=payload)


@router.post(
    "/{task_id}/complete",
    status_code=status.HTTP_200_OK,
    summary="Complete an in-progress task (creator only)",
)
async def complete_task(
    task_id: str,
    current_user: dict[str, str] = Depends(require_authenticated_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    from uuid import UUID
    
    service = TaskService(session)
    task = await service.complete_task(current_user, UUID(task_id))
    payload, status_code = success_response(
        {"task": task.model_dump(mode="json")}, status_code=status.HTTP_200_OK
    )
    return JSONResponse(status_code=status_code, content=payload)


@router.post(
    "/{task_id}/cancel",
    status_code=status.HTTP_200_OK,
    summary="Cancel a task (creator only, refunds escrow if applicable)",
)
async def cancel_task(
    task_id: str,
    current_user: dict[str, str] = Depends(require_authenticated_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    from uuid import UUID
    
    service = TaskService(session)
    task = await service.cancel_task(current_user, UUID(task_id))
    payload, status_code = success_response(
        {"task": task.model_dump(mode="json")}, status_code=status.HTTP_200_OK
    )
    return JSONResponse(status_code=status_code, content=payload)
