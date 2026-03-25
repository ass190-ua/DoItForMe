from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MessageCreateRequest(BaseModel):
    content: str = Field(..., max_length=2000, description="Contenido del mensaje")


class MessagePublic(BaseModel):
    id: UUID
    task_id: UUID
    sender_id: UUID
    content: str
    image_url: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
