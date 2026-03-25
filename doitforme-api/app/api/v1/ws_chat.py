"""WebSocket endpoint for real-time chat within a task room."""
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.core.security import decode_token
from app.core.ws_manager import ws_manager
from app.db.session import get_db_session
from app.models.message import Message
from app.repositories.auth_session_repository import AuthSessionRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.messages import MessagePublic

router = APIRouter()


async def _authenticate_ws(token: str, session: AsyncSession) -> dict[str, str]:
    """Validate JWT token for WebSocket connections."""
    try:
        payload = decode_token(token)
    except AppException:
        return None

    if payload.get("token_type") != "access":
        return None

    auth_repo = AuthSessionRepository(session)
    auth_session = await auth_repo.get_active_by_access_jti(str(payload["jti"]))
    if auth_session is None:
        return None

    return {key: str(payload[key]) for key in ("sub", "email", "role", "jti")}


@router.websocket("/ws/chat/{task_id}")
async def websocket_chat(
    websocket: WebSocket,
    task_id: str,
    token: str = Query(...),
):
    # 1. Get DB session
    session_gen = get_db_session()
    session: AsyncSession = await session_gen.__anext__()

    try:
        task_uuid = UUID(task_id)

        # 2. Authenticate via JWT
        user = await _authenticate_ws(token, session)
        if user is None:
            await websocket.close(code=4001, reason="Authentication failed")
            return

        user_id = UUID(user["sub"])

        # 3. Validate user has access to this task's chat
        task_repo = TaskRepository(session)
        task = await task_repo.get_by_id(task_uuid)
        if not task:
            await websocket.close(code=4004, reason="Task not found")
            return

        if task.creator_id != user_id and task.runner_id != user_id:
            await websocket.close(code=4003, reason="Forbidden")
            return

        # 4. Accept connection and join room
        await ws_manager.connect(task_uuid, user_id, websocket)

        try:
            while True:
                # 5. Receive message
                data = await websocket.receive_json()
                content = data.get("content", "").strip()
                if not content:
                    continue

                # Truncate to max length
                content = content[:2000]

                # 6. Persist to database
                msg_repo = MessageRepository(session)
                message = Message(
                    task_id=task_uuid,
                    sender_id=user_id,
                    content=content,
                )
                created = await msg_repo.create(message)
                await session.commit()

                # 7. Broadcast to all in room
                msg_public = MessagePublic.model_validate(created)
                await ws_manager.broadcast_to_task(
                    task_uuid,
                    msg_public.model_dump(mode="json"),
                )

        except WebSocketDisconnect:
            ws_manager.disconnect(task_uuid, user_id)
        except Exception:
            ws_manager.disconnect(task_uuid, user_id)

    finally:
        # Cleanup DB session
        try:
            await session_gen.aclose()
        except Exception:
            pass
