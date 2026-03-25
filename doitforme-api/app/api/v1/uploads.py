"""Upload endpoints for task proof images and chat attachments."""
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session_dependency, require_authenticated_user
from app.core.exceptions import AppException
from app.core.response import success_response
from app.repositories.task_repository import TaskRepository
from app.repositories.message_repository import MessageRepository
from app.models.message import Message
from app.services.file_storage import LocalFileStorage

router = APIRouter()


@router.post(
    "/task-proof/{task_id}",
    status_code=200,
    summary="Upload a proof-of-work image for a task (runner only)",
)
async def upload_task_proof(
    task_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(require_authenticated_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    user_id = UUID(current_user["sub"])
    task_uuid = UUID(task_id)

    # Validate task
    task_repo = TaskRepository(session)
    task = await task_repo.get_by_id(task_uuid)
    if not task:
        raise AppException(code="NOT_FOUND", message="Task not found", status_code=404)

    # Only the runner can upload proof
    if task.runner_id != user_id:
        raise AppException(
            code="FORBIDDEN",
            message="Only the assigned runner can upload proof images",
            status_code=403,
        )

    # Task must be in_progress or accepted
    if task.status not in ("accepted", "in_progress"):
        raise AppException(
            code="INVALID_STATE",
            message="Proof can only be uploaded for accepted or in-progress tasks",
            status_code=400,
        )

    # Read and save file
    file_bytes = await file.read()
    storage = LocalFileStorage()
    url = await storage.save(
        file_bytes=file_bytes,
        content_type=file.content_type or "application/octet-stream",
        subdirectory="tasks",
        original_filename=file.filename or "upload",
    )

    # Update task
    task.proof_image_url = url
    await task_repo.update(task)
    await session.commit()

    payload, status_code = success_response({"image_url": url})
    return JSONResponse(status_code=status_code, content=payload)


@router.post(
    "/chat-image/{task_id}",
    status_code=200,
    summary="Upload an image in the task chat",
)
async def upload_chat_image(
    task_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(require_authenticated_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    user_id = UUID(current_user["sub"])
    task_uuid = UUID(task_id)

    # Validate task and access
    task_repo = TaskRepository(session)
    task = await task_repo.get_by_id(task_uuid)
    if not task:
        raise AppException(code="NOT_FOUND", message="Task not found", status_code=404)

    if task.creator_id != user_id and task.runner_id != user_id:
        raise AppException(
            code="FORBIDDEN_CHAT_ACCESS",
            message="No tienes permiso para enviar imágenes a esta tarea.",
            status_code=403,
        )

    # Read and save file
    file_bytes = await file.read()
    storage = LocalFileStorage()
    url = await storage.save(
        file_bytes=file_bytes,
        content_type=file.content_type or "application/octet-stream",
        subdirectory="messages",
        original_filename=file.filename or "upload",
    )

    # Create message with image
    msg_repo = MessageRepository(session)
    message = Message(
        task_id=task_uuid,
        sender_id=user_id,
        content="[image]",
        image_url=url,
    )
    created = await msg_repo.create(message)
    await session.commit()

    from app.schemas.messages import MessagePublic
    msg_public = MessagePublic.model_validate(created)

    payload, status_code = success_response({
        "message": msg_public.model_dump(mode="json"),
    })
    return JSONResponse(status_code=status_code, content=payload)
