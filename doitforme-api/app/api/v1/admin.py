from uuid import UUID
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session_dependency, require_admin_user
from app.core.response import success_response
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.models.message import Message
from app.services.task_service import TaskService
from app.services.wallet_service import WalletService

router = APIRouter()

@router.get("/metrics", summary="Get platform metrics")
async def get_metrics(
    admin: dict[str, str] = Depends(require_admin_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    # Basic counts
    user_count = await session.scalar(select(func.count(User.user_id)))
    task_count = await session.scalar(select(func.count(Task.task_id)))
    completed_task_count = await session.scalar(
        select(func.count(Task.task_id)).where(Task.status == TaskStatus.COMPLETED)
    )
    
    completion_rate = (completed_task_count / task_count * 100) if task_count > 0 else 0
    
    payload, status_code = success_response({
        "total_users": user_count,
        "total_tasks": task_count,
        "completed_tasks": completed_task_count,
        "completion_rate": round(completion_rate, 2)
    })
    return JSONResponse(status_code=status_code, content=payload)

@router.get("/users", summary="List all users")
async def list_users(
    admin: dict[str, str] = Depends(require_admin_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    result = await session.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    
    payload, status_code = success_response({
        "users": [{
            "user_id": str(u.user_id),
            "email": u.email,
            "name": u.name,
            "role": u.role,
            "balance": str(u.balance),
            "rating": str(u.rating),
            "created_at": u.created_at.isoformat()
        } for u in users]
    })
    return JSONResponse(status_code=status_code, content=payload)

@router.get("/tasks", summary="List all tasks")
async def list_tasks(
    status_filter: TaskStatus | None = None,
    admin: dict[str, str] = Depends(require_admin_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    stmt = select(Task).order_by(Task.created_at.desc())
    if status_filter:
        stmt = stmt.where(Task.status == status_filter)
        
    result = await session.execute(stmt)
    tasks = result.scalars().all()
    
    payload, status_code = success_response({
        "tasks": [{
            "task_id": str(t.task_id),
            "title": t.title,
            "status": t.status,
            "creator_id": str(t.creator_id),
            "runner_id": str(t.runner_id) if t.runner_id else None,
            "accepted_price": str(t.accepted_price) if t.accepted_price else None,
            "created_at": t.created_at.isoformat()
        } for t in tasks]
    })
    return JSONResponse(status_code=status_code, content=payload)

@router.get("/tasks/{task_id}", summary="Get task detail with chat history")
async def get_task_admin(
    task_id: UUID,
    admin: dict[str, str] = Depends(require_admin_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    task = await session.get(Task, task_id)
    if not task:
        payload, status_code = success_response({"message": "Task not found"}, status_code=404)
        return JSONResponse(status_code=status_code, content=payload)
    
    # Get chat history
    msg_result = await session.execute(
        select(Message).where(Message.task_id == task_id).order_by(Message.created_at.asc())
    )
    messages = msg_result.scalars().all()
    
    payload, status_code = success_response({
        "task": {
            "task_id": str(task.task_id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "creator_id": str(task.creator_id),
            "runner_id": str(task.runner_id) if task.runner_id else None,
            "accepted_price": str(task.accepted_price) if task.accepted_price else None,
            "proof_image_url": task.proof_image_url
        },
        "chat_history": [{
            "id": str(m.id),
            "sender_id": str(m.sender_id),
            "content": m.content,
            "image_url": m.image_url,
            "created_at": m.created_at.isoformat()
        } for m in messages]
    })
    return JSONResponse(status_code=status_code, content=payload)

@router.post("/payments/{task_id}/adjust", summary="Manual escrow adjustment")
async def adjust_payment(
    task_id: UUID,
    action: str, # "release" or "refund"
    admin: dict[str, str] = Depends(require_admin_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    task_service = TaskService(session)
    
    if action == "release":
        task = await task_service.admin_force_release_payment(task_id)
    elif action == "refund":
        task = await task_service.admin_force_refund_payment(task_id)
    else:
        payload, status_code = success_response({"message": "Invalid action. Use 'release' or 'refund'"}, status_code=400)
        return JSONResponse(status_code=status_code, content=payload)
        
    payload, status_code = success_response({
        "message": f"Action {action} performed successfully for task {task_id}",
        "new_status": task.status
    })
    return JSONResponse(status_code=status_code, content=payload)
