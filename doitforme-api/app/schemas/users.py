from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SelfProfile(BaseModel):
    user_id: UUID
    email: str
    name: str
    role: str
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    balance: Decimal
    rating: Decimal
    completed_tasks_count: int
    rating_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SelfProfileResponse(BaseModel):
    profile: SelfProfile


class PublicProfile(BaseModel):
    user_id: UUID
    name: str
    role: str
    rating: Decimal
    completed_tasks_count: int
    rating_count: int

    model_config = ConfigDict(from_attributes=True)


class PublicProfileResponse(BaseModel):
    profile: PublicProfile


class SelfProfileUpdateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)

    model_config = ConfigDict(extra="forbid")
