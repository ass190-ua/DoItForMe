from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)
    location_lat: Decimal = Field(ge=-90, le=90)
    location_lng: Decimal = Field(ge=-180, le=180)
    address: str = Field(min_length=1, max_length=255)
    initial_offer: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    category: str | None = Field(default=None, min_length=1, max_length=50)

    model_config = ConfigDict(extra="forbid")


class TaskPublic(BaseModel):
    task_id: UUID
    title: str
    description: str | None
    location_lat: Decimal
    location_lng: Decimal
    address: str
    initial_offer: Decimal
    accepted_price: Decimal | None = None
    category: str | None = None
    status: str
    creator_id: UUID
    runner_id: UUID | None = None
    proof_image_url: str | None = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TaskResponse(BaseModel):
    task: TaskPublic
