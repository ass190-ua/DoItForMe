from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProposalCreateRequest(BaseModel):
    proposed_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    message: str | None = Field(default=None, max_length=1000)

    model_config = ConfigDict(extra="forbid")


class ProposalPublic(BaseModel):
    id: UUID
    task_id: UUID
    runner_id: UUID
    proposed_price: Decimal
    message: str | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProposalResponse(BaseModel):
    proposal: ProposalPublic
