from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import Message

class MessageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, message: Message) -> Message:
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message

    async def get_by_task_id(self, task_id: UUID) -> Sequence[Message]:
        result = await self.session.execute(
            select(Message)
            .where(Message.task_id == task_id)
            .order_by(Message.created_at.asc())
        )
        return result.scalars().all()
