from uuid import UUID
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.message import Message
from app.repositories.message_repository import MessageRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.messages import MessageCreateRequest, MessagePublic

class MessageService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.message_repository = MessageRepository(session)
        self.task_repository = TaskRepository(session)

    async def _validate_user_can_access_chat(self, task_id: UUID, user_id: UUID) -> None:
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            raise AppException(code="TASK_NOT_FOUND", message="Task not found", status_code=404)
        
        if task.creator_id != user_id and task.runner_id != user_id:
            raise AppException(
                code="FORBIDDEN_CHAT_ACCESS", 
                message="No tienes permiso para ver o enviar mensajes a esta tarea.", 
                status_code=403
            )

    async def create_message(self, current_user: dict[str, str], task_id: UUID, data: MessageCreateRequest) -> MessagePublic:
        user_id = UUID(current_user["sub"])
        await self._validate_user_can_access_chat(task_id, user_id)
        
        message = Message(
            task_id=task_id,
            sender_id=user_id,
            content=data.content
        )
        
        created_message = await self.message_repository.create(message)
        
        # Sprint 8: Notification Trigger
        task = await self.task_repository.get_by_id(task_id)
        if task:
            recipient_id = task.runner_id if user_id == task.creator_id else task.creator_id
            if recipient_id:
                from app.services.notification_service import NotificationService
                await NotificationService.notify_new_message(
                    recipient_id=recipient_id,
                    sender_name=current_user.get("name", "Usuario"),
                    message_text=data.content,
                    task_id=task_id
                )

        await self.session.commit()
        return MessagePublic.model_validate(created_message)

    async def get_task_messages(self, current_user: dict[str, str], task_id: UUID) -> Sequence[MessagePublic]:
        user_id = UUID(current_user["sub"])
        await self._validate_user_can_access_chat(task_id, user_id)
        
        messages = await self.message_repository.get_by_task_id(task_id)
        return [MessagePublic.model_validate(m) for m in messages]
