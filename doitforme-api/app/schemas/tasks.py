from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskLocation(BaseModel):
    latitude: Decimal = Field(ge=-90, le=90)
    longitude: Decimal = Field(ge=-180, le=180)


class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)
    location: TaskLocation
    initial_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    category: str | None = Field(default=None, min_length=1, max_length=50)

    model_config = ConfigDict(extra="forbid")


class TaskPublic(BaseModel):
    task_id: UUID
    title: str
    description: str | None
    location: TaskLocation
    initial_price: Decimal
    category: str | None = None
    status: str
    created_by: UUID
    created_at: datetime


class TaskResponse(BaseModel):
    task: TaskPublic
