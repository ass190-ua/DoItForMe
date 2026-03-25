from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreateRequest(BaseModel):
    task_id: UUID
    reviewee_id: UUID
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=1000)

    model_config = ConfigDict(extra="forbid")


class ReviewCreate(BaseModel):
    reviewee_id: UUID
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=1000)

    model_config = ConfigDict(extra="forbid")


class ReviewPublic(BaseModel):
    id: UUID
    task_id: UUID
    reviewer_id: UUID
    reviewee_id: UUID
    rating: int
    comment: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewResponse(BaseModel):
    review: ReviewPublic
